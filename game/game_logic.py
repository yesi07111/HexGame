import random
import copy
import numpy as np

from game.configs import *

class HexGame:
    def __init__(self, size, game_mode, players):
        self.size = size
        self.game_mode = game_mode
        self.players = players
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.player0_positions = []
        self.player1_positions = []
        self.current_player = 0
        self.winner = None
        self.winning_path = []
        self.longest_virtual_paths = {0: (0, [], None, [], False), 1: (0, [], None, [], False)}
        self.last_move = {0: None, 1: None}
        self.step_before_last = {0: None, 1: None}
        self.last_move_save_copy = {0: None, 1: None}
        self.step_before_last_save_copy = {0: None, 1: None}
        self.disjoint_set = DisjointSet(size)
        self.disjoint_set_save_copy = DisjointSet(size)
        
        # Estados IA
        self.ai_thinking = False
        self.ai_target = None
        self.ai_progress = 0
        self.ai = None
        self.ai2 = None
        
        if game_mode == "PVAI":
            pass  # La IA se configurará desde main.py
        elif game_mode == "AIVAI":
            self.ai = None  # Se configurará desde main.py
            self.ai2 = None
    
    def place_piece(self, r, q, player=None):
        player = player if player is not None else self.current_player
        if self.is_valid_move(r, q):
            self.board[r][q] = player
            if player == 0:
                self.player0_positions.append((r, q))
            else:
                self.player1_positions.append((r, q))
            if self.last_move[player] is not None:
                step_before = copy.deepcopy(self.last_move[player])
                self.step_before_last[player] = step_before
            self.last_move[player] = (r, q)
            return True
        return False
    
    def place_piece_for_test(self, r, q, player=None):
        player = player if player is not None else self.current_player
        if self.is_valid_move(r, q):
            self.board[r][q] = player
            self.last_move_save_copy = copy.deepcopy(self.last_move)
            self.step_before_last_save_copy = copy.deepcopy(self.step_before_last)
            self.disjoint_set_save_copy = copy.deepcopy(self.disjoint_set)
            if self.last_move[player] is not None:
                step_before = self.last_move[player]
                temp = step_before
                self.step_before_last[player] = temp
            self.last_move[player] = (r, q)
            return True
        return False

    def get_player_positions(self, player):
        return self.player0_positions if player == 0 else self.player1_positions

    def get_neighbors(self, pos):
        q, r = pos
        return [(q + dq, r + dr) for dq, dr in HEX_NEIGHBORS 
                if 0 <= q + dq < self.size and 0 <= r + dr < self.size]

    def is_valid_move(self, q, r):
        return 0 <= q < self.size and 0 <= r < self.size and self.board[q][r] is None

    def check_win(self, player):
            if self.last_move[player] is None:  # Añadir validación
                return False
            position = self.last_move[player]
            action_x, action_y = position

            flat_action_index = np.ravel_multi_index(
                position, (self.size, self.size)
            )

            for x, y in HEX_NEIGHBORS:
                nX, nY = x + action_x, y + action_y
                neighbor = nX, nY

                if not (
                    0 <= nX < self.size
                    and 0 <= nY < self.size
                    and self.board[nX][nY] == player
                ):
                    continue

                flat_index = np.ravel_multi_index(
                    neighbor, (self.size, self.size)
                )

                self.disjoint_set.union(flat_action_index, flat_index)

            action_group = self.disjoint_set.find(flat_action_index)

            left = self.disjoint_set.leftmost_index[action_group]
            right = self.disjoint_set.rightmost_index[action_group]

            upper = self.disjoint_set.uppermost_index[action_group]
            bottom = self.disjoint_set.bottommost_index[action_group]

            if player == 0:
                win = left == 0 and right == self.size - 1
            elif player == 1:
                win = upper == 0 and bottom == self.size - 1
            else:
                raise ValueError("Player can only be 0 or 1.")

            if win:
                self.winner = player

            return win

    def copy(self):
        """Crea una copia profunda del juego"""
        new_game = HexGame(self.size, self.game_mode, self.players)
        new_game.board = [row.copy() for row in self.board]
        new_game.current_player = self.current_player
        new_game.winner = self.winner
        new_game.winning_path = self.winning_path.copy() if self.winning_path else []
        new_game.player0_positions = self.player0_positions.copy()
        new_game.player1_positions = self.player1_positions.copy()
        new_game.longest_virtual_paths = {
            0: (self.longest_virtual_paths[0][0], self.longest_virtual_paths[0][1].copy(), self.longest_virtual_paths[0][2]),
            1: (self.longest_virtual_paths[1][0], self.longest_virtual_paths[1][1].copy(), self.longest_virtual_paths[1][2])
        }
        new_game.last_move = self.last_move.copy()  
        new_game.step_before_last = self.step_before_last.copy()
        return new_game
    
    def undo_move(self, q, r):
        """Revierte un movimiento"""
        if self.board[q][r] == 0 and (q, r) in self.player0_positions:
            self.player0_positions.remove((q, r))
        else:
            if (q, r) in self.player1_positions:
                self.player1_positions.remove((q, r))
        self.board[q][r] = None
        self.winner = None

    def undo_test_move(self, q, r):
        """Revierte un movimiento"""
        if self.board[q][r] == 0 and (q, r) in self.player0_positions:
            self.player0_positions.remove((q, r))
        else:
            if (q, r) in self.player1_positions:
                self.player1_positions.remove((q, r))
        self.last_move = copy.deepcopy(self.last_move_save_copy)
        self.step_before_last = copy.deepcopy(self.step_before_last_save_copy)
        self.disjoint_set = copy.deepcopy(self.disjoint_set_save_copy)
        self.board[q][r] = None
        self.winner = None
    
    def get_empty_cells(self):
        """Obtiene todas las celdas vacías"""
        return [(q, r) for q in range(self.size) for r in range(self.size) if self.board[q][r] is None]
    
    def is_board_full(self):
        """Verifica si el tablero está lleno"""
        return all(cell is not None for row in self.board for cell in row)

    def random_valid_move(self):
        """Devuelve un movimiento aleatorio válido"""
        empty_cells = self.get_empty_cells()
        if not empty_cells:
            return None  # No hay movimientos válidos si el tablero está lleno
        return random.choice(empty_cells)