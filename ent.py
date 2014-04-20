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

class Player(Entity):
    def __init__(self, x, y):
        _ai = ai.AiPlayer()
        _at = hit.Attacker(5)
        _de = hit.DestructiblePlayer(15, 1)
        _co = item.Container(5)
        self.name = 'you'
        self.char = '@'
        self.speed = 10
        
        Entity.__init__(self, x, y, name=self.name, char=self.char, speed=self.speed,
                        attacker=_at, ai=_ai, destructible=_de, container=_co)

class Zombie(Entity):
    def __init__(self, x, y):
        _ai = ai.AiZombie()
        _de = hit.DestructibleMonster(10, 1, corpse_name="zombie body")
        _at = hit.Attacker(2)
        self.name = 'zombie'
        self.char = 'Z'
        self.speed = tcod.random_get_int(0, 4, 6)
        
        Entity.__init__(self, x, y, name=self.name, char=self.char, speed=self.speed,
                        attacker=_at, ai=_ai, destructible=_de)