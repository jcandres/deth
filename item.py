#!/usr/bin/env python
import libtcodpy as tcod
import core
import enum
import game
import map
import gui
import ent

''' components of objects, items, scenery '''

class Pickable(core.Pickable):
    pass
class Container(core.Container):
    pass
class Equip(core.Equipment):
    pass

class Helmet(Equip):
    def __init__(self, bonus_def, slot='head'):
        Equip.__init__(self, slot=slot, bonus_def=bonus_def) 

class Healer(Pickable):
    def __init__(self, amount):
        Pickable.__init__(self) 
        self.amount = amount
    def use(self, wearer, target):
        if wearer and wearer.container:
            wearer.container.inventory.remove(self.owner)
        a = target.destructible.heal(self.amount)
        if a > 0:
            game.log('the', self.owner.name, 'heals', target.name, 'by', a, 'hp')
            return True
        else:
            game.log('the', self.owner.name, 'has no visible effect!')
            return True
            
class ExplosiveThrow(Pickable):
    def __init__(self, radius, damage, throw):
        Pickable.__init__(self) 
        self.radius = radius + tcod.random_get_int(0, 0, 5)
        self.damage = damage
        self.throw = throw
    def use(self, wearer, target):
        d = game.player.ai.choose_direction()
        if d is None:
            return False
        target_x = wearer.x + (d[0] * self.throw)
        target_y = wearer.y + (d[1] * self.throw)
        for x in range(target_x-self.radius, target_x+self.radius):
            for y in range(target_y-self.radius, target_y+self.radius):
                if not map.is_wall(x, y):
                    s = ent.Smoke(x, y, tcod.random_get_int(0, 0, game.NORMAL_SPEED*5))
                    game.actors.append(s)
        map.fov_recompute(game.player.x, game.player.y)
        game.log("you throw the grenade..")
        game.log("a really dense gas expands quickly! vision is difficult")
        if wearer and wearer.container:
            wearer.container.inventory.remove(self.owner)
        return True
        
            

            
        
