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
        line =' %s - %s'  % (chr(ord('a')+i), inventory[i].name)
        tcod.console_print(con, xx+2, yy+1+i, line)
    tcod.console_flush()
    
def draw_equipment(con, inventory, title):
    INVENTORY_HEIGHT = len(inventory)+2
    xx = game.GAME_WIDTH/2 - INVENTORY_WIDTH/2
    yy = game.GAME_HEIGHT/2 - INVENTORY_HEIGHT/2
    tcod.console_set_default_foreground(con, COL_A)
    tcod.console_print_frame(con, xx, yy, INVENTORY_WIDTH, INVENTORY_HEIGHT, fmt=title)
    for i in range(len(inventory)):
        tcod.console_set_default_foreground(con, COL_B)
        line =' %s - %s'  % (chr(ord('a')+i), inventory[i].name)
        if inventory[i].equipment:
            if inventory[i].equipment.is_equipped:
                tcod.console_set_default_foreground(con, tcod.lightest_gray)
                line += ' ['+inventory[i].equipment.slot+']'
            else:
                tcod.console_set_default_foreground(con, COL_A)
        tcod.console_print(con, xx+2, yy+1+i, line)
    tcod.console_flush()

  
def draw_directions(con, target):
    game.draw_all()
    tcod.console_set_default_foreground(con, COL_A)
    tcod.console_put_char(con, target.x-1, target.y, tcod.CHAR_ARROW_W)
    tcod.console_put_char(con, target.x+1, target.y, tcod.CHAR_ARROW_E)
    tcod.console_put_char(con, target.x, target.y-1, tcod.CHAR_ARROW_N)
    tcod.console_put_char(con, target.x, target.y+1, tcod.CHAR_ARROW_S)
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
        ' | DEF: %d' % game.player.defense,
        ' | POW: %d' % game.player.power,
        ' | SPD: %d / %d' % (game.player.action_points ,game.player.speed),
        ' | INV: %d' % len(game.player.container.inventory),
        ' | '
        )
    line += str(game.player.get_all_equipped())
    tcod.console_print_ex(con, 1, game.GAME_HEIGHT-2, tcod.BKGND_ADD, tcod.LEFT, line)    
    return True

#extracts n lines and prints on screen
def draw_log(con, n_lines):
    tcod.console_set_default_foreground(con, COL_A)
    log_y = game.GAME_HEIGHT - n_lines - 1
    while len(game.game_log) < n_lines: #dummy lines at game start
        game.game_log.append('\b')

    for i in range(n_lines):
        c = (i-(i*30)-50)
        tcod.console_set_default_foreground(con, tcod.Color(c, c, c))
        tcod.console_print(con, 1, log_y - i, game.game_log[len(game.game_log)-1-i])

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
    tcod.console_set_default_foreground(con, COL_A)
    img = tcod.image_load('small.png')
    tcod.image_set_key_color(img, tcod.red)
    tcod.image_blit(img, 0, 45, 30,  tcod.BKGND_LIGHTEN, .5, .25, 0)
    #tcod.image_blit_2x(img, 0, 0, 0)
    
    xx=-20
    yy=15
    
    options=(
             """
             GAME TITLE """+chr(tcod.CHAR_BLOCK2)+chr(tcod.CHAR_BLOCK1)+chr(tcod.CHAR_BLOCK1)+"""
             |
             |
             \t-- (n)ew game
             |
             \t--\t-- (c)ontinue
             |  |
             |  \t-- (d)elete
             |
             \t-- (esc)cape
             """)
    tcod.console_print_ex(con, game.GAME_WIDTH/4+xx, game.GAME_HEIGHT/3+yy,
                              tcod.BKGND_LIGHTEN, tcod.LEFT,options)
    tcod.console_flush()
    tcod.console_clear(con)
    
        
