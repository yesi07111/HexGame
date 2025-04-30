import time
import heapq
import hashlib
import asyncio
import numpy as np

from typing import List, Tuple
from asgiref.sync import async_to_sync
from itertools import zip_longest as zipl

HEX_NEIGHBORS = (
    (1, -1),
    (-1, 1),
    (-1, 0),
    (0, -1),
    (0, 1),
    (1, 0),
)

class DisjointSet:
    def __init__(self, size: int):
        self.parent = list(range(size**2))

        self.leftmost_index = [list(range(size)) for _ in range(size)]
        self.leftmost_index = [e for row in self.leftmost_index for e in row]
        self.rightmost_index = [list(range(size)) for _ in range(size)]
        self.rightmost_index = [e for row in self.rightmost_index for e in row]

        self.uppermost_index = [[i for _ in range(size)] for i in range(size)]
        self.uppermost_index = [e for row in self.uppermost_index for e in row]
        self.bottommost_index = [[i for _ in range(size)] for i in range(size)]
        self.bottommost_index = [e for row in self.bottommost_index for e in row]

    async def copy(self):
        new_instance = DisjointSet(1)

        new_instance.parent = self.parent[:]
        new_instance.leftmost_index = self.leftmost_index[:]
        new_instance.rightmost_index = self.rightmost_index[:]
        new_instance.uppermost_index = self.uppermost_index[:]
        new_instance.bottommost_index = self.bottommost_index[:]

        return new_instance

    async def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = await self.find(self.parent[x])
        return self.parent[x]

    async def union(self, x: int, y: int) -> None:
        rootX = await self.find(x)
        rootY = await self.find(y)

        if rootX != rootY:
            self.leftmost_index[rootY] = min( # type: ignore
                self.leftmost_index[rootY], self.leftmost_index[rootX]
            )
            self.uppermost_index[rootY] = min( # type: ignore
                self.uppermost_index[rootY], self.uppermost_index[rootX]
            )

            self.rightmost_index[rootY] = max( # type: ignore
                self.rightmost_index[rootY], self.rightmost_index[rootX]
            )
            self.bottommost_index[rootY] = max( # type: ignore
                self.bottommost_index[rootY], self.bottommost_index[rootX]
            )

            self.parent[rootX] = rootY

    async def connected(self, x: int, y: int) -> bool:
        return await self.find(x) == await self.find(y)

class HexGameSim:
    def __init__(self, board_size: int):
        self.board_size = board_size
        self.board = np.zeros(shape=(board_size, board_size), dtype="int8")
        self.disjoint_set = DisjointSet(board_size)
        self.current_player = 1  # A = 1, B = -1
        self.winner = None

    async def copy(self):
        new_instance = HexGameSim(1)
        new_instance.board_size = self.board_size
        new_instance.board = self.board.copy()
        new_instance.disjoint_set = await self.disjoint_set.copy()
        new_instance.current_player = self.current_player
        new_instance.winner = self.winner

        return new_instance

    async def is_valid_action(self, position: Tuple[int, int]) -> bool:
        position = tuple(position) # type: ignore
        x, y = position

        return (
            0 <= x < self.board_size
            and 0 <= y < self.board_size
            and self.board[position] == 0
        )

    async def place_piece(self, position: Tuple[int, int]) -> bool:
        position = tuple(position) # type: ignore
        if not await self.is_valid_action(position):
            raise ValueError(f"❌ La posición {position} no es válida.")

        player = self.current_player
        self.current_player *= -1  # This changes from player A to B and from B to A

        self.board[position] = player

        action_x, action_y = position

        flat_action_index = np.ravel_multi_index(
            position, (self.board_size, self.board_size)
        )

        for x, y in HEX_NEIGHBORS:
            nX, nY = x + action_x, y + action_y
            neighbor = nX, nY

            if not (
                0 <= nX < self.board_size
                and 0 <= nY < self.board_size
                and self.board[neighbor] == player
            ):
                continue

            flat_index = np.ravel_multi_index(
                neighbor, (self.board_size, self.board_size)
            )

            await self.disjoint_set.union(flat_action_index, flat_index) # type: ignore

        action_group = await self.disjoint_set.find(flat_action_index) # type: ignore

        left = self.disjoint_set.leftmost_index[action_group]
        right = self.disjoint_set.rightmost_index[action_group]

        upper = self.disjoint_set.uppermost_index[action_group]
        bottom = self.disjoint_set.bottommost_index[action_group]

        if player == 1:
            win = left == 0 and right == self.board_size - 1
        elif player == -1:
            win = upper == 0 and bottom == self.board_size - 1
        else:
            raise ValueError("❌ Error: El jugador solo puede ser 1 o -1.")

        if win:
            self.winner = player

        return win

class MasterAI:
    NAME = "MasterAI"
    def __init__(self, player, time=30):
        self.player = player
        self.memo = {}
        self.maxtime = time - time/8
        self.player_a_moves = []
        self.player_b_moves = []

    async def _heuristics(self, position: Tuple[int, int], player: int):
        x, y = position

        if player == 1:
            return 10 - y
        return 10 - x

    async def _a_star(self, board: HexGameSim, player: int) -> float:
        if player == -1:
            player_positions = [(0, i) for i in range(board.board_size)]
        elif player == 1:
            player_positions = [(i, 0) for i in range(board.board_size)]

        distances = np.zeros_like(board.board) + np.inf

        q = []
        for position in player_positions:
            if board.board[position] == -player:
                continue

            position = tuple(position)
            h = await self._heuristics(position, player) 
            heapq.heappush(q, (h, position))

        while len(q) != 0:
            _weight, position = heapq.heappop(q)

            x, y = position

            if distances[position] != float("inf"):
                continue

            distances[position] = _weight

            if (player == 1 and y == 10) or (player == -1 and x == 10):
                return _weight

            for c, r in HEX_NEIGHBORS:
                neighbor = (x + c, y + r)
                nx, ny = neighbor

                if (
                    not (
                        0 <= nx < board.board_size and 0 <= ny < board.board_size
                    )  # out of bounds
                    or board.board[neighbor] == -player  # not valid
                    or distances[neighbor] != float("inf")  # already visited
                ):
                    continue

                weight = 0 if board.board[neighbor] == player else 1
                h = await self._heuristics(neighbor, player)

                f = _weight + weight + h
                heapq.heappush(q, (f, neighbor))

        return float("inf")

    async def eval_board(self, board: HexGameSim, player: int = 1) -> float:
        enemy = 1 if board.current_player == -1 else -1

        distances_player = await self._a_star(board, board.current_player) 
        distances_enemy = await self._a_star(board, enemy)

        return distances_enemy / (distances_player + 0.00001)

    async def alpha_beta_search(
        self, game: HexGameSim, depth: int, alpha: float, beta: float, maximize: bool
    ) -> float:
        if depth == 0 or await self._a_star(game, -game.current_player) == 0:
            return await self.eval_board(game, game.current_player)

        state_key = (await hash_matrix(game.board), depth, maximize)

        if state_key in self.memo:
            return self.memo[state_key]

        value = 0
        start_time = time.time()
            
        def check_time():
            if time.time() - start_time > self.maxtime:
                raise asyncio.TimeoutError("Timeout en búsqueda")
        if maximize:
            max_eval = float("-inf")
            valid_moves = await get_valid_moves(game.board, self.player, player_a=self.player_a_moves, player_b=self.player_b_moves, depth=depth)

            for move in valid_moves:
                check_time()
                game.board[move] = game.current_player
                game.current_player *= -1

                eval = await self.alpha_beta_search(
                    game, depth - 1, alpha, beta, not maximize
                )
                
                game.board[move] = 0
                game.current_player *= -1

                max_eval = max(max_eval, eval)

                if max_eval > beta:
                    break

                alpha = max(alpha, max_eval)

            value = max_eval
        else:
            min_eval = float("inf")
            valid_moves = await get_valid_moves(game.board, self.player, player_a=self.player_a_moves, player_b=self.player_b_moves, depth=depth)

            for move in valid_moves:
                check_time()
                game.board[move] = game.current_player
                game.current_player *= -1

                eval = await self.alpha_beta_search(
                    game, depth - 1, alpha, beta, not maximize
                )

                game.board[move] = 0
                game.current_player *= -1

                min_eval = min(min_eval, eval) 

                if min_eval < alpha:
                    break

                beta = min(beta, min_eval)

            value = min_eval

        self.memo[state_key] = value
        return value

    @async_to_sync
    async def get_best_move(self, game):
        self.winning_move = None
        async def eval_position(position, game_state) -> Tuple[float, Tuple[int, int]]|Exception:
            res = await game_state.place_piece(position)

            if res:
                self.winning_move = position
                return float("inf"), position
            
            move_eval = await self.alpha_beta_search(game_state, 3, float("-inf"), float("inf"), False)
    
            return move_eval, position 
        
        board_list: List = game.board
        size: int = game.size

        _game = HexGameSim(size)

        for i, row in enumerate(board_list):
            for j, col in enumerate(row):
                if (i, j) in self.player_a_moves or (i, j) in self.player_b_moves:
                    continue 
                if col == 0:
                    self.player_a_moves.append((i, j))
                if col == 1:
                    self.player_b_moves.append((i, j))

        for a, b in zipl(self.player_a_moves, self.player_b_moves, fillvalue=(-1, -1)):
            await _game.place_piece(a)
            try:
                await _game.place_piece(b)
            except ValueError:
                pass

        valid_positions = await get_valid_moves(_game.board, self.player, player_a=self.player_a_moves, player_b=self.player_b_moves, depth=3)
        best_eval = float("-inf")
        best_move = (-1, -1)

        tasks = []

        for space in valid_positions:
            __game = await _game.copy()
            task = asyncio.create_task(eval_position(space, __game))
            tasks.append(task)

        try:
            done, pending = await asyncio.wait(
                tasks,
                timeout=self.maxtime,
                return_when=asyncio.ALL_COMPLETED
            )
        except asyncio.TimeoutError:
            done, pending = await asyncio.wait(tasks, timeout=0)

        # Cancelar tareas pendientes
        for task in pending:
            task.cancel()
        
        if self.winning_move:
            print(f"🎉 Jugada ganadora encontrada: {self.winning_move}")
            return self.winning_move

        # Procesar resultados completados
        for task in done:
            try:
                move_eval, space = await task
                print(f"🎯 Movimiento: {space} ->  💎 Evaluación: {move_eval}")
                if move_eval > best_eval:
                    best_eval = move_eval
                    best_move = space
            except Exception as e:
                continue
        print(f"✅ Seleccionada: {best_move} con valor {best_eval}")
        return best_move

async def hash_matrix(matrix: np.ndarray):
    if not isinstance(matrix, np.ndarray):
        raise TypeError("Input must be a NumPy array")

    if matrix.ndim != 2:
        raise ValueError("Input array must be 2-dimensional")

    matrix_bytes = matrix.tobytes()
    hash_obj = hashlib.sha256(matrix_bytes)
    return hash_obj.hexdigest()

async def get_valid_moves(board: np.ndarray, player: int, player_a=None, player_b=None, depth=3) -> list:
    if not isinstance(board, np.ndarray):
        raise TypeError("Input must be a NumPy array")
    if board.ndim != 2:
        raise ValueError("Input array must be 2-dimensional")

    h, w = board.shape
    valid = []

    edge_candidates = [(h//2, w//2)]
    for edge in edge_candidates:
        if board[edge] == 0:
            valid.append(edge)

    def safe_coords(data):
        if isinstance(data, np.ndarray):
            return [tuple(map(int, pos)) for pos in data]
        return data or []

    player_a = safe_coords(player_a) if player_a is not None else safe_coords(np.argwhere(board == 1))
    player_b = safe_coords(player_a) if player_b is not None else safe_coords(np.argwhere(board == -1))

    a_positions = player_a[-3:] if (depth <= 2 and len(player_a) >= 3) else player_a.copy()
    b_positions = player_b[-3:] if (depth <= 2 and len(player_b) >= 3) else player_b.copy()

    ordered = a_positions + b_positions if player == 1 else b_positions + a_positions

    for pos in ordered:
        try:
            x, y = map(int, pos)
            for dx, dy in HEX_NEIGHBORS:
                nx, ny = x + dx, y + dy
                if 0 <= nx < h and 0 <= ny < w and board[nx, ny] == 0 and (nx, ny) not in valid:
                    valid.append((nx, ny))
        except (ValueError, IndexError, TypeError):
            continue    
    return valid
        
def annoying_move(game, rival, path):
    last_move = game.last_move[rival]
    rival_eff_len, rival_path, best_rival_gap, rival_gaps, blocked = game.longest_virtual_paths[rival]
    
    if last_move is None:
        print("🎲 [MOV ALEATORIO] Sin último movimiento rival - movimiento aleatorio")
        return game.random_valid_move()
    
    original_dir = _get_closest_edge_direction(rival, last_move, game, path)
    print(f"📍 [DIRECCIÓN OBJETIVO] Moviéndose hacia {original_dir} desde {last_move}")
    
    # 1. Intentar dirección principal
    main_move = (last_move[0] + original_dir[0], last_move[1] + original_dir[1])
    if game.is_valid_move(*main_move):
        print(f"🔄 [MOV DIRECTO] Siguiendo dirección principal hacia {main_move}")
        return main_move
    elif best_rival_gap:
        print(f"🔒 [MOV DIRECTO BLOQUEADO] Atacando mejor gap del rival: {best_rival_gap}")
        return best_rival_gap
    else:
        # 2. Intentar alternativas originales
        alt_moves = [
            (last_move[0] + original_dir[0] + 1, last_move[1] + original_dir[1]),
            (last_move[0] + original_dir[0], last_move[1] + original_dir[1] + 1),
            (last_move[0] + original_dir[0] - 1, last_move[1] + original_dir[1]),
            (last_move[0] + original_dir[0], last_move[1] + original_dir[1] - 1)
        ]
        for move in alt_moves:
            if game.is_valid_move(*move):
                print(f"🔄 [MOV ALTERNATIVO] Usando dirección secundaria hacia {move}")
                return move
        
        # 3. Intentar dirección opuesta (-1 * dirección original)
        opposite_dir = (-original_dir[0], -original_dir[1])
        opposite_move = (last_move[0] + opposite_dir[0], last_move[1] + opposite_dir[1])
        if game.is_valid_move(*opposite_move):
            print(f"🔄 [MOV OPUESTO] Invirtiendo dirección hacia {opposite_move}")
            return opposite_move
        
        # 4. Intentar diagonales estratégicas según dirección original
        if original_dir[0] == 0:  # Dirección horizontal
            diagonal_dirs = [(-1, original_dir[1]), (1, original_dir[1])]  # Arriba-derecha/izquierda y abajo-derecha/izquierda
        else:  # Dirección vertical
            diagonal_dirs = [(original_dir[0], -1), (original_dir[0], 1)]  # Izquierda-arriba/abajo y derecha-arriba/abajo
        
        diagonal_moves = [(last_move[0] + d[0], last_move[1] + d[1]) for d in diagonal_dirs]
        for move in diagonal_moves:
            if game.is_valid_move(*move):
                print(f"🔄 [MOV DIAGONAL] Explorando diagonal estratégica hacia {move}")
                return move
        
        # 5. Fallback final a movimiento aleatorio
        print("🎲 [MOV ALEATORIO FALLBACK] No se encontraron movimientos estratégicos - aleatorio")
        return game.random_valid_move()   
 
def _get_closest_edge_direction(player, gap, game, path):
        """Devuelve la dirección hacia el borde más cercano + objetivo"""
        size = game.size
        q, r = gap
        occupied_spots = set()
        for pos in path:
            if player == 0:
                occupied_spots.add(pos[1])
            else:
                occupied_spots.add(pos[0])
        
        midpoint = (size - 1) // 2
        
        if player == 0:  # Horizontal: priorizar derecha (objetivo)
            # Determinar si la mayoría de los números en occupied_spots son menores o mayores que el punto medio
            if sum(1 for spot in occupied_spots if spot <= midpoint) > len(occupied_spots) / 2:
                return (0, 1)  # Mayoría menor que el punto medio
            else:
                return (0, -1)  # Mayoría mayor que el punto medio

        else:  # Vertical: priorizar abajo (objetivo)
            # Determinar si la mayoría de los números en occupied_spots son menores o mayores que el punto medio
            if sum(1 for spot in occupied_spots if spot <= midpoint) > len(occupied_spots) / 2:
                return (1, 0)  # Mayoría menor que el punto medio
            else:
                return (-1, 0)  # Mayoría mayor que el punto medio

