#!/usr/bin/env python
import libtcodpy as tcod
import core
import enum
import game
import map
import gui
import ai

''' things that hurt and things that can break :'( '''

class Destructible(core.Destructible):
    pass
class Attacker(core.Attacker):
    pass

class DestructibleMonster(Destructible):
    pass

class DestructiblePlayer(Destructible):
    def die(self):
        self.owner.char = "%"
        self.owner.color = tcod.dark_red
        self.owner.blocks = False
        self.owner.ai = None
        game.game_state = enum.GameS.DEFEAT
        
