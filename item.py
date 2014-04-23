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
    def __init__(self, slot, **kw):
        core.Equipment.__init__(self, slot=slot, **kw) 

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
        
class Digger(Pickable):
    def use(self, wearer, target):
        if not wearer.ai:
            return False
        d = wearer.ai.choose_direction()
        if d is None:
            return False
        
        dx =  wearer.x + d[0]
        dy =  wearer.y + d[1]
        if map.is_wall(dx, dy):
            if map.is_diggable(dx, dy):
                map.set_wall(dx, dy, False, False)
                game.log('with great effort,', wearer.name, 'dig into the solid rock')
                wearer.action_points -= game.NORMAL_SPEED*10
            else:
                game.log('this rock is too hard for', wearer.name, 'to dig..')
        else:
            game.log(wearer.name, "can't dig here")
        return True
        
            
class ExplosiveThrow(Pickable):
    def __init__(self, radius, damage, length):
        Pickable.__init__(self) 
        self.radius = radius
        self.damage = damage + tcod.random_get_int(0, 0, 2)
        self.length = length
    def use(self, wearer, target):
        d = game.player.ai.choose_direction()
        if d is None:
            return False
        
        dist = self.length + wearer.power / 3
        tx =  wearer.x# + d[0]
        ty =  wearer.y# + d[1]
        while dist:
            dist -= 1
            tx += d[0]
            ty += d[1]
            a = map.get_actor_alive(tx, ty)
            if (a and a is not wearer) or map.is_blocked(tx, ty):
                dist = 0
        target_x = tx#wearer.x + (d[0] * self.throw)
        target_y = ty#wearer.y + (d[1] * self.throw)
        
        game.log(wearer.name,"threw the", self.owner.name+'!')
        game.log_turn()
        game.log('BOOOM!!')
        game.log_turn()
        did_hole = False
        for x in range(target_x-self.radius+1, target_x+self.radius):
            for y in range(target_y-self.radius+1, target_y+self.radius):
                if map.is_diggable(x, y):
                    map.set_wall(x, y, False, False)
                    did_hole = True
                if not map.is_wall(x, y):
                    if map.get_distance_coord(target_x, target_y, x, y) < self.radius:
                        s = ent.Smoke(x, y, tcod.random_get_int(0, 0, game.NORMAL_SPEED*5),
                                      was_visible=not map.is_wall(x,y))
                        game.actors.append(s)
                        s = ent.Projectile(x, y, self.damage, wearer, name='explosion', self_remove=True)
                        game.actors.append(s)
                        
        if did_hole:
            game.log("the", self.owner.name, 'made a huge hole in the walls!')
        map.fov_recompute(game.player.x, game.player.y)
        if wearer and wearer.container:
            wearer.container.inventory.remove(self.owner)
            pass
        return True
    
class SmokeThrow(Pickable):
    def __init__(self, radius, damage, throw):
        Pickable.__init__(self) 
        self.radius = radius + tcod.random_get_int(0, 0, 2)
        self.damage = damage
        self.throw = throw
    def use(self, wearer, target):
        d = game.player.ai.choose_direction()
        if d is None:
            return False
        target_x = wearer.x + (d[0] * self.throw)
        target_y = wearer.y + (d[1] * self.throw)
        for x in range(target_x-self.radius+1, target_x+self.radius):
            for y in range(target_y-self.radius+1, target_y+self.radius):
                if not map.is_wall(x, y) and map.get_distance_coord(target_x, target_y, x, y) < self.radius:
                    s = ent.Smoke(x, y, tcod.random_get_int(0, 0, game.NORMAL_SPEED*5))
                    game.actors.append(s)
        map.fov_recompute(game.player.x, game.player.y)
        game.log(wearer.name,"threw the", self.owner.name)
        game.log("a really dense gas expands quickly! vision is difficult")
        if wearer and wearer.container:
            wearer.container.inventory.remove(self.owner)
        return True
    
class SlingshotThrow(Pickable):
    def __init__(self, length, damage):
        Pickable.__init__(self) 
        self.length = length
        self.damage = damage
    def use(self, wearer, target):
        if not wearer.ai:
            return False
        d = wearer.ai.choose_direction()
        if d is None:
            return False
        
        dist = self.length + wearer.power / 3
        x =  wearer.x# + d[0]
        y =  wearer.y# + d[1]
        while dist:
            dist -= 1
            x += d[0]
            y += d[1]
            a = map.get_actor_alive(x, y)
            if (a and a is not wearer) or map.is_blocked(x, y):
                dist = 0
                if map.is_wall(x, y):
                    x -= d[0]
                    y -= d[1]
        p = ent.Projectile(x, y, self.damage, wearer)
        game.actors.append(p)
        return True
        
            

            
        
