#!/usr/bin/env python

import libtcodpy as tcod
import enum
import game
import map
import gui


class Object:
    def __init__(self, x, y, char="?", name="something",color=tcod.lighter_gray, blocks=True, speed=10,
                 invisible=False, material=None,
                 destructible=None, attacker=None, ai=None, pickable=None, container=None, equipment=None):
        self.x = x
        self.y = y
        self.char = char
        self._name = name
        self.init_name = name
        self.color = color
        self.blocks = blocks
        self.invisible = invisible
        self.material = material
        
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
    #############################################################################
    @property
    def name(self):
        n=[]
        if self.destructible and self.destructible.is_dead(): n.append('dead')
        if self.invisible: n.append('invisible')
        if self.material: n.append(self.material)
        n.append(self._name)
        return ' '.join(n)
    @property
    def speed(self):
        bonus = sum(item.equipment.bonus_sp for item in self.get_all_equipped())
        return self.speed + bonus
    @property
    def power(self):
        if not self.attacker:
            return 0
        base = self.attacker.power
        bonus = sum(item.equipment.bonus_po for item in self.get_all_equipped())
        return base + bonus
    @property
    def defense(self):
        if not self.destructible:
            return 0
        base = self.destructible.defense
        bonus = sum(item.equipment.bonus_de for item in self.get_all_equipped())
        return base + bonus
    @property
    def max_hp(self):
        if not self.destructible:
            return 0
        base = self.destructible.max_hp
        bonus = sum(item.equipment.bonus_hp for item in self.get_all_equipped())
        return base + bonus
    ############################################################################
    
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
            
    def draw(self, con, skip_fov=False, no_char=False):
        '''skip_fov: means seeing with TEH MIND! - also makes invisible display as <space>
        no_char: means that the player can 'sense', but not see clearly - aka blinded'''
        tcod.console_set_default_foreground(con, self.color)
        ch = self.char
        
        if self.invisible and not skip_fov:
            return False
        if no_char:
            ch = ' '
        if skip_fov:
            tcod.console_put_char(con, self.x, self.y, ch, tcod.BKGND_NONE)
            return True
        if map.is_fov(self.x, self.y):
            tcod.console_put_char(con, self.x, self.y, ch, tcod.BKGND_NONE)
            
        
    def get_equipped_in_slot(self, slot): 
        if not self.container:
            return None
        for obj in self.container.inventory:
            if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
                return obj
        return None
    def get_all_equipped(self):
        if not self.container:
            return []
        equip_list = []
        for obj in self.container.inventory:
            if obj.equipment and obj.equipment.is_equipped:
                equip_list.append(obj)
        return equip_list
    
    def move(self, dx, dy):
        if map.is_wall(self.x+dx, self.y+dy) or map.is_blocked(self.x+dx, self.y+dy):
            return False
        else:
            self.x += dx
            self.y += dy
            return True
        
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
        if self.owner.equipment and self.owner.equipment.is_equipped:
            game.log(wearer.name, "can't drop something equipped!")
            game.log_turn()
            return False
        game.log(wearer.name, 'dropped a', self.owner.name)
        wearer.container.inventory.remove(self.owner)
        game.actors.append(self.owner)
        self.owner.x = wearer.x
        self.owner.y = wearer.y
        return True
        
        
##### EQUIPABLE
class Equipment(Object):
    def __init__(self, slot, po=0, de=0, hp=0, sp=0):
        self.bonus_po = po
        self.bonus_de = de
        self.bonus_hp = hp
        self.bonus_sd = sp
        self.slot = slot
        self.is_equipped = False
    def toggle_equip(self, wearer):
        if self.is_equipped:
            self.dequip(wearer)
        else:
            self.equip(wearer)
    def equip(self, wearer):
        old_equipment = wearer.get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.equipment.dequip(wearer)
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
            if self.owner.power > target.defense:
                target.destructible.take_damage(self.owner.power)
                return self.owner.power - target.defense
            else:
                return 0
        return None
    def attack_tile(self, x, y):
        target = map.get_actor_alive(x, y)
        if target:
            if self.owner.power > target.defense:
                target.destructible.take_damage(self.owner.power)
                #return self.owner.power - target.defense
                return target
            else:
                return False
        return None

###### AI
class Ai:
    def __init__(self):
        pass
    def update(self):
        pass
                

        
