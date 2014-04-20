#!/usr/bin/env python
import libtcodpy as tcod
import core
import enum
import game
import map
import gui
import ent

''' objects, items, scenery '''

class Pickable(core.Pickable):
    pass
class Container(core.Container):
    pass
class Item(core.Object):
    pass

######################### GAME OBJECTS ###################
class PotionHeal(Item):
    def __init__(self, x, y):
        _pi = Healer(10)
        self.name = 'heal potion'
        self.char = '!'
        self.blocks = False
        Item.__init__(self, x, y, name=self.name, char=self.char, blocks=self.blocks, pickable=_pi)
'''
class GrenadeSmoke(Item):
    def __init__(self, x, y):
        _pi = Healer(10)
        self.name = 'smoke grenade'
        self.char = 'o'
        self.blocks = False
        Item.__init__(self, x, y, name=self.name, char=self.char, blocks=self.blocks, pickable=_pi)
'''

######################### COMPONENTS #####################
class Healer(Pickable):
    def __init__(self, amount):
        Pickable.__init__(self) 
        self.amount = amount
    def use(self, wearer, target):
        if wearer and wearer.container:
            wearer.container.inventory.remove(self.owner)
        a = target.destructible.heal(self.amount)
        if a > 0:
            game.log(target.name, 'heals by', a, 'hp')
        else:
            game.log('but it has no visible effect!')
            

            
        
