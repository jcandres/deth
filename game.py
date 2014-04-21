#!/usr/bin/env python
import libtcodpy as tcod
import sys, os
import textwrap, shelve
import enum
import map
import gui
import ent, item, ai, hit


GAME_WIDTH = 80
GAME_HEIGHT = 60
NORMAL_SPEED = 10


def log(*args):
    global turn_log
    turn_log += concatenate(*args)+'. '
    #line = concatenate(*args)
    #messages = textwrap.wrap(line, GAME_WIDTH-2) #divide in several lines if needed
    #for l in messages:
    #    game_log.append(l)
def log_turn():
    global turn_log
    if len(turn_log) <= 1:
        return False
    
    messages = textwrap.wrap(turn_log, GAME_WIDTH-2) #divide in several lines if needed
    for l in messages:
        game_log.append(l)
    print turn_log
    turn_log = ''
   
def concatenate(*args):
    ls = []
    for arg in args:
        ls.append(str(arg))
    line = ' '.join(ls)
    return line

def draw_all():
        tcod.console_clear(0)
        map.draw(0)
        for object in actors:
            object.draw(0)
        for object in actors:
            if object.blocks:
                object.draw(0)
        #gui.draw_log(0, 5)
        gui.draw_hud(0)
        gui.draw_visible(0)
    
class Game:
    def init(self): #init tcod & such
        global turn_log
        tcod.console_init_root(GAME_WIDTH,GAME_HEIGHT,'deth')
        tcod.console_set_default_background(0, tcod.darkest_gray)
        tcod.sys_set_fps(15)
        
        turn_log = '\b'
        
        self.menu()
        
    def menu(self): #new gam or load
        print 'has save game:', os.path.isfile('save')
        while not tcod.console_is_window_closed():
            gui.draw_main_menu(0)
            key = tcod.console_check_for_keypress(True)
            if key.c == ord('n'):
                self.new_game()
                break
            if key.c == ord('c'):
                try: 
                    self.load_game()
                    break
                except:
                    print 'no saved gam'
            elif key.c == ord('d'):
                os.remove('save')
                print 'deleted save game'
            elif key.vk == tcod.KEY_ESCAPE:
                print 'quit...'
                sys.exit(0)
                
    def save_game(self):
        global game_state, actors, game_log, player, stairs_up, stairs_down
        file = shelve.open('save', 'n')
        file['game_state'] = game_state
        file['actors'] = actors
        file['player_index'] = actors.index(player)
        file['stairs_u_index'] = actors.index(stairs_up)
        file['stairs_d_index'] = actors.index(stairs_down)
        file['game_log'] = game_log
        file['map'] = map.map
        file.close()
        
    def load_game(self):
        global game_state, actors, game_log, player, stairs_up, stairs_down
        file = shelve.open('save', 'r')
        game_state = file['game_state']
        actors = file['actors']
        player = actors[file['player_index']]
        stairs_up = actors[file['stairs_u_index']]
        stairs_down = actors[file['stairs_d_index']]
        game_log = file['game_log']
        map.map = file['map']
        file.close()
        map.fov_init()
        map.fov_recompute(player.x, player.y)
        
    def new_game(self):
        global game_state, actors, game_log, player, stairs_up, stairs_down
        game_state = enum.GameS.STARTUP
        actors = []
        game_log = []
        
        player = ent.Player(0,0)
        stairs_up = ent.Entity(1,2,"<", "upward staircase", blocks=False)
        stairs_down = ent.Entity(1,2,">", "downward staircase", blocks=False)
        
        actors.append(stairs_up)
        actors.append(stairs_down)
        actors.append(player)
        
        map.make_map()
        map.fov_recompute(player.x, player.y)
        
        game_state = enum.GameS.IDLE
        tcod.console_flush()

            
    def loop(self):
        global game_state, key
        while not tcod.console_is_window_closed():
            if game_state == enum.GameS.NEW_TURN:
                game_state = enum.GameS.IDLE
            
            key = tcod.console_check_for_keypress(True)
            player.take_turn() #different actions will trigger the new turn
            
            ### turn loop
            if game_state == enum.GameS.NEW_TURN:
                player.action_points -= NORMAL_SPEED #player pays its movement
                while player.action_points < NORMAL_SPEED: #player can't move, party time
                    for object in actors:
                        object.action_points += object.speed
                        while object.action_points >= NORMAL_SPEED:
                            object.update()
                            object.action_points -= NORMAL_SPEED
                    player.action_points += player.speed
                
                for object in actors: #remove unnecesary entities safely
                    if object.remove:
                        actors.remove(object)
                    
                if game_state == enum.GameS.DEFEAT:
                    if os.path.isfile('save'):
                        os.remove('save')
                map.fov_recompute(player.x, player.y)
                log_turn()
            ### end of turn loop
            
            draw_all()
            tcod.console_flush()
            if key.vk == tcod.KEY_ESCAPE:
                self.end()
            if key.vk == tcod.KEY_F5: #debug-quit
                break
        
    def end(self):
        global game_state
        if game_state is not enum.GameS.DEFEAT:
            self.save_game()
            print 'end-func: saved!'
        self.menu()