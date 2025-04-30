import random
from collections import deque

class MrHuman:
    NAME = "Mr. Human"
    def __init__(self, player):
        self.player = player
        self.directions = [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)]
        self.debug = True
        self.virtual_paths = {  # Almacenamiento optimizado de caminos
            0: {'length': 0, 'path': [], 'gap': None, 'all_gaps': None, 'blocked': None},
            1: {'length': 0, 'path': [], 'gap': None, 'all_gaps': None, 'blocked': None}
        }

    def get_best_move(self, game):
        print(f"\n🤖 [IA - Jugador {self.player}] Decidiendo movimiento...")   
        
        # Calcular caminos virtuales actualizados
        rival = 1 - self.player
        self_eff_len, self_path, best_self_gap, self_gaps, self_block = self.calculate_virtual_path(game, self.player)
        rival_eff_len, rival_path, best_rival_gap, rival_gaps, blocked = self.calculate_virtual_path(game, rival)

        print(f"\n✅ Mejor camino virtual para Rival (Jugador {1 - self.player}): Longitud {rival_eff_len}, Camino {rival_path} Gaps {rival_gaps} Best Gap {best_rival_gap}")
        print(f"✅ Mejor camino virtual para IA (Jugador {self.player}): Longitud {self_eff_len}, Camino {self_path} Gaps {self_gaps} Best Gap {best_self_gap}")

        # Lógica de primer movimiento (ambos jugadores sin piezas)
        if self_eff_len == 0 and rival_eff_len == 0 and len(game.player0_positions) == 0:
            board_mid = (game.size-1)//2
            print("🆕 [PRIMER MOVIMIENTO] Ambos jugadores sin piezas - eligiendo posición central aleatoria")
            if self.player == 0:
                return (random.choice([board_mid, board_mid + 1, board_mid - 1]), random.choice([board_mid]))
            else:
                return (random.choice([board_mid]), random.choice([board_mid, board_mid + 1, board_mid - 1]))

        # Lógica de segundo movimiento (IA sin piezas pero rival tiene)
        elif self_eff_len == 0:
            print(f"🚨 [SEGUNDO MOVIMIENTO] IA sin piezas - bloqueando camino rival con movimiento molesto")
            return self.annoying_move(game, rival, rival_path)

        # Comparación de caminos virtuales
        if rival_eff_len >= self_eff_len + 1:
            self_about_to_win = self.about_to_win(game, 1-rival, self_path)
            if self_about_to_win is not None:
                game.undo_test_move(self_about_to_win[0], self_about_to_win[1])
                print(f"⚔️⚔️ [Victoria garantizada] Movimiento ganador encontrado!")
                return self_about_to_win
            
            about_to_win = self.about_to_win(game, rival, rival_path)
            if about_to_win is not None:
                game.undo_test_move(about_to_win[0], about_to_win[1])
                print(f"🚨🚨 [ALERTA CRÍTICA] Rival a punto de ganar!")
                return about_to_win
            
            two_step_move = self.is_two_step_move(game, rival, rival_path)
            if two_step_move is not None:
                return two_step_move
            
            one_step_move = self.is_one_step_move(game, rival, rival_path)
            if one_step_move is not None:
                return one_step_move
            
            if blocked:
                is_near_main_path = self.last_move_near_main_path(game, rival)
                if is_near_main_path and best_self_gap:
                    if self_block and best_rival_gap:
                        print(f"🚧 [BLOQUEO ACTIVADO] Rival con camino bloqueado y camino propio bloqueado - usando mejor gap rival {best_rival_gap}")
                        return best_rival_gap
                    
                    elif self_block:
                        print(f"🚧 [BLOQUEO ACTIVADO] Rival con camino bloqueado y camino propio bloqueado - usando movimiento molesto")
                        return self.annoying_move(game, rival, rival_path)
                    
                    else:
                        print(f"🚧 [BLOQUEO ACTIVADO] Rival con camino bloqueado - usando mejor gap propio {best_self_gap}")
                        return best_self_gap
                    
                elif is_near_main_path:
                    print(f"🚧 [BLOQUEO ACTIVADO] Rival con camino bloqueado - activando expansion agresiva")
                    return self.aggressive_expansion(game, self.player)
                else:
                    print(f"🚧 [BLOQUEO ACTIVADO] Rival con camino bloqueado - usando movimiento molesto")
                    return self.annoying_move(game, rival, rival_path)
            else:        
                has_winning_chance = self.has_winning_chance(game, rival, rival_path)
                if has_winning_chance:
                    print(f"🚨🚨 [ALERTA CRÍTICA] Rival peligrosamente cerca del borde!")
                    # Estrategia de bloqueo agresivo
                    block_move = self.block_winning_path(game, rival, rival_path)
                    return block_move
                elif best_rival_gap:
                    print(f"🎯 [OBJETIVO CRÍTICO] Rival cerca de ganar - atacando mejor gap rival: {best_rival_gap}")
                    return best_rival_gap 
                elif game.last_move[rival] is not None:
                    print(f"🎯 [OBJETIVO SECUNDARIO] Rival cerca de ganar - atacando donde más le duele")
                    return self.annoying_move(game, rival, rival_path)
                
                # Lógica de flanqueo para jugador 1 (vertical)
                elif self.player == 1:
                    print("⚔️ [FLANQUEO VERTICAL] Intentando rodear última posición rival")
                    if game.is_valid_move(rival_path[-1][0] + 1, rival_path[-1][1] + 0): 
                        return (rival_path[-1][0] + 1, rival_path[-1][1])
                    elif game.is_valid_move(rival_path[-1][0] - 1, rival_path[-1][1] + 0):
                        return (rival_path[-1][0] - 1, rival_path[-1][1])
                    elif game.is_valid_move(rival_path[0][0] + 1, rival_path[0][1] + 0): 
                        return (rival_path[0][0] + 1, rival_path[0][1])
                    elif game.is_valid_move(rival_path[0][0] - 1, rival_path[0][1] + 0):
                        return (rival_path[0][0] - 1, rival_path[0][1])
                
                # Lógica de flanqueo para jugador 0 (horizontal)
                elif self.player == 0:
                    print("⚔️ [FLANQUEO HORIZONTAL] Intentando rodear última posición rival")
                    if game.is_valid_move(rival_path[-1][0], rival_path[-1][1] + 1): 
                        return (rival_path[-1][0], rival_path[-1][1] + 1)
                    elif game.is_valid_move(rival_path[-1][0], rival_path[-1][1] - 1):
                        return (rival_path[-1][0], rival_path[-1][1] - 1)
                    elif game.is_valid_move(rival_path[0][0], rival_path[0][1] + 1): 
                        return (rival_path[0][0], rival_path[0][1] + 1)
                    elif game.is_valid_move(rival_path[0][0], rival_path[0][1] - 1):
                        return (rival_path[0][0], rival_path[0][1] - 1)
        else:
            self_about_to_win = self.about_to_win(game, 1-rival, self_path)
            if self_about_to_win is not None:
                game.undo_test_move(self_about_to_win[0], self_about_to_win[1])
                print(f"⚔️⚔️ [Victoria garantizada] Movimiento ganador encontrado!")
                return self_about_to_win
            
            about_to_win = self.about_to_win(game, rival, rival_path)
            if about_to_win is not None:
                game.undo_test_move(about_to_win[0], about_to_win[1])
                print(f"🚨🚨 [ALERTA CRÍTICA] Rival a punto de ganar!")
                return about_to_win
            
            if not blocked:
                return self.aggressive_expansion(game, self.player)
            
            two_step_move = self.is_two_step_move(game, rival, rival_path)
            if two_step_move is not None:
                return two_step_move
            
            one_step_move = self.is_one_step_move(game, rival, rival_path)
            if one_step_move is not None:
                return one_step_move
            else:
                return self.annoying_move(game, rival, rival_path)
              
    def annoying_move(self, game, rival, path):
        last_move = game.last_move[rival]
        rival_eff_len, rival_path, best_rival_gap, rival_gaps, blocked = game.longest_virtual_paths[rival]

        if last_move is None:
            print("🎲 [MOV ALEATORIO] Sin último movimiento rival - movimiento aleatorio")
            return game.random_valid_move()

        original_dir = self.get_closest_edge_direction(rival, last_move, game, path)
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

    def last_move_near_main_path(self, game, rival):
            rival_last_move = game.last_move[rival]
            if rival_last_move is None:
                print("🔍 [RIVAL LAST MOVE] Sin último movimiento registrado")
                return False
            
            rival_path = game.longest_virtual_paths[rival][1]
            if not rival_path:
                print("🔍 [RIVAL PATH] El rival no tiene camino principal")
                return False
            
            print(f"🔍 [VERIFICANDO PROXIMIDAD] Último movimiento rival: {rival_last_move}, Camino principal: {rival_path[:3]}...")
            
            # Verificar vecinos directos
            direct_neighbors = game.get_neighbors(rival_last_move)
            for n in direct_neighbors:
                if n in rival_path:
                    print(f"📍 [PROXIMIDAD DETECTADA] Vecino directo {n} está en el camino rival")
                    return True
            
            # Verificar celdas a 1 espacio vacío de distancia
            empty_neighbors = [n for n in direct_neighbors if game.is_valid_move(n[0], n[1])]
            print(f"🔍 [CELDAS VACÍAS CERCANAS] Posibles puentes: {empty_neighbors}")
            
            for empty_n in empty_neighbors:
                secondary_neighbors = game.get_neighbors(empty_n)
                for sn in secondary_neighbors:
                    if sn in rival_path:
                        print(f"📍 [PROXIMIDAD DETECTADA] Celda vacía {empty_n} conecta a {sn} del camino rival")
                        return True
            
            print("🔍 [SIN PROXIMIDAD] Último movimiento rival no está cerca del camino principal")
            return False

    def aggressive_expansion(self, game, player):
        print(f"\n🚀 [EXPANSIÓN AGRESIVA] Jugador {player} buscando expansión...")
        _, path, best_gap, _, _ = game.longest_virtual_paths[player]
        _, _, rival_best_gap, _, _ = game.longest_virtual_paths[1-player]

        if not path:
            print("🚨 [SIN CAMINO] No hay camino virtual - usando movimiento molesto")
            return self.annoying_move(game, 1 - player, game.longest_virtual_paths[1-player][1])
        
        possible_choices = set()
        if best_gap:
            possible_choices.add(best_gap)
        if rival_best_gap:
            possible_choices.add(rival_best_gap)
        
        # Determinar gap objetivo
        target_gap = best_gap if best_gap else None
        target_gap = rival_best_gap if (target_gap is None and rival_best_gap) else None

        if target_gap == best_gap and not rival_best_gap:
            print(f"🎯 [GAP OBJETIVO] Usando mejor gap propio: {target_gap}")
            return target_gap
        elif target_gap == rival_best_gap and not best_gap:
            print(f"🎯 [GAP OBJETIVO] Usando mejor rival: {target_gap}")
            return target_gap
        if len(possible_choices) >= 2:
            self_score = 0
            rival_score = 0
            if best_gap:
                self_score += 8
            rival_neighbors = game.get_neighbors(rival_best_gap)
            for i in range(0, len(rival_neighbors)):
                if rival_neighbors[i] in path:
                    rival_score += 10
            if self_score > rival_score:
                print(f"🎯 [GAP OBJETIVO] Usando mejor gap propio: {target_gap}")
                return best_gap
            else:
                print(f"🎯 [GAP OBJETIVO] Usando mejor rival: {target_gap}")
                return rival_best_gap
        else:
            target_gap = path[-1]
            print(f"🎯 [GAP OBJETIVO] Usando fin del camino: {target_gap}")
            # Calcular dirección ganadora
            direction = self.get_closest_edge_direction(player, target_gap, game, path)
            print(f"🧭 [DIRECCIÓN] Tendiendo hacia {direction} desde {target_gap}")

            # 1. Intentar movimiento principal
            main_move = (target_gap[0] + direction[0], target_gap[1] + direction[1])
            if game.is_valid_move(*main_move):
                print(f"✅ [MOVIMIENTO PRINCIPAL] Avanzando directamente a {main_move}")
                return main_move

            # 2. Generar diagonales estratégicas
            if direction in [(0, 1), (0, -1)]:  # Horizontal
                diagonals = [(-1, direction[1]), (1, direction[1])]
            else:  # Vertical
                diagonals = [(direction[0], 1), (direction[0], -1)]

            print(f"🔀 [DIAGONALES PRINCIPALES] Probando direcciones: {diagonals}")
            for dx, dy in diagonals:
                diag_move = (target_gap[0] + dx, target_gap[1] + dy)
                if game.is_valid_move(*diag_move):
                    print(f"✅ [MOV DIAGONAL PRINCIPAL] Conexión estratégica en {diag_move}")
                    return diag_move
            # 3. Intentar dirección opuesta desde inicio del camino
            opposite_dir = (-direction[0], -direction[1])
            start_pos = path[0]
            opposite_move = (start_pos[0] + opposite_dir[0], start_pos[1] + opposite_dir[1])
            print(f"\n🔄 [DIRECCIÓN OPUESTA] Probando desde inicio {start_pos} hacia {opposite_dir}: {opposite_move}")
            if game.is_valid_move(*opposite_move):
                print(f"✅ [MOV OPUESTO] Expansión contraria en {opposite_move}")
                return opposite_move

            # 4. Diagonales de dirección opuesta
            if opposite_dir in [(0, 1), (0, -1)]:  # Horizontal inverso
                opposite_diagonals = [(-1, opposite_dir[1]), (1, opposite_dir[1])]
            else:  # Vertical inverso
                opposite_diagonals = [(opposite_dir[0], 1), (opposite_dir[0], -1)]

            print(f"🔀 [DIAGONALES OPUESTAS] Explorando direcciones: {opposite_diagonals}")
            for dx, dy in opposite_diagonals:
                diag_move = (start_pos[0] + dx, start_pos[1] + dy)
                if game.is_valid_move(*diag_move):
                    print(f"✅ [MOV DIAGONAL OPUESTO] Conexión estratégica en {diag_move}")
                    return diag_move

            # Fallback final
            print("\n🚨 [EXPANSIÓN FALLIDA] Sin movimientos válidos en ninguna dirección - último recurso")
            return self.annoying_move(game, 1 - player, game.longest_virtual_paths[1-player][1])

    def calculate_virtual_path(self, game, player):
        """Calcula el camino virtual optimizado usando el estado anterior"""
        
        longest_real = self.find_longest_real_path(game, player)
        if not longest_real:
            game.longest_virtual_paths[player] = (0, [], None, [], False)
            self.virtual_paths[player] = {'length': 0, 'path': [], 'gap': None, 'all_gaps': [], 'blocked': False}
            return (0, [], None, [], False)
        
        gaps = self.find_potential_gaps(game, player, longest_real)
        best_gap = self.select_best_gap(longest_real, game, gaps, player)
        max_length = len(longest_real) + 1 if best_gap else len(longest_real)

        if self.longest_real_path_is_blocked(game, player, longest_real):
            game.longest_virtual_paths[player] = (len(longest_real), longest_real, best_gap, gaps, True)
            self.virtual_paths[player] = {'length': len(longest_real), 'path': longest_real, 'gap': best_gap, 'all_gaps': gaps, 'blocked': True}
            return (len(longest_real), longest_real, best_gap, gaps, True)
        
        self.virtual_paths[player] = {
            'length': max_length,
            'path': longest_real + ([best_gap] if best_gap else []),
            'gap': best_gap,
            'all_gaps': gaps
        }
        self.log_virtual_path(player, longest_real, best_gap)
        game.longest_virtual_paths[player] = (max_length, longest_real, best_gap, gaps, False)
        self.virtual_paths[player] = {'length': max_length, 'path': longest_real, 'gap': best_gap, 'all_gaps': gaps, 'blocked': False}
        return (max_length, longest_real, best_gap, gaps, False)

    def find_longest_real_path(self, game, player):
        """Encuentra el camino más largo en dirección ganadora sin ciclos con desempate por avance"""
        max_length = 0
        max_paths = []  # Almacena todos los caminos de máxima longitud
        starts = game.player0_positions if player == 0 else game.player1_positions
        relevant_coord = 1 if player == 0 else 0  # Coordenada relevante para el avance

        if not starts:
            return []

        for start in starts:
            visited = set()
            stack = [(start, [start])]
            
            while stack:
                pos, path = stack.pop()
                
                if pos in visited:
                    continue
                visited.add(pos)

                # Actualizar máximo y caminos
                current_len = len(path)
                if current_len > max_length:
                    # Nuevo máximo, resetear lista
                    max_length = current_len
                    max_paths = [path.copy()]
                elif current_len == max_length:
                    # Misma longitud, agregar a candidatos
                    max_paths.append(path.copy())
                
                # Explorar vecinos
                for neighbor in self.get_directional_neighbors_for_real_path(pos, player, game, path):
                    if game.board[neighbor[0]][neighbor[1]] == player and neighbor not in visited:
                        new_path = path + [neighbor]
                        stack.append((neighbor, new_path))

        # Seleccionar mejor camino entre los de máxima longitud
        if not max_paths:
            return []
        
        if len(max_paths) == 1:
            return max_paths[0]

        # Calcular avance en dirección ganadora para desempate
        def calculate_advance(path):
            unique_relevant = {pos[relevant_coord] for pos in path}
            return len(unique_relevant)

        # Encontrar el camino con máximo avance
        max_advance = -1
        best_path = max_paths[0]
        for path in max_paths:
            advance = calculate_advance(path)
            if advance > max_advance:
                max_advance = advance
                best_path = path

        return best_path

    def select_best_gap(self, path, game, gaps, player):
        """Selecciona el gap con mejor proyección y aplica criterios de desempate"""
        if not gaps:
            return None

        # Paso 1: Calcular scores básicos
        gap_scores = []
        if len(gaps) == 1:
            return gaps[0]
        if len(gaps) == 3:
            breaked = False
            for i in range (0, len(gaps)):
                for j in range (0, len(gaps)):
                    if gaps[i][0] == gaps[j][0] and abs(gaps[i][1] - gaps[j][1]) == 2 or gaps[i][1] == gaps[j][1] and abs(gaps[i][0] - gaps[j][0]) == 2:
                        gaps = [gaps[i], gaps[j]]
                        breaked = True
                        break
                if breaked:
                    break

        if len(gaps) == 2: 
            dir_gap_0 = self.get_closest_edge_direction(player, gaps[0], game, path)
            dir_gap_1 = self.get_closest_edge_direction(player, gaps[1], game, path)
            if player == 0:
                gap_position = "left" if gaps[0][1] <= (game.size-1)//2 else "right"
            else:
                gap_position = "up" if gaps[0][0] <= (game.size-1)//2 else "down"
         
            if dir_gap_0 == dir_gap_1 and ((dir_gap_0 == (0, 1) or dir_gap_0 == (0, -1)) and (gaps[0][0] == gaps[1][0])):
                if gap_position == "right":
                    return gaps[0] if gaps[0][1] > gaps[0][1] else gaps[1]
                else:
                    return gaps[0] if gaps[0][1] < gaps[0][1] else gaps[1]
            elif dir_gap_0 == dir_gap_1 and ((dir_gap_0 == (-1, 0) or dir_gap_0 == (1, 0)) and (gaps[0][1] == gaps[1][1])):
                if dir_gap_0 == (1, 0):
                    return gaps[0] if gaps[0][1] > gaps[0][1] else gaps[1]
                else:
                    return gaps[0] if gaps[0][1] < gaps[0][1] else gaps[1]            
        
        for gap in gaps:
            direction = self.get_closest_edge_direction(player, gap, game, path)
            score = self.evaluate_direction(game, gap, direction, player)
            edge_bonus = self.calculate_edge_bonus(player, gap, game, direction)
            total_score = score + edge_bonus
            gap_scores.append((gap, total_score))
    

        # Paso 2: Ordenar por score
        gap_scores.sort(key=lambda x: (-x[1], -x[0][0] if player == 0 else -x[0][1]))
        
        if self.debug:
            print("\n🔝 Top gaps:")
            for gap, score in gap_scores[:5]:
                print(f"• {gap}: {score}")

        # Paso 3: Filtrar máximos y aplicar desempate
        max_score = gap_scores[0][1]
        candidates = [g for g, s in gap_scores if s == max_score]
        
        if len(candidates) == 1:
            return candidates[0]
        
        # Criterio de desempate: alineación con dirección ganadora
        if self.debug:
            print(f"\n⚖️ Desempate entre {len(candidates)} gaps con score {max_score}")
        
        best_gap = self.break_tie(path, game, player, candidates)
        return best_gap

    def break_tie(self, path, game, player, candidates):
        """Aplica criterio de alineación con camino existente"""
        direction = (0, 1) if player == 0 else (1, 0)  # Dirección ganadora primaria
        scores = []
        
        # Buscar gaps adyacentes al camino en dirección ganadora
        for gap in candidates:
            score = 0
            # Verificar si tiene vecino en dirección ganadora que esté en el camino
            neighbor1 = (gap[0] - direction[0], gap[1] - direction[1])
            neighbor2 = (gap[0] + direction[0], gap[1] + direction[1])
            if neighbor1 in path or neighbor2 in path:
                score += 5
                if self.debug:
                    print(f"  🏆 Gap {gap} conecta con camino en dirección ganadora")
            score += (game.size * 2) // self.min_dist_to_edge(player, gap, game)
            scores.append(score)
        
        # Encontrar el máximo puntaje
        max_score = max(scores)
        
        # Seleccionar el primer candidato con el puntaje máximo
        for i, score in enumerate(scores):
            if score == max_score:
                print(f"  🏆 Gap {candidates[i]} gana con score de {score}")
                return candidates[i]
    
    def longest_real_path_is_blocked(self, game, player, path):
        print(f"🔒 Determinando si el camino del jugador {player} está bloqueado. Camino {path}")
        """Determina si el camino está bloqueado en cualquier dirección crítica"""
        if not path:
            print("🕳️ [CAMINO VACÍO] No hay camino para verificar bloqueos")
            return False

        # Obtener dirección original y opuesta
        original_dir = self.get_closest_edge_direction(player, path[-1], game, path)
        opposite_dir = (-original_dir[0], -original_dir[1])
        enemy = 1 - player

        print(f"🧭 [DIRECCIONES CRÍTICAS] Original: {original_dir} | Opuesta: {opposite_dir}")

        def check_direction(direction):
            """Verifica bloqueos en una dirección específica"""
            end_points = []
            for r, q in path:
                next_r, next_q = r + direction[0], q + direction[1]
                if (next_r, next_q) not in path:  # Solo considerar extremos no conectados
                    end_points.append((r, q))

            if not end_points:
                print(f"⚠️ [SIN EXTREMOS] No hay puntos finales en dirección {direction}")
                return False

            print(f"🔍 [VERIFICANDO BLOQUEO] Dirección {direction} en puntos: {end_points}")

            all_blocked = True
            for r, q in end_points:
                next_r, next_q = r + direction[0], q + direction[1]
                if 0 <= next_r < game.size and 0 <= next_q < game.size:
                    if game.board[next_r][next_q] != enemy:
                        all_blocked = False

            return all_blocked

        # Verificar ambas direcciones
        original_blocked = check_direction(original_dir)
        opposite_blocked = check_direction(opposite_dir)

        print(f"📊 [RESULTADOS BLOQUEO] Original: {original_blocked} | Opuesta: {opposite_blocked}")

        # Considerar bloqueado si alguna dirección crítica está completamente bloqueada
        is_blocked = original_blocked or opposite_blocked
        print(f"🔒 [BLOQUEO TOTAL] {is_blocked}")
        return is_blocked
       
    def get_closest_edge_direction(self, player, gap, game, path):
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
        
    def min_dist_to_edge(self, player, gap, game):
        size = game.size
        q, r = gap
        if player == 0:  # Horizontal: priorizar derecha (objetivo)
            distance_right = (size - 1) - r
            distance_left = r
            return max(min(distance_right, distance_left), 1)
        
        else:  # Vertical: priorizar abajo (objetivo)
            distance_down = (size - 1) - q
            distance_up = q
            return max(min(distance_up, distance_down), 1)

    def evaluate_direction(self, game, gap, direction, player):
        """Evalúa una dirección hasta encontrar obstáculo o borde"""
        score = 0
        current = gap
        enemy = 1 - player
        if player == 0:
            gap_position = "left" if gap[1] <= (game.size-1)//2 else "right"
        else:
            gap_position = "up" if gap[0] <= (game.size-1)//2 else "down"
        
        while True:
            current = (current[0] + direction[0], current[1] + direction[1])
            
            # Salir si se alcanza el borde
            if not (0 <= current[0] < game.size and 0 <= current[1] < game.size):
                score += 2  # Bono por llegar al borde
                break
            
            cell = game.board[current[0]][current[1]]
            
            if cell == player:
                score -= 3  # Conexión directa
                if (0 <= current[0] + direction[0] < game.size and 0 <= current[1] + direction[0] < game.size) and game.board[current[0] + direction[0]][current[1] + direction[1]] == enemy:
                    score -= 12
                break
            elif cell == enemy:
                score -= 2  # Bloqueo severo
                break
            else:
                score += 1  # Espacio libre
                break
        current2 = gap
        while True:
            current2 = (current2[0] - direction[0], current2[1] - direction[1])
            
            # Salir si se alcanza el borde
            if not (0 <= current2[0] < game.size and 0 <= current2[1] < game.size):
                score += 2  # Bono por llegar al borde
                break
            
            cell = game.board[current2[0]][current2[1]]
            
            if cell == player:
                score += 3  # Conexión directa
                break
            elif cell == enemy:
                score -= 2  # Bloqueo severo
                break
            else:
                score += 1  # Espacio libre
                break
        
        if (gap_position == 'left' and direction[1] != -1) :
            score -= gap[1]

        elif (gap_position == 'right' and direction[1] != 1):
            score -= (game.size - 1 - gap[1])

        elif (gap_position == 'up' and direction[0] != -1): 
            score -= gap[1]

        elif (gap_position == 'down' and direction[0] != 1):
            score -= (game.size - 1 - gap[0])
        return score    

    def calculate_edge_bonus(self, player, gap, game, dir):
        """Calcula bono por proximidad al borde objetivo"""
        if player == 0 and dir == (0, 1):  # Horizontal: priorizar derecha
            distance = (game.size - 1) - gap[1]  # Distancia a borde derecho
        elif player == 0 and dir == (0, -1):
            distance = gap[1]
        elif player == 1 and dir == (1, 0):
            distance = (game.size - 1) - gap[0]
        else:
            distance = gap[0]  # Distancia a borde inferior
        distance = max(distance, 1)
        return (game.size*2)//distance   # Máximo bono cuando está pegado al borde

    def log_virtual_path(self, player, real_path, gap):
        if self.debug:
            print(f"\n🔍 [Virtual Path - Jugador {player}]")
            print(f"🏁 Camino real base: {real_path}")
            print(f"📍 Mejor gap: {gap}")
            print(f"🏆 Longitud virtual: {len(real_path) + (1 if gap else 0)}")
    
    def block_initial_rival_path(self, game, rival, rival_path, rival_gaps):
        """Versión corregida con sistema de coordenadas consistente (q=columna, r=fila)"""
        print(f"\n🛡️ [Rival {rival}] Iniciando estrategia de bloqueo dual-direccional...")
        print(f"⚙️ Parámetros iniciales - rival_path: {rival_path}, rival_gaps: {rival_gaps}")
        
        # 1. Obtener posición del rival y validar
        human_move = game.last_move.get(rival)
        if not human_move:
            print("⚠️ No hay último movimiento del rival. Usando aleatorio.")
            return self.random_valid_move(game)
        
        r_rival, q_rival = human_move  # r=fila, q=columna
        print(f"📍 Posición rival - r: {q_rival} (fila), q: {r_rival} (columna)")
        print(f"🎯 Objetivo rival: {'Conectar columnas (horizontal)' if rival == 0 else 'Conectar filas (vertical)'}")
        
        # 2. Generar candidatos según tipo de rival
        candidates = []
        board_mid = (game.size - 1) // 2
        # board_mid = board_mid // 2
        
        if rival == 0:  # Rival horizontal (bloquear expansión de columnas)
            print("\n🔧 Generando candidatos para rival horizontal...")
            if q_rival <= board_mid:
                print("⬅️ Rival en mitad izquierda. Bloqueando hacia la DERECHA (+columnas)")
                target_q = game.size - 1
                # Generar todos los q con 0 y todos los q con game.size - 1
                candidates = [(board_mid, q) for q in range(q_rival + board_mid, target_q - board_mid//4)] + [(board_mid + board_mid//2, q) for q in range(q_rival + board_mid, target_q - board_mid//4)]

            else:
                print("➡️ Rival en mitad derecha. Bloqueando hacia la IZQUIERDA (-columnas)")
                target_q = 0
                # Generar todos los q con 0 y todos los q con game.size - 1
                candidates = [(board_mid, q) for q in range(target_q + board_mid//4, q_rival + 1 - board_mid)] + [(board_mid - board_mid//2, q) for q in range(target_q + board_mid//4, q_rival + 1 - board_mid)]
            
            print(f"🧭 Candidatos generados: {candidates}")
        
        else:  # Rival vertical (bloquear expansión de filas) 
            print("\n🔧 Generando candidatos para rival vertical...")
            if r_rival <= board_mid:
                print("⬆️ Rival en mitad superior. Bloqueando hacia ABAJO (+filas)")
                target_r = game.size-1
                candidates = [(r, board_mid) for r in range(r_rival + board_mid, target_r - board_mid//4)] + [(r, board_mid + board_mid//2) for r in range(r_rival + board_mid, target_r - board_mid//4)]
            else:
                print("⬇️ Rival en mitad inferior. Bloqueando hacia ARRIBA (-filas)")
                target_r = 0
                candidates = [(r, board_mid) for r in range(target_r + board_mid//4, r_rival + 1 - board_mid)] + [(r, board_mid - board_mid//2) for r in range(target_r + board_mid//4, r_rival + 1 - board_mid)]
            
            print(f"🧭 Candidatos generados: {candidates}")
        
        # 3. Filtrar movimientos válidos y estratégicos
        print("\n🔎 Filtrando movimientos válidos...")
        valid_candidates = [pos for pos in candidates if game.is_valid_move(*pos)]
        print(f"✅ Candidatos válidos: {valid_candidates}")
        
        if not valid_candidates:
            print("⚠️ No hay candidatos válidos. Usando aleatorio.")
            return self.random_valid_move(game)
        
        choosen = valid_candidates[random.randint(0, len(valid_candidates) - 1)]
        print(f"🎯 Escogido movimiento a {choosen}")
        return choosen



        self.debug = True  # Activar logs

    def get_directional_neighbors(self, pos, player, game, path):
        """Obtiene vecinos en la dirección ganadora y evita ciclos"""
        r, q = pos
        occupied_spots = set()

        for dir in path:
            if player == 0:
                occupied_spots.add(dir[1])
            else:
                occupied_spots.add(dir[0])

        # Direcciones en la dirección ganadora
        if player == 0:  # Horizontal (Izquierda, Derecha, Abajo-Atras, Arriba-Alante)
            directional_neighbors = [(0, -1), (0, 1), (1, -1), (-1, 1)] # Al reves [(-1, 0), (1, 0), (-1, 1), (0, 1), (1, -1)]
        else:  # Vertical           (Arriba-Directo, Arriba-Alante, Abajo-Directo, Abajo-Atras)
            directional_neighbors = [(-1, 0), (-1, 1), (1, 0), (1, -1) ] # Al reves [(0, -1), (1, -1), (0, 1), (-1, 1) ]

        # Generar vecinos válidos en la dirección ganadora
        neighbors = []
        for dr, dq in directional_neighbors:
            nr = r + dr
            nq = q + dq
            if 0 <= nq < game.size and 0 <= nr < game.size:
                neighbors.append((nr, nq))

        # Filtrar vecinos que formen ciclos o no avancen
        filtered = []
        for n in neighbors:
           
            # 1. Chequear avance en dirección ganadora
            if player == 0 and n[1] == q:  
                continue
            if player == 1 and n[0] == r:  
                continue

            filtered.append(n)

        # Priorizar dirección ganadora y diagonales relacionadas
        if player == 0:  # Horizontal
            filtered.sort(key=lambda x: (-x[0], abs(x[1] - r)))
        else:  # Vertical
            filtered.sort(key=lambda x: (-x[1], abs(x[0] - q)))

        return filtered
    
    def get_best_directional_neighbors(self, pos, player, game, path):
        """Obtiene vecinos en la dirección ganadora y evita ciclos"""
        r, q = pos
        directional_neighbors = [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)] 

        relevant_coord = 1 if player == 0 else 0  # 1=q para jugador 0 (horizontal), 0=r para jugador 1 (vertical)
        occupied = [p[relevant_coord] for p in path]

        # Generar vecinos válidos en la dirección ganadora
        neighbors = []
        for dr, dq in directional_neighbors:
            nr = r + dr
            nq = q + dq
            if 0 <= nq < game.size and 0 <= nr < game.size:
                neighbors.append((nr, nq))

        win_dir_gaps = []
        others = []
        for n in neighbors:   
            # 1. Chequear avance en dirección ganadora
            if player == 0: 
                dir = (0, 1) if n[1] >= (game.size-1)//2 else (0, -1)
                if not game.is_valid_move(n[0], n[1]):
                    continue
                if n[1] in occupied:
                    others.append(n)
                    continue
            if player == 1:   
                dir = (1, 0) if n[1] >= (game.size-1)//2 else (-1, 0)
                if not game.is_valid_move(n[0], n[1]):
                    continue
                if n[0] in occupied:
                    others.append(n)
                    continue

            win_dir_gaps.append(n)
        
        return win_dir_gaps, others

    def get_directional_neighbors_for_real_path(self, pos, player, game, path):
        """Obtiene vecinos en la dirección ganadora y evita ciclos"""
        r, q = pos
        directional_neighbors = [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)] 

        # Generar vecinos válidos en la dirección ganadora
        neighbors = []
        for dr, dq in directional_neighbors:
            nr = r + dr
            nq = q + dq
            if 0 <= nq < game.size and 0 <= nr < game.size:
                neighbors.append((nr, nq))

        return neighbors

    def find_potential_gaps(self, game, player, path):
        """Encuentra gaps adyacentes al camino con potencial de extensión"""
        gaps = set()
        other_gaps = set()
        extremes = set()
        side_way = self.get_side_way_extremes(game, player, path)
        if len(side_way) > 0:
            for pos in side_way:
                extremes.add(pos)
        if len(path) == 1:
            extremes.add(path[0])
        else:
            if player == 0:
                if path[0][1] != 0 and path[0][1] != game.size-1:
                    extremes.add(path[0]) 
                if path[len(path) - 1][1] != 0 and path[len(path) - 1][1] != game.size-1:
                    extremes.add(path[len(path) - 1])
            else:
                if path[0][0] != 0 and path[0][0] != game.size-1:
                    extremes.add(path[0]) 
                if path[len(path) - 1][0] != 0 and path[len(path) - 1][0] != game.size-1:
                    extremes.add(path[len(path) - 1])
        
        most_advanced = self.get_most_advanced_in_main_path(game, player, path, not_extremes=True)
        most_advanced = set(most_advanced)
        extremes = extremes.union(most_advanced)

        for pos in extremes:
            win_dir_gaps, others = self.get_best_directional_neighbors(pos, player, game, path)
            if len(win_dir_gaps) > 0:
                for neighbor in win_dir_gaps:
                    if game.board[neighbor[0]][neighbor[1]] is None:
                        gaps.add(neighbor)
            else:
                for neighbor in others:
                    if game.board[neighbor[0]][neighbor[1]] is None:
                        other_gaps.add(neighbor)

        if len(gaps) > 0:
            return sorted(gaps, key=lambda x: (x[0] if player == 0 else x[1]), reverse=True)
        else:
            return sorted(other_gaps, key=lambda x: (x[0] if player == 0 else x[1]), reverse=True)
    
    def get_side_way_extremes(self, game, player, path):
        """Devuelve una lista de extremos de caminos laterales que se conectan con el camino más largo"""
        path_set = set(path)  # Convertir el camino más largo a un conjunto para búsquedas rápidas
        player_positions = set(game.get_player_positions(player))  # Obtener todas las posiciones del jugador
        lateral_extremes = []
        processed_positions = set()  # Conjunto para rastrear posiciones ya procesadas

        # Remover las posiciones que ya están en el camino más largo
        remaining_positions = player_positions - path_set

        # Buscar caminos laterales que se conecten con el camino más largo
        for pos in remaining_positions:
            if pos in processed_positions:
                continue  # Saltar si la posición ya ha sido procesada

            queue = deque([pos])
            visited = set()

            while queue:
                current_pos = queue.popleft()
                if current_pos in visited:
                    continue
                visited.add(current_pos)

                # Verificar si se conecta con el camino más largo
                if any(neighbor in path_set for neighbor in game.get_neighbors(current_pos)):
                    lateral_extremes.append(pos)  # Agregar el extremo inicial del camino lateral
                    processed_positions.update(visited)  # Marcar todas las posiciones visitadas como procesadas
                    break

                # Agregar vecinos no visitados del jugador a la cola
                for neighbor in game.get_neighbors(current_pos):
                    if neighbor in remaining_positions and neighbor not in visited:
                        queue.append(neighbor)

        return lateral_extremes

    def random_valid_move(self, game):
        """Movimiento aleatorio válido como fallback"""
        print("\n🎲 Generando movimiento aleatorio...")
        empty = game.get_empty_cells()
        if empty:
            chosen = random.choice(empty)
            print(f"🎲 Movimiento aleatorio seleccionado: {chosen}")
            return chosen
        print("💥 ¡No hay movimientos posibles!")
        return None

    def has_winning_chance(self, game, player, path):
        """Determina si el jugador tiene alta probabilidad de ganar"""
        if len(path) < game.size//2:
            return False
        
        # Obtener direcciones críticas
        end_dir = self.get_closest_edge_direction(player, path[-1], game, path)
        start_dir = self.get_closest_edge_direction(player, path[0], game, path)
        
        # Calcular pasos hasta el borde desde ambos extremos
        steps_from_end = self.steps_to_edge(game, path[-1], end_dir)
        steps_from_start = self.steps_to_edge(game, path[0], start_dir)
        
        # Determinar posiciones ganadoras ocupadas
        winning_positions = self.count_winning_positions(game, player, path, end_dir)
        
        print(f"🎯 [ANÁLISIS VICTORIA] Pasos desde fin: {steps_from_end} | Desde inicio: {steps_from_start} | Posiciones clave: {winning_positions}/{game.size}")
        
        # Umbral ajustable para peligro (cuanto menor, más sensible)
        DANGER_STEPS = 3  # Aumentado a 3 para hacerlo evitable
        return (winning_positions > game.size//2 + 1) and \
            (steps_from_end <= DANGER_STEPS or steps_from_start <= DANGER_STEPS)

    def steps_to_edge(self, game, pos, direction):
        """Calcula los pasos necesarios para llegar al borde desde una posición"""
        q, r = pos
        dq, dr = direction
        steps = 0
        
        while 0 <= q < game.size and 0 <= r < game.size:
            q += dq
            r += dr
            steps += 1
        
        return steps - 1  # Restar el último paso que sale del tablero

    def count_winning_positions(self, game, player, path, direction):
        """Cuenta las posiciones estratégicas ocupadas en la dirección ganadora"""
        if player == 0:  # Horizontal
            return len(set(q for _, q in path))
        else:  # Vertical
            return len(set(r for r, _ in path))

    def block_winning_path(self, game, player, path):
        """Intenta bloquear el camino ganador del rival"""

        def calculate_direction_score(base_pos, direction):
            """Calcula el score para una dirección específica"""
            score = 0
            current_pos = base_pos
            for _ in range(game.size):
                current_pos = (current_pos[0] + direction[0], current_pos[1] + direction[1])
                if not game.is_valid_move(*current_pos):
                    break
                if game.board[current_pos[0]][current_pos[1]] == player:
                    score += 1
                    if self.is_connected_to_main_path(game, current_pos, path):
                        score += (game.size-1)//2
            return score
        
        def is_already_blocked(game, pos, path, rival, dir):
            """Determina si una posicion del enemigo ya esta bloqueada y en que posicion esta el que bloquea. None si no hay."""
            for i in range(0, game.size):
                if (0 <= pos[0] + dir[0]*i < game.size and 0 <= pos[1] + dir[1]*i < game.size):
                    if game.board[pos[0] + dir[0]*i][pos[1] + dir[1]*i] == (1 - rival):
                        return (pos[0] + dir[0]*i, pos[1] + dir[1]*i)
                else:
                    break
            return None

        # Obtener todos los extremos críticos
        main_extremes = [path[0], path[-1]]
        lateral_extremes = self.get_side_way_extremes(game, player, path)
        all_extremes = main_extremes + lateral_extremes

        # Encontrar el extremo más peligroso
        most_critical = None
        min_steps = float('inf')
        for extreme in all_extremes:
            dir = self.get_closest_edge_direction(player, extreme, game, path)
            steps = self.steps_to_edge(game, extreme, dir)
            if steps < min_steps:
                most_critical = extreme
                min_steps = steps
                critical_dir = dir

        if not most_critical:
            return self.annoying_move(game, player, path)

        print(f"🎯 [BLOQUEO] Extremo crítico en {most_critical} a {min_steps} pasos del borde")
        
        dir = self.get_closest_edge_direction(player, most_critical, game, path)
        block_pos = is_already_blocked(game, most_critical, path, player, dir)
        if block_pos is not None:
            if dir == (0, 1) or dir == (0, -1):
                score_up = 0
                score_down = 0
                if (0 <= block_pos[0] + 1 < game.size and 0 <= block_pos[1] < game.size) and game.board[block_pos[0] + 1][block_pos[1]] != (1-player) and game.board[block_pos[0] + 1][block_pos[1]] != player:
                    score_up += 1
                    block_down = (block_pos[0] + 1 + (dir[0]*(-1)), block_pos[1] + (dir[1]*(-1)))
                    if (0 <= block_pos[0] + 1 + (dir[0]*(-1)) < game.size and 0 <= block_pos[1] + (dir[1]*(-1)) < game.size) and game.board[block_down[0]][block_down[1]] == player:
                        score_up += 3
                    if (0 <= block_pos[0] + 1 + (dir[0]*(-1)) < game.size and 0 <= block_pos[1] + (dir[1]*(-1)) < game.size) and self.is_connected_to_main_path(game, (block_down[0], block_down[1]), path):
                        score_up += 5
                
                if game.board[block_pos[0] - 1][block_pos[1]] != (1-player) and game.board[block_pos[0] - 1][block_pos[1]] != player:
                    score_down += 1
                    block_up = (block_pos[0] - 1 + (dir[0]*(-1)), block_pos[1] + (dir[1]*(-1)))
                    if (0 <= block_pos[0] - 1 + (dir[0]*(-1)) < game.size and 0 <= block_pos[1] + (dir[1]*(-1)) < game.size) and game.board[block_up[0]][block_up[1]] == player:
                        score_down += 3
                    if (0 <= block_pos[0] - 1 + (dir[0]*(-1)) < game.size and 0 <= block_pos[1] + (dir[1]*(-1)) < game.size) and self.is_connected_to_main_path(game, (block_up[0], block_up[1]), path):
                        score_down += 5
                if score_up > 0 or score_down > 0:
                    return block_up if score_down >= score_up else block_down
                else:
                    return self.annoying_move(game, player, path)
            else:
                score_right = 0
                score_left = 0
                if (0 <= block_pos[0] < game.size and 0 <= block_pos[1] + 1 < game.size) and game.board[block_pos[0]][block_pos[1] + 1] != (1-player) and game.board[block_pos[0]][block_pos[1] + 1] != player:
                    score_right += 1
                    block_up_right = (block_pos[0] + (dir[0]*(-1)), block_pos[1] + 1 + (dir[1]*(-1)))
                    if (0 <= block_pos[0] + (dir[0]*(-1)) < game.size and 0 <= block_pos[1] + 1 + (dir[1]*(-1)) < game.size) and game.board[block_up_right[0]][block_up_right[1]] == player:
                        score_right += 3
                    if (0 <= block_pos[0] + (dir[0]*(-1)) < game.size and 0 <= block_pos[1] + 1 + (dir[1]*(-1)) < game.size) and self.is_connected_to_main_path(game, (block_up_right[0], block_up_right[1]), path):
                        score_right += 5
                
                if (0 <= block_pos[0] < game.size and 0 <= block_pos[1] - 1 < game.size) and game.board[block_pos[0]][block_pos[1] - 1] != (1-player) and game.board[block_pos[0] - 1][block_pos[1]] != player:
                    score_left += 1
                    block_up_left = (block_pos[0] + (dir[0]*(-1)), block_pos[1] - 1 + (dir[1]*(-1)))
                    if (0 <= block_pos[0] + (dir[0]*(-1)) < game.size and 0 <= block_pos[1] - 1 + (dir[1]*(-1)) < game.size) and game.board[block_up_left[0]][block_up_left[1]] == player:
                        score_left += 3
                    if (0 <= block_pos[0] + (dir[0]*(-1)) < game.size and 0 <= block_pos[1] - 1 + (dir[1]*(-1)) < game.size) and self.is_connected_to_main_path(game, (block_up_left[0], block_up_left[1]), path):
                        score_left += 5
                if score_right > 0 or score_left > 0:
                    return block_up_right if score_right >= score_left else block_up_left
                else:
                    return self.annoying_move(game, player, path)

        # Generar movimientos de bloqueo prioritarios
        for i in [1, 2, 3]:
            block_cell = (
                most_critical[0] + critical_dir[0]*i,
                most_critical[1] + critical_dir[1]*i
            )
            if not game.is_valid_move(*block_cell):
                continue
                
            if game.board[block_cell[0]][block_cell[1]] == (1 - player):
                print(f"🔍 [BLOQUEO INTELIGENTE] Analizando entorno de {block_cell}")
                
                # Determinar direcciones a verificar
                if critical_dir in [(0,1), (0,-1)]:  # Horizontal
                    dirs = [(-1,0), (1,0)]  # Arriba y abajo
                else:  # Vertical
                    dirs = [(0,1), (0,-1)]  # Izquierda y derecha
                    
                # Calcular scores para cada dirección
                scores = {}
                for d in dirs:
                    check_pos = (block_cell[0] + d[0], block_cell[1] + d[1])
                    if game.is_valid_move(*check_pos):
                        scores[d] = calculate_direction_score(check_pos, critical_dir)
                
                if scores:
                    best_dir = max(scores, key=scores.get)
                    best_cell = (block_cell[0] + best_dir[0], block_cell[1] + best_dir[1])
                    print(f"⚖️ [MEJOR DIRECCIÓN] {best_dir} con score {scores[best_dir]}")
                    return best_cell
                else:
                    print("⚠️ [SIN DIRECCIONES VÁLIDAS] Usando alternativa")
                    return self.annoying_move(game, player, path)
                    
            elif game.is_valid_move(*block_cell):
                print(f"🛑 [BLOQUEO DIRECTO] En {block_cell}")
                return block_cell

        # Bloqueo de último recurso en conexiones laterales
        print("⚔️ [BLOQUEO PROFUNDO] Buscando conexiones laterales")
        lateral_blocks = self.find_lateral_blocks(game, player, path)
        if lateral_blocks:
            return random.choice(lateral_blocks)
        
        print("⚠️ [BLOQUEO FALLIDO] Usando estrategia alternativa")
        return self.annoying_move(game, player, path)

    def find_lateral_blocks(self, game, player, path):
        """Encuentra bloques en caminos laterales conectados"""
        lateral_blocks = []
        path_set = set(path)
        
        for pos in game.get_player_positions(player):
            if pos not in path_set and any(n in path_set for n in game.get_neighbors(pos)):
                for neighbor in game.get_neighbors(pos):
                    if game.is_valid_move(*neighbor) and neighbor not in path_set:
                        lateral_blocks.append(neighbor)
        
        return lateral_blocks

    def is_connected_to_main_path(self, game, pos, path):
            """Verifica si una posición está conectada al camino principal del rival"""
            return any(neighbor in path for neighbor in game.get_neighbors(pos))

    def about_to_win(self, game, rival, path):
        if rival == 0:
            all_plays = game.player0_positions
        else:
            all_plays = game.player1_positions

        all_neighbors = set()
        for i in range (0, len(all_plays)):
            neighbors = game.get_neighbors(all_plays[i])
            neighbors_set = set(neighbors)
            all_neighbors = all_neighbors.union(neighbors_set)

        for neighbor in all_neighbors:
            if game.place_piece_for_test(neighbor[0], neighbor[1], rival):
                if game.check_win(rival):
                    return (neighbor[0], neighbor[1])     
                game.undo_test_move(neighbor[0], neighbor[1])
        return None
    
    def is_one_step_move(self, game, rival, path):
        last_move = game.last_move[rival]
        if game.step_before_last[rival] is None:
            return None
        move_before_last = game.step_before_last[rival]

        self_neighbors = game.get_neighbors(last_move)
        if move_before_last in self_neighbors:
            return None

        all_neighbors = set()
        for i in range(0, len(self_neighbors)):
            neighbors = game.get_neighbors(self_neighbors[i])
            neighbors_set = set(neighbors)
            all_neighbors = all_neighbors.union(neighbors_set)

        if move_before_last in all_neighbors:
            return self.stop_one_step_move(game, rival, move_before_last, last_move)
        
        for neighbor in all_neighbors:
            if (neighbor[0], neighbor[1]) in path:
                return self.stop_one_step_move(game, rival, (neighbor[0], neighbor[1]), last_move)

        return None
        
    def stop_one_step_move(self, game, rival, step1, step2):
        neighbors_step1 = game.get_neighbors(step1)
        neighbors_step2 = game.get_neighbors(step2)

        for i in range(0, len(neighbors_step1)):
            if neighbors_step1[i] in neighbors_step2 and game.is_valid_move(neighbors_step1[i][0], neighbors_step1[i][1]):
                return neighbors_step1[i]
        return None

    def is_two_step_move(self, game, rival, path):
        last_move = game.last_move[rival]
        
        if game.step_before_last[rival] is None:
            return None
        move_before_last = game.step_before_last[rival]

        self_last_neighbors = game.get_neighbors(last_move)
        self_before_neighbors = game.get_neighbors(move_before_last)
        
        if move_before_last in self_last_neighbors:
            return None

        all_neighbors = set()
        for i in range(0, len(self_last_neighbors)):
            neighbors = game.get_neighbors(self_last_neighbors[i])
            neighbors_set = set(neighbors)
            all_neighbors = all_neighbors.union(neighbors_set)

        if move_before_last in all_neighbors:
            return None
        
        for i in range(0, len(self_before_neighbors)):
            if self_before_neighbors[i] in all_neighbors:
                return self_before_neighbors[i]          

        return None
  
    def get_most_advanced_in_main_path(self, game, player, path, not_extremes=False):
        if not path:
            return []

        size = game.size
        relevant_coord = 1 if player == 0 else 0  # 1=q para jugador 0 (horizontal), 0=r para jugador 1 (vertical)
        opposite_coord = 0 if player == 0 else 1
        
        # Extraer coordenadas relevantes
        relevant_values = [pos[relevant_coord] for pos in path]
        
        # Filtrar extremos si es necesario
        filtered_path = path
        if not_extremes:
            filtered_path = [pos for pos in path 
                            if pos[relevant_coord] not in (0, size-1)]
        
        if not filtered_path:
            return []

        # Obtener valores mínimos y máximos relevantes
        min_rel = min(pos[relevant_coord] for pos in filtered_path)
        max_rel = max(pos[relevant_coord] for pos in filtered_path)
        
        # Separar en grupos por valor relevante
        min_group = [pos for pos in filtered_path if pos[relevant_coord] == min_rel]
        max_group = [pos for pos in filtered_path if pos[relevant_coord] == max_rel]
        
        # Función para encontrar extremos en coordenada opuesta
        def get_extremes(group):
            if not group:
                return []
            opposites = [pos[opposite_coord] for pos in group]
            min_opp = min(opposites)
            max_opp = max(opposites)
            return [pos for pos in group if pos[opposite_coord] in (min_opp, max_opp)]
        
        # Obtener posiciones extremas
        candidates = []
        candidates.extend(get_extremes(min_group))
        candidates.extend(get_extremes(max_group))
        
        # Eliminar duplicados y ordenar
        unique_candidates = list({(pos[0], pos[1]): pos for pos in candidates}.values())
        
        # Priorizar hasta 4 posiciones únicas
        if len(unique_candidates) <= 4:
            return sorted(unique_candidates, key=lambda x: (x[relevant_coord], x[opposite_coord]))
        
        # Seleccionar los 4 más representativos
        return sorted(unique_candidates, 
                    key=lambda x: (x[relevant_coord], -x[opposite_coord]))[:4]




