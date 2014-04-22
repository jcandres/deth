#!/usr/bin/env python

class GameS:
    STARTUP = 0
    IDLE = 1
    NEW_TURN = 2
    VICTORY = 3
    DEFEAT = 4
    
class dir:
    UP = [0, -1]
    DOWN = [0, +1]
    RIGHT = [1, 0]
    LEFT = [-1, 0]