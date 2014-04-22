#!/usr/bin/env python

import libtcodpy as tcod
import enum
import game
import map
import gui


class Object:
    def __init__(self, x, y, char="?", name="something",color=tcod.lighter_gray, blocks=True, speed=10,
                 destructible=None, attacker=None, ai=None, pickable=None, container=None, equipment=None):
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
        self.equipment = equipment
        
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
        if self.equipment:
            self.equipment.owner = self
            #add a pickable component to all equipable items
            self.pickable = Pickable()
            self.pickable.owner = self
    
    def update(self):
        if self.ai:
            self.ai.update()
        
    def get_equipped_in_slot(self, slot): ############
        if not self.owner.container:
            return None
        for obj in self.container.inventory:
            if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
                return obj.equipment
        return None
    def get_all_equipped(self):
        if not self.container:
            return None
        equip_list = []
        for obj in self.container.inventory:
            if obj.equipment and obj.is_equipped:
                equip_list.append(obj.equipment)
        return equip_list
    
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
    def use(self, *args):
        pass
    def drop(self, wearer):
        if not wearer.container:
            return False
        game.log(wearer.name, 'dropped a', self.owner.name)
        wearer.container.inventory.remove(self.owner)
        game.actors.append(self.owner)
        self.owner.x = wearer.x
        self.owner.y = wearer.y
        return True
        
        
##### EQUIPABLE
class Equipment(Object):
    def __init__(self, slot, bonus_pow=0, bonus_def=0, bonus_hp=0):
        self.bonus_pow = bonus_pow
        self.bonus_def = bonus_def
        self.bonus_hp = bonus_hp
        self.slot = slot
        self.is_equipped = False
    def toggle_equip(self, wearer):
        if self.is_equipped:
            self.dequip(wearer)
        else:
            self.equip(wearer)
    def equip(self, wearer):
        old_equipment = self.get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()
        self.is_equipped = True
        game.log(wearer.name, 'equipped a', self.owner.name)
        return True
    def dequip(self, wearer):
        if self.is_equipped:
            self.is_equipped = False
            game.log(wearer.name, 'took off a', self.owner.name)
            return True
        
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
                

        
