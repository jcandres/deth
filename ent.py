#!/usr/bin/env python
import libtcodpy as tcod
import core
import enum
import game
import map
import gui
import ai
import item
import hit

''' living actors, entities '''

class Entity(core.Object):
    pass

######################### LIVING STUFF ###################
class Player(Entity):
    def __init__(self, x, y):
        _ai = ai.AiPlayer()
        _at = hit.Attacker(5)
        _de = hit.DestructiblePlayer(15, 1)
        _co = item.Container(15)
        self.name = 'you'
        self.char = '@'
        self.speed = 10
        
        Entity.__init__(self, x, y, name=self.name, char=self.char, speed=self.speed,
                        attacker=_at, ai=_ai, destructible=_de, container=_co)
        self.sense_objects = True #outside fov
        self.sense_entities = True #outside fov
        self.sense_map = False #this means you can't see smoke!
        self.blind = False #can see characters of the things
        
    def update(self):#override this
        pass 
    def take_turn(self): #for this!
        if self.ai:
            self.ai.update()

class Zombie(Entity):
    def __init__(self, x, y):
        _ai = ai.AiZombie()
        _de = hit.DestructibleMonster(10, 1, corpse_name="zombie body")
        _at = hit.Attacker(2)
        self.speed = tcod.random_get_int(0, 4, 6)
        bod = enum.body.human
        Entity.__init__(self, x, y, name='zombie', char='Z', speed=self.speed,
                        attacker=_at, ai=_ai, destructible=_de, body=bod)
        
######################### GAME OBJECTS ###################
# tools #
class Shovel(Entity):
    def __init__(self, x, y):
        _pi = item.Digger(10)
        Entity.__init__(self, x, y, name='shovel', char='/', blocks=False, pickable=_pi)
class Slingshot(Entity):
    def __init__(self, x, y):
        _pi = item.SlingshotThrow(3, 5)
        Entity.__init__(self, x, y, name='slingshot', char='/', blocks=False, pickable=_pi)
        
# equip #
class DaggerSmall(Entity):
    def __init__(self, x, y):
        _eq = item.Equip('right hand', po=1)
        Entity.__init__(self, x, y, name='tiny dagger', char='/', blocks=False, equipment=_eq)
class HelmetCopper(Entity):
    def __init__(self, x, y):
        _eq = item.Equip('head', de=2)
        Entity.__init__(self, x, y, name='copper helmet', char='[', blocks=False, equipment=_eq)
class ShieldWood(Entity):
    def __init__(self, x, y):
        _eq = item.Equip('left hand', de=1, po=1)
        Entity.__init__(self, x, y, name='small shield', material=enum.mat.WOOD, char='[',
                        blocks=False, equipment=_eq)
# consumables #
class MossRed(Entity):
    def __init__(self, x, y):
        _pi = item.Healer(10)
        Entity.__init__(self, x, y, name='red moss', char='+', blocks=False, pickable=_pi)
class GrenadeSmoke(Entity):
    def __init__(self, x, y):
        _pi = item.SmokeThrow(5, 1, 5)
        Entity.__init__(self, x, y, name='smoke grenade', char='!', blocks=False, pickable=_pi)
class Grenade(Entity):
    def __init__(self, x, y):
        _pi = item.ExplosiveThrow(3,10,5)
        Entity.__init__(self, x, y, name='grenade', char='!', blocks=False, pickable=_pi)
        
# random junk and stuff #
class Smoke(Entity):
    def __init__(self, x, y, life, was_visible=True):
        self.life = life
        self.was_visible = was_visible
        Entity.__init__(self, x, y, name='smoke', char=chr(tcod.CHAR_BLOCK2), blocks=False)
        if not map.is_wall(self.x, self.y):
            map.fov_set(self.x, self.y, visible=False, blocked=map.is_wall(self.x, self.y))
    def update(self):
        Entity.update(self)
        self.life -= 1
        if self.life <= 0:
            self.remove = True
            map.fov_set(self.x, self.y, visible=self.was_visible, blocked=False)
            #map.fov_init()

class Projectile(Entity):
    def __init__(self, x, y, power, wearer=None, name=None, self_remove=False):
        _at = hit.Attacker(power)
        nam = 'projectile'
        if name: nam = name
        Entity.__init__(self, x, y, name=nam, char='*', blocks=False, attacker=_at)
        t = self.attacker.attack_tile(x, y)
        if t:
            game.log('the', self.name, 'hits the',t.init_name+'!')
            if t.destructible.is_dead() and wearer:
                game.log(wearer.name, 'killed the', t.init_name+'!')
        self.attacker = None
        self.remove = self_remove