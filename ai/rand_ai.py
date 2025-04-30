import random

class RandomAI:
    NAME = "Random Randy"  
    
    def __init__(self, player):
        self.player = player

    def get_best_move(self, game):
        return random.choice(game.get_empty_cells())