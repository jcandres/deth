#!/usr/bin/env python
import libtcodpy as tcod
import core
import enum
import game
import map
import gui

''' ai and stuff - base class is empty! '''

class Ai(core.Ai):
    pass

class AiPlayer(Ai):
    def __init__(self):
        Ai.__init__(self)
        self.last_command = None
    def update(self):
        dx = 0
        dy = 0
        if game.key.vk == tcod.KEY_RIGHT:
            dx = +1
        elif game.key.vk == tcod.KEY_LEFT:
            dx = -1
        elif game.key.vk == tcod.KEY_UP:
            dy = -1
        elif game.key.vk == tcod.KEY_DOWN:
            dy = +1
        else:
            self.handle_action_key(game.key.c)
            
        #process attacks or movement
        if dx != 0 or dy != 0:
            e = map.get_actor_alive(self.owner.x+dx, self.owner.y+dy)
            if e and e.blocks and e.destructible:
                nam = e.name
                self.owner.attacker.attack(e)
                game.log(self.owner.name, 'hit the', nam)
                if e.destructible.is_dead():
                    game.log(self.owner.name, 'killed the', nam+'!')
                game.game_state = enum.GameS.NEW_TURN #
            elif game.player.move(dx, dy):
                game.game_state = enum.GameS.NEW_TURN #
        
    def handle_action_key(self, key):
        #repeat
        if key == ord("x") and self.last_command:
            self.last_command.pickable.use(self.owner, self.owner)
            game.game_state = enum.GameS.NEW_TURN
        #inventory
        if key == ord("i"):
            gui.draw_inventory(0, self.owner.container.inventory, 'inventory')
            item = self.choose_from_inventory(self.owner.container.inventory)
            if item is not None:
                if item.pickable.use(self.owner, self.owner):
                    game.game_state = enum.GameS.NEW_TURN
                    self.last_command = item
                else:
                    game.log("that's a silly thing to use")
                    game.log_turn()
        #drop items
        if key == ord("d"):
            gui.draw_inventory(0, self.owner.container.inventory, 'drop an object')
            item = self.choose_from_inventory(self.owner.container.inventory)
            if item is not None:
                if item.pickable.drop(self.owner):
                    game.game_state = enum.GameS.NEW_TURN
        #equip / dequip stuff
        if key == ord("e"):
            gui.draw_equipment(0, self.owner.container.inventory, 'equipment')
            item = self.choose_from_inventory(self.owner.container.inventory)
            if item is not None and item.equipment:
                item.equipment.toggle_equip(self.owner)
                #game.log('ai player - equip', item.name)
                game.game_state = enum.GameS.NEW_TURN
        #grab
        elif key == ord("g"):
            self.owner.send_front()
            e = map.get_actor_pickable(self.owner.x, self.owner.y)
            if e and e.pickable:
                if e.pickable.pick(self.owner):
                    game.log('you pick a', e.name)
                    game.game_state = enum.GameS.NEW_TURN #
                else:
                    game.log("you can't carry more")
                    game.log_turn()
        #look
        elif key == ord(";"):
            self.owner.send_front() #will be checked the last 
            e = map.get_actor(self.owner.x, self.owner.y)
            if e and e is not self.owner:
                game.log('you see a', e.name, 'here')
            else:
                game.log("there's nothing of interest here")
            game.game_state = enum.GameS.NEW_TURN #
            self.owner.action_points -= 100
            
    def choose_from_inventory(self, inventory):
        #gui.draw_inventory(0, inventory, title)
        key = tcod.console_wait_for_keypress(True)
        if key.vk == tcod.KEY_CHAR:
            actor_index = key.c - ord('a')
            if actor_index >= 0 and actor_index < len(inventory):
                return inventory[actor_index]
        return None
    def choose_direction(self):
        gui.draw_directions(0, self.owner)
        key = tcod.console_wait_for_keypress(True)
        key = tcod.console_wait_for_keypress(True)
        if key.vk == tcod.KEY_RIGHT:
            return enum.dir.RIGHT
        elif key.vk == tcod.KEY_LEFT:
            return enum.dir.LEFT
        elif key.vk == tcod.KEY_UP:
            return enum.dir.UP
        elif key.vk == tcod.KEY_DOWN:
            return enum.dir.DOWN
        return None

class AiZombie(Ai):
    
    def __init__(self):
        self.tracking_turns = 5
        self.move_count = 0
     
    def update(self):
        if map.is_fov(self.owner.x, self.owner.y):
            self.move_count = self.tracking_turns
        if self.move_count:
            self.move_count -= 1
            self.seek_and_destroy(game.player)
            
    def seek_and_destroy(self, target):
        if target:
            dx = target.x - self.owner.x
            dy = target.y - self.owner.y
            distance = map.get_distance(self.owner, target)
            if distance > 0:
                dx = int(round(dx / distance))
                dy = int(round(dy / distance))
                d = tcod.random_get_int(0,0,1) #make them zombies move orthogonally fuck
                if d == 0:
                    if dx != 0:
                        dy = 0
                    else:
                        dx = 0
                self.owner.move(dx, dy)
                e = map.get_actor_alive(self.owner.x+dx, self.owner.y+dy)
                if e and map.is_fov(self.owner.x, self.owner.y):
                    self.owner.attacker.attack(e)
                    if e is game.player:
                        game.log('the', self.owner.name, 'hits!')
                    elif e.destructible:
                        game.log('a', self.owner.name, 'hits the', e.name)
            
        

