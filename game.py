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
    #turn_log = concatenate(*args)+'. ' + turn_log
    
def log_turn():
    global turn_log
    if len(turn_log) <= 1:
        return False
    messages = textwrap.wrap(turn_log, GAME_WIDTH-2) #divide in several lines if needed
    for l in messages:
        game_log.append(l)
    turn_log = ''
   
def concatenate(*args):
    ls = []
    for arg in args:
        #ls.append(str(arg))
        ls.append(str(arg))
    line = ' '.join(ls)
    return line

def draw_all():
        tcod.console_clear(0)
        map.draw(0, player.sense_map)
        for object in actors:
            if not object.blocks:
                object.draw(0, skip_fov=player.sense_objects,
                        no_char=(player.blind and not player.sense_objects))
        for object in actors:
            if object.blocks:
                object.draw(0, skip_fov=player.sense_entities,
                            no_char=(player.blind and not player.sense_entities))
        gui.draw_log(0, 5)
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
        print 'menu: has save game:', os.path.isfile('save')
        while not tcod.console_is_window_closed():
            gui.draw_main_menu(0, os.path.isfile('save'))
            key = tcod.console_check_for_keypress(True)
            if key.c == ord('n'):
                self.new_game()
                break
            if key.c == ord('c'):
                try: 
                    self.load_game()
                    break
                except:
                    print 'menu: no saved gam'
            elif key.c == ord('D'):
                os.remove('save')
                self.clean_stored_maps()
                print 'menu: deleted save game'
            elif key.vk == tcod.KEY_ESCAPE:
                print 'menu: quit...'
                sys.exit(0)
                
            
    def loop(self):
        global game_state, key, actors
        while not tcod.console_is_window_closed():
            if game_state == enum.GameS.NEW_TURN:
                game_state = enum.GameS.IDLE
            
            key = tcod.console_check_for_keypress(True)
            player.take_turn() #different actions will trigger the new turn
            
            if game_state == enum.GameS.STAIRS_DOWN:
                self.change_floor(+1)
            elif game_state == enum.GameS.STAIRS_UP:
                self.change_floor(-1)
                    
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
                
                #refresh actors removing dead things
                ol = [object for object in actors if not object.remove]
                actors = ol
                    
                map.fov_recompute(player.x, player.y)
                log_turn()
            if game_state == enum.GameS.DEFEAT:
                if os.path.isfile('save'):
                    os.remove('save')
                self.clean_stored_maps()
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
    
    def change_floor(self, amount):
        global game_state, level, actors, game_log, player, stairs_up, stairs_down
        self.store_map()
        
        level = level + amount
        
        actors = []
        actors.append(player)
        actors.append(stairs_up)
        actors.append(stairs_down)
        
        if not os.path.isfile('l'+str(level)+'.s'): #if new floor is new, make it
            map.make_map()
        else:
            self.restore_map() #else load it
        
        if amount > 0: #down
            player.x = stairs_up.x
            player.y = stairs_up.y
        else:
            player.x = stairs_down.x
            player.y = stairs_down.y
        log("you are now at floor", level)
        log_turn()
        map.fov_recompute(player.x, player.y)
        game_state = enum.GameS.IDLE
        tcod.console_flush()
    
    def save_game(self, file_name='save'):
        global game_state, actors, game_log, player, stairs_up, stairs_down, level
        file = shelve.open(file_name, 'n')
        file['game_state'] = game_state
        file['actors'] = actors
        file['level'] = level
        file['player_index'] = actors.index(player)
        file['stairs_u_index'] = actors.index(stairs_up)
        file['stairs_d_index'] = actors.index(stairs_down)
        file['game_log'] = game_log
        file['map'] = map.map
        file.close()
  
    def load_game(self, file_name='save'):
        global game_state, actors, game_log, player, stairs_up, stairs_down, level
        file = shelve.open(file_name, 'r')
        game_state = file['game_state']
        level = file['level']
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
        global game_state, actors, game_log, player, stairs_up, stairs_down, level
        self.clean_stored_maps()
        game_state = enum.GameS.STARTUP
        actors = []
        game_log = []
        level = 1
        
        player = ent.Player(0,0)
        stairs_up = ent.Entity(1,2,"<", "upward staircase", blocks=False)
        stairs_down = ent.Entity(1,2,">", "downward staircase", blocks=False)
        
        actors.append(stairs_up)
        actors.append(stairs_down)
        actors.append(player)
        
        map.make_map()
        map.fov_recompute(player.x, player.y)
        
        stairs_up.x, stairs_up.y = (-1, -1)
        game_state = enum.GameS.IDLE
        tcod.console_flush()
    
    def store_map(self):
        global level
        self.save_game('l'+str(level)+'.s')
    def restore_map(self):
        global level, actors, player
        o_player = player
        self.load_game('l'+str(level)+'.s')
        actors.remove(player)
        player = o_player
        actors.append(player)
    def clean_stored_maps(self):
        for i in range(50):
            if os.path.isfile('l'+str(i)+'.s'):
                os.remove('l'+str(i)+'.s')
        







