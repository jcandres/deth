#!/usr/bin/env python

import libtcodpy as tcod
import math
import game
import ent, item, hit, ai

class Rect:
    def __init__(self, x, y, w, h, number=None):
        self.w = w
        self.h = h
        self.x1 = x
        self.y1 = y
        self.x2 = x+w
        self.y2 = y+h
        self.number = number
        self.center_x = int((self.x1 + self.x2) / 2)
        self.center_y = int((self.y1 + self.y2) / 2)

class Tile:
    def __init__(self, blocked, block_sight=None):
        self.explored = False
        self.diggable = True
        self.blocked = blocked
        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight
        
## MAP ##
MAP_WIDTH = 80
MAP_HEIGHT = 50
MAX_LEAF_SIZE = 16
MIN_LEAF_SIZE = 8
MAX_ROOM_SIZE = 12
MIN_ROOM_SIZE = 5

MAX_ROOM_DOORS = 2  
MAX_ROOM_MONSTERS = 3
MAX_ROOM_ITEMS = 3

LIGHT_RADIUS = 7

map = [[Tile(True)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]
fov_map = tcod.map_new(MAP_WIDTH, MAP_HEIGHT)
leafs = []
rooms = []
doors = []


##population
def populate():
    #redefine generation values
    MAX_ROOM_MONSTERS = from_dungeon_level([[2, 0], [3, 3], [7, 6]])
    MAX_ROOM_ITEMS = from_dungeon_level([[3, 0], [2, 3], [1, 6]])
    
    for object in rooms:
        r = object
        num_monsters = tcod.random_get_int(0,0,MAX_ROOM_MONSTERS)
        num_items = tcod.random_get_int(0,0,MAX_ROOM_ITEMS)
        for i in range(num_monsters):
            x = tcod.random_get_int(0, r.x1, r.x2-1)
            y = tcod.random_get_int(0, r.y1, r.y2-1)
            make_monster(x, y)
        for i in range(num_items):
            x = tcod.random_get_int(0, r.x1, r.x2-1)
            y = tcod.random_get_int(0, r.y1, r.y2-1)
            make_item(x, y)
            
        #Special cases
        if r.number == 0:
            game.player.x = r.center_x
            game.player.y = r.center_y
            game.stairs_up.x = r.center_x
            game.stairs_up.y = r.center_y
        if r.number == len(rooms)-1:
            game.stairs_down.x = r.center_x
            game.stairs_down.y = r.center_y

def make_monster(x, y):
    chances = {}
    #monster_chances[ent.Zombie] = 5 #=always
    chances[ent.Zombie] = from_dungeon_level([[15, 0], [30, 5], [60, 7]])
    
    choice = random_choice(chances)
    if choice:
        m=choice(x, y)
        game.actors.append(m)
def make_item(x, y):
    chances = {}
    chances[ent.MossRed] = from_dungeon_level([[60, 0], [30, 5], [10, 7], [5, 15]])
    chances[ent.DaggerSmall] = from_dungeon_level([[30, 0], [15, 5], [5, 10]])
    chances[ent.HelmetCopper] = from_dungeon_level([[30, 2], [15, 7], [5, 15]])
    chances[ent.ShieldWood] = from_dungeon_level([[30, 0], [10, 5], [5, 10]])
    chances[ent.Shovel] = from_dungeon_level([[5, 10]])
    chances[ent.Slingshot] = from_dungeon_level([[3, 10]])
    chances[ent.GrenadeSmoke] = from_dungeon_level([[10, 7], [5, 15]])
    chances[ent.Grenade] = from_dungeon_level([[10, 10], [5, 15]])
    
    choice = random_choice(chances)
    if choice:
        m=choice(x, y)
        game.actors.append(m)            

## generation ##
def make_map():
    global map, leafs, rooms, doors, fov_map
    map = [[Tile(True)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]
    leafs = []
    rooms = []
    doors = []
    fov_map = tcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    bsp = tcod.bsp_new_with_size(2, 2, MAP_WIDTH-3, MAP_HEIGHT-3)
    tcod.bsp_split_recursive(bsp, 0, 4 , MIN_LEAF_SIZE, MAX_LEAF_SIZE, 1.5, 1.5)
    tcod.bsp_traverse_inverted_level_order(bsp, bsp_callback)
    
    n=0 #create numerated rooms from leafs
    for object in leafs:
        make_room(object, n)
        n += 1 
    for object in rooms: #dig rooms & corridors
        dig(object)
        make_doors(object, object.number)
    for object in doors:
        prev = doors[object.number-1]
        dig_h_tunnel(prev.center_x, object.center_x, prev.center_y)
        dig_v_tunnel(prev.center_y, object.center_y, object.center_x)
    
    for x in range(0, MAP_WIDTH):
        set_diggable(x,0,False)
        set_diggable(x,MAP_HEIGHT-1,False)
    for y in range(0, MAP_HEIGHT):
        set_diggable(0,y,False)
        set_diggable(MAP_WIDTH-1,y,False)
    
    populate()
    
    fov_init()

def make_room(leaf, n=0):
    w = tcod.random_get_int(0, MIN_ROOM_SIZE, leaf.w)
    h = tcod.random_get_int(0, MIN_ROOM_SIZE, leaf.h)
    x = tcod.random_get_int(0, leaf.x1, leaf.x2-w)
    y = tcod.random_get_int(0, leaf.y1, leaf.y2-h)
    r = Rect(x, y, w-1, h-1, n)
    rooms.append(r)
def make_doors(room, number):
    n = tcod.random_get_int(0, 0, MAX_ROOM_DOORS-1) + 1
    for i in range(n):
        x = tcod.random_get_int(0, room.x1+1, room.x2-1)
        y = tcod.random_get_int(0, room.y1+1, room.y2-1)
        s = tcod.random_get_int(0,0,3) #side of the room
        if s == 0:
            x = room.x1
        elif s ==1 :
            y = room.y1
        elif s ==2 :
            x = room.x2-1
        elif s ==3 :
            y = room.y2-1
        door = Rect(x,y,1,1,number)
        doors.append(door)
        
### DRAW
def draw(con, skip_fov=False):
    #global map
    tcod.console_set_default_foreground(con, tcod.gray)
    
    if skip_fov:
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                wall = map[x][y].block_sight
                if wall:
                    tcod.console_put_char(con, x, y, "#")
                else:
                    tcod.console_put_char(con, x, y, ".")
        return True
    
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            wall = map[x][y].block_sight
            if is_fov(x, y):
                map[x][y].explored = True
                if wall:
                    tcod.console_put_char(con, x, y, "#")
                else:
                    tcod.console_put_char(con, x, y, ".")
            else: #outside FOV
                if map[x][y].explored:
                    if wall:
                        tcod.console_put_char(con, x, y, ".")
                    else:
                        tcod.console_put_char(con, x, y, " ")
    for object in doors:
        #tcod.console_put_char(0, object.center_x, object.center_y, object.number+65)
        pass
   

### DIG FUNCTIONS 
def dig(room):
    for x in range(room.x1, room.x2):
        for y in range(room.y1, room.y2):
            set_wall(x, y, False, False)
def dig_h_tunnel(x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2)+1):
        set_wall(x, y, False, False)
def dig_v_tunnel(y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2)+1):
        set_wall(x, y, False, False)
            
def set_wall(x, y, solid=True, visible=True):
    if solid is not None:
        map[x][y].blocked = solid
    if visible is not None:
        map[x][y].block_sight = visible

## utils and shit ##
def is_wall(x,y):
    if not is_in_bounds(x, y):
        return False
    return map[x][y].blocked

def is_diggable(x, y):
    return map[x][y].diggable

def set_diggable(x, y, can_dig=True):
    map[x][y].diggable = can_dig

def is_blocked(x, y):
    if is_wall(x, y):
        return True
    for object in game.actors:
        if object.x==x and object.y==y and object.blocks:
            return True
    return False

def is_in_bounds(x, y):
    return x >= 0 and y >= 0 and x < MAP_WIDTH and y < MAP_HEIGHT

def get_actor(x, y):
    for object in game.actors:
        if object.x==x and object.y==y:
            return object
    return None
def get_actor_alive(x, y):
    for object in game.actors:
        if object.x==x and object.y==y and object.destructible and not object.destructible.is_dead():
            return object
    return None
def get_actor_pickable(x, y):
    for object in game.actors:
        if object.x==x and object.y==y and object.pickable:
            return object
    return None

def get_distance(ent_a, ent_b):
    dx = ent_a.x - ent_b.x
    dy = ent_a.y - ent_b.y
    return math.sqrt(dx ** 2 + dy ** 2)
def get_distance_coord(x1, y1, x2, y2):
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx ** 2 + dy ** 2)

def fov_init():
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            fov_set(x, y, not map[x][y].block_sight, map[x][y].blocked)
def fov_set(x, y, visible, blocked):
    tcod.map_set_properties(fov_map, x, y, visible, not blocked)
def fov_recompute(x, y):
    tcod.map_compute_fov(fov_map, x, y, LIGHT_RADIUS, True, 0)
def is_fov(x, y):
    return tcod.map_is_in_fov(fov_map, x, y)
        
def bsp_callback(node, data):
    if tcod.bsp_is_leaf(node):
        l = Rect(node.x, node.y, node.w, node.h)
        leafs.append(l)
    return True #importent - C wizardy :0
    
def random_choice_index(chances):  #choose one option from list of chances, returning its index
    #the dice will land on some number between 1 and the sum of the chances
    dice = tcod.random_get_int(0, 1, sum(chances))
    #go through all chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w
        #see if the dice landed in the part that corresponds to this choice
        if dice <= running_sum:
            return choice
        choice += 1
def random_choice(chances_dict):
    #choose one option from dictionary of chances, returning its key
    chances = chances_dict.values()
    strings = chances_dict.keys()
    return strings[random_choice_index(chances)]
def from_dungeon_level(table):
    '''from_dungeon_level([[level, value], [level, value]]) etc
    returns a value that depends on level. the table specifies what value occurs after each level, default is 0.
    '''
    for (value, level) in reversed(table): ##asumes that table is in ascendent order...
        if game.level >= level:
            return value
    return 0
        
        
        
        
        
        