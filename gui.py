#!/usr/bin/env python

import libtcodpy as tcod
import game
import enum
import map


COL_A = tcod.lighter_gray
COL_B = tcod.gray
INVENTORY_HEIGHT = 28
INVENTORY_WIDTH = 40

def draw_inventory(con, inventory, title):
    INVENTORY_HEIGHT = len(inventory)+2
    xx = game.GAME_WIDTH/2 - INVENTORY_WIDTH/2
    yy = game.GAME_HEIGHT/2 - INVENTORY_HEIGHT/2
    tcod.console_set_default_foreground(con, COL_A)
    tcod.console_print_frame(con, xx, yy, INVENTORY_WIDTH, INVENTORY_HEIGHT, fmt=title)
    for i in range(len(inventory)):
        tcod.console_print(con, xx+2, yy+1+i,' %s - %s '  % (chr(ord('a')+i), inventory[i].name))
    tcod.console_flush()
    
#draws player stats
def draw_hud(con):
    tcod.console_set_default_foreground(con, COL_A)
    
    if game.game_state == enum.GameS.DEFEAT:
        line = " * u ded * "
        tcod.console_set_default_foreground(con, tcod.crimson)
        tcod.console_print_ex(con, game.GAME_WIDTH/2, game.GAME_HEIGHT/2,
                              tcod.BKGND_ADD, tcod.CENTER,line)
        return True
    
    if not game.player:
        return False
    
    line = game.concatenate(
        #'| HP: %d / %d' % (game.player.destructible.hp, game.player.destructible.max_hp),
        ' | ' + chr(219) * game.player.destructible.hp + chr(224) * (game.player.destructible.max_hp-game.player.destructible.hp),
        ' | DEF: %d' % game.player.destructible.defense,
        ' | POW: %d' % game.player.attacker.power,
        ' | SPD: %d / %d' % (game.player.action_points ,game.player.speed),
        ' | INV: %d' % len(game.player.container.inventory),
        ' | '
        )
        
    tcod.console_print_ex(con, 1, game.GAME_HEIGHT-2, tcod.BKGND_ADD, tcod.LEFT, line)
    
    return True

#extracts n lines and prints on screen
def draw_log(con, n_lines):
    tcod.console_set_default_foreground(con, COL_A)
    log_y = game.GAME_HEIGHT - n_lines - 5
    line = []
    while len(game.game_log) < n_lines: #dummy lines at game start
        game.log('\b')
        
    for i in range(n_lines):
        line.append(game.game_log[len(game.game_log)-i-1])
    
    for i in range(len(line)):
        tcod.console_print(con, 1, log_y + i, line[i])
 
#draws list of visible entities       
def draw_visible(con):
    tcod.console_set_default_foreground(con, COL_B)
    ls = []
    for object in game.actors:
        if map.is_fov(object.x, object.y):
            ls.append(object.char)  
    line = ', '.join(ls)
    tcod.console_print(con, 1, game.GAME_HEIGHT - 4, chr(254)+' '+line)
    
def draw_main_menu(con):
    img = tcod.image_load('small.png')
    tcod.image_blit_2x(img, 0, 0, 0)
        
    line = ('-'*16+"\n == GAM MENU == \n"+'-'*16+
             "\n\n\n n - new game \n c - continue \n esc - exit \n(d)elete")
    tcod.console_set_default_foreground(con, COL_A)
    tcod.console_print_ex(con, game.GAME_WIDTH/2, game.GAME_HEIGHT/3,
                              tcod.BKGND_ADD, tcod.CENTER,line)
    tcod.console_flush()
    tcod.console_clear(con)
    
        