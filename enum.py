#!/usr/bin/env python
import libtcodpy as tcod

def rand_body_part(entity):
    if not entity.body:
        return ''
    return entity.body[tcod.random_get_int(0,0,len(entity.body))-1]

class GameS:
    STARTUP = 0
    IDLE = 1
    NEW_TURN = 2
    VICTORY = 3
    DEFEAT = 4
    
class dir:
    UP = [0, -1]
    DOWN = [0, +1]
    RIGHT = [1, 0]
    LEFT = [-1, 0]

class mat:
    STONE = 'stone'
    FLESH = 'flesh'
    GAS = 'gaseous'
    METAL = 'metallic'
    JELLY = 'gelatinous'
    VEGETAL = 'vegetal'
    WOOD = 'wooden'
    
class body: #dicts can contain values... maybe used for damages or colors, or..?
    human = ['head', 'eyes', 'ears', 'mouth', 'torso', 'right hand', 'left hand', 'feet']
    book = ['pages', 'cover']