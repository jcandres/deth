#!/usr/bin/env python

import libtcodpy as tcod
import enum
import game
import map
import gui


class Object:
    def __init__(self, x, y, char="?", name="something",color=tcod.lighter_gray, blocks=True,
                 speed=10, destructible=None, attacker=None, ai=None, pickable=None, container=None):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks
                
        self.speed = speed
        self.action_points = tcod.random_get_int(0,0,speed)
        self.remove = False
        
        self.destructible = destructible
        self.ai = ai
        self.attacker = attacker
        self.pickable = pickable
        self.container = container
        self.init_components()
    
    def init_components(self):
        if self.destructible:
            self.destructible.owner = self
        if self.ai:
            self.ai.owner = self
        if self.attacker:
            self.attacker.owner = self
        if self.pickable:
            self.pickable.owner = self
        if self.container:
            self.container.owner = self
    
    def update(self):
        if self.ai:
            self.ai.update()
    
    def move(self, dx, dy):
        if map.is_wall(self.x+dx, self.y+dy) or map.is_blocked(self.x+dx, self.y+dy):
            return False
        else:
            self.x += dx
            self.y += dy
            return True
    
    def draw(self, con):
        if map.is_fov(self.x, self.y):
            tcod.console_set_default_foreground(con, self.color)
            tcod.console_put_char(con, self.x, self.y, self.char, tcod.BKGND_NONE)
        
    def send_back(self):
        game.actors.remove(self)
        game.actors.insert(0, self)
    def send_front(self):
        game.actors.remove(self)
        game.actors.append(self)
    
    
###### CONTAINER
class Container:
    def __init__(self, size):
        self.size = size
        self.inventory = []
    def add(self, item):
        if len(self.inventory) >= self.size:
            return False
        self.inventory.append(item)
        return True
    
###### PICKABLE
class Pickable:
    def __init__(self, use_function=None):
        self.use_function = use_function
        self.wearer = None
    def pick(self, wearer):
        if wearer.container and wearer.container.add(self.owner):
            game.actors.remove(self.owner)
            return True
        return False
    def use(self):
        pass
        


        
###### DESTRUCTIBLE
class Destructible:
    def __init__(self, hp, defense, corpse_name=None ):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.corpse_name = corpse_name
    def take_damage(self, amount):
        amount -= self.defense
        if amount > 0:
            self.hp -= amount
            if self.is_dead():
                self.die()
        else:
            return max(amount, 0)
    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            amount -= self.hp-self.max_hp
            self.hp = self.max_hp
        return amount
    def die(self):
        self.owner.char = "%"
        if self.corpse_name:
            self.owner.name = self.corpse_name
        self.owner.color = tcod.dark_red
        self.owner.blocks = False
        self.owner.send_back()
        self.owner.ai = None
    def is_dead(self):
        return self.hp <= 0
    
            
###### ATTACKER
class Attacker:
    def __init__(self, power):
        self.power = power
    def attack(self, target):
        #target = map.get_actor(self.owner.x + x, self.owner.y + y)
        if target is None:
            return False
        if target.destructible and not target.destructible.is_dead():
            if self.power > target.destructible.defense:
                target.destructible.take_damage(self.power)
                return self.power - target.destructible.defense
            else:
                return 0
        else:
            return None

###### AI
class Ai:
    def update(self):
        pass
                

        
