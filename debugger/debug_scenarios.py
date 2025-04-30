from game.game_logic import HexGame
from game.configs import AI_REGISTRY  # Importamos los tipos de IA disponibles

def print_board(game):
    """
    Imprime el tablero de Hex en formato legible con coordenadas.
    
    Args:
        game (HexGame): Instancia del juego Hex con el tablero a imprimir.
        
    El tablero se imprime con:
    - Números de columna en la parte superior
    - Cada fila desplazada diagonalmente para mejor visualización
    - Números de fila al inicio y final de cada línea
    - 'X' para jugador 0, 'O' para jugador 1, '.' para casillas vacías
    """
    size = len(game.board)
    print("\nTablero actual:")

    # Imprimir números de columna
    print("   " + " ".join(f"{col:2}" for col in range(size)))

    for i, row in enumerate(game.board):
        # Crear representación de fila con espacios para efecto diagonal
        row_str = " " * i + " ".join(["X" if cell == 0 else "O" if cell == 1 else "." for cell in row])
        # Imprimir número de fila al inicio y final
        print(f"{i:2} {row_str} {i}")

def create_custom_board(size=11, players_moves=None, last_moves=None, step_before_last=None):
    """
    Crea un tablero personalizado con movimientos específicos para cada jugador.
    
    Args:
        size (int): Tamaño del tablero (default 11)
        players_moves (list): Lista de tuplas (player_id, moves_list) donde:
            - player_id: 0 o 1 (jugador)
            - moves_list: Lista de tuplas (row, col) con movimientos del jugador
        last_moves (dict): Diccionario con {player_id: (row, col)} del último movimiento
        step_before_last (dict): Diccionario con {player_id: (row, col)} del penúltimo movimiento
    
    Returns:
        HexGame: Instancia del juego con el tablero configurado
    """
    game = HexGame(size, "CUSTOM", ["Human", "AI"])
    
    # Aplicar movimientos de cada jugador
    if players_moves:
        for player_id, moves in players_moves:
            for row, col in moves:
                game.place_piece(row, col, player_id)
                game.check_win(player_id)
    
    # Configurar últimos movimientos si se especifican
    if last_moves:
        for player_id, move in last_moves.items():
            game.last_move[player_id] = move
    
    # Configurar penúltimos movimientos si se especifican
    if step_before_last:
        for player_id, move in step_before_last.items():
            game.step_before_last[player_id] = move
    
    return game

def setup_debug_examples(debug_type="empty", size=11):
    """
    Crea un tablero con configuraciones predefinidas para testing.
    
    Args:
        debug_type (str): Tipo de configuración predefinida. Opciones:
            - "empty": Tablero vacío
            - "single_piece": Un solo movimiento del jugador 0
            - "rival_virtual_3": Jugador 0 con camino virtual de 3
            - "own_virtual_4": Jugador 1 con camino virtual de 4
            - "complex_scenario": Escenario complejo con múltiples movimientos
            - "new_scenario": Escenario con caminos diagonales
            - "another_one": Escenario con pocos movimientos
            - "new1": Escenario con múltiples movimientos
            - "new2": Escenario con fila completa de un jugador
        size (int): Tamaño del tablero (default 11)
    
    Returns:
        HexGame: Instancia del juego con el tablero configurado
    """
    # Usamos la nueva función genérica para los casos predefinidos
    if debug_type == "empty":
        return create_custom_board(size)
    
    elif debug_type == "single_piece":
        return create_custom_board(size, [(0, [(2, 2)])])
    
    elif debug_type == "rival_virtual_3":
        return create_custom_board(
            size,
            players_moves=[
                (0, [(2, 1), (2, 2), (2, 3)]),  # Jugador 0
                (1, [(4, 4)])],                   # Jugador 1
            last_moves={0: (3, 2)}
        )
    
    elif debug_type == "own_virtual_4":
        return create_custom_board(
            size,
            players_moves=[
                (1, [(0, 2), (1, 2), (2, 2), (3, 2)]),  # Jugador 1
                (0, [(0, 0)])],                          # Jugador 0
            last_moves={1: (2, 3)}
        )
    
    elif debug_type == "complex_scenario":
        moves = [
            (4, 2, 0), (4, 3, 0), (4, 4, 0), (4, 5, 0), (4, 6, 0), (3, 7, 0), (3, 8, 0), (3, 9, 0),
            (5, 6, 0), (6, 6, 0), (7, 6, 0), (8, 6, 0), (9, 6, 0), (5, 7, 1), (0, 0, 1), (1, 0, 1)
        ]
        return create_custom_board(
            size,
            players_moves=[
                (0, [(r, q) for r, q, p in moves if p == 0]),
                (1, [(r, q) for r, q, p in moves if p == 1])
            ],
            last_moves={0: (9, 6), 1: (5, 7)}
        )
    
    elif debug_type == "new_scenario":
        moves = [
            (4, 3, 0), (5, 3, 0), (6, 3, 0), (7, 3, 0), (7, 4, 0), (6, 5, 0), (5, 6, 0), (4, 7, 0), (4, 8, 0), (3, 9, 0),
            (4, 2, 1), (4, 4, 1), (3, 4, 1), (5, 4, 1), (6, 4, 1), (7, 5, 1), (6, 6, 1), (5, 7, 1), (4, 9, 1)
        ]
        return create_custom_board(
            size,
            players_moves=[
                (0, [(r, q) for r, q, p in moves if p == 0]),
                (1, [(r, q) for r, q, p in moves if p == 1])
            ],
            last_moves={0: (1, 7), 1: (7, 5)}
        )
    
    elif debug_type == "another_one":
        moves = [
            (3, 3, 0), (4, 3, 0), (4, 4, 0), (8, 0, 0),
            (1, 0, 1), (3, 4, 1), (5, 2, 1)
        ]
        return create_custom_board(
            size,
            players_moves=[
                (0, [(r, q) for r, q, p in moves if p == 0]),
                (1, [(r, q) for r, q, p in moves if p == 1])
            ],
            last_moves={0: (8, 0), 1: (5, 2)}
        )
    
    elif debug_type == "new1":
        moves = [
            (3, 4, 0), (4, 6, 0), (5, 5, 0), (6, 3, 0), (6, 5, 0), (2, 6, 0), (2, 7, 0), (2, 8, 0), (1, 8, 0), (0, 9, 0), (3, 0, 0), (3, 1, 0), (3, 2, 0), (3, 3, 0),
            (3, 5, 1), (3, 6, 1), (3, 7, 1), (4, 5, 1), (5, 4, 1), (6, 4, 1), (7, 4, 1)
        ]
        return create_custom_board(
            size,
            players_moves=[
                (0, [(r, q) for r, q, p in moves if p == 0]),
                (1, [(r, q) for r, q, p in moves if p == 1])
            ],
            last_moves={0: (0, 10), 1: (7, 4)},
            step_before_last={0: (3, 3), 1: (6, 4)}
        )
    
    elif debug_type == "new2":
        moves = [
            (0, 0, 0), (0, 1, 0), (0, 2, 0), (0, 3, 0), (0, 4, 0), (0, 5, 0), (0, 6, 0), (0, 7, 0), (0, 8, 0), (0, 9, 0),
            (2, 3, 1), (2, 4, 1)
        ]
        return create_custom_board(
            size,
            players_moves=[
                (0, [(r, q) for r, q, p in moves if p == 0]),
                (1, [(r, q) for r, q, p in moves if p == 1])
            ],
            last_moves={0: (0, 9), 1: (2, 4)},
            step_before_last={0: (0, 8), 1: (2, 3)}
        )
    
    else:
        raise ValueError(f"Tipo de debug no reconocido: {debug_type}")

def test_ai_decisions(ai_player=1, test_cases=None, ai_class=AI_REGISTRY[0]):
    """
    Ejecuta pruebas de decisión de IA con diferentes configuraciones de tablero.
    
    Args:
        ai_player (int): 0 o 1, indica qué jugador controla la IA
        test_cases (list): Lista de tuplas (debug_type, description) a probar.
                          Si es None, usa los casos por defecto.
        ai_class (class): Clase de IA a utilizar (default primer AI registrada en AI_REGISTRY de game/configs.py)
    """
    # Configurar IA
    ai = ai_class(ai_player)
    ai.debug = True  # Activar logs detallados
    
    # Casos de prueba por defecto si no se especifican
    if test_cases is None:
        test_cases = [
            ("empty", "Tablero vacío"),
            ("single_piece", "Solo una pieza rival"),
            ("rival_virtual_3", "Camino virtual rival tamaño 3"),
            ("own_virtual_4", "Camino virtual propio tamaño 4"),
            ("complex_scenario", "Escenario complejo del log"),
            ("new_scenario", "Nuevo escenario con camino del jugador 0 y posiciones de IA"),
            ("another_one", "Ver index out of range cases"),
            ("new1", "Escenario con múltiples movimientos"),
            ("new2", "Escenario con fila completa de un jugador")
        ]

    for case, description in test_cases:
        print(f"\n{'='*50}")
        print(f"🏁 Caso de prueba: {description}")
        game = setup_debug_examples(case)
        print_board(game)
        
        # Reiniciar caminos virtuales de la IA
        ai.virtual_paths = {
            0: {'length': 0, 'path': [], 'gap': None},
            1: {'length': 0, 'path': [], 'gap': None}
        }
        
        # Obtener mejor movimiento
        print("\n🤖 Procesando decisión de IA...")
        move = ai.get_best_move(game)

        print(f"✅ Movimiento seleccionado: {move}")

if __name__ == "__main__":
    # Ejemplo de uso con configuración personalizada
    custom_test = [
        ("empty", "Tablero vacío personalizado"),
        ("single_piece", "Pieza única personalizada")
    ]
    
    # Ejecutar con configuración por defecto
    test_ai_decisions()
    
    # Ejemplo de ejecución con parámetros personalizados:
    # test_ai_decisions(
    #     ai_player=0,  # La IA será el jugador 0
    #     test_cases=custom_test,
    #     ai_class=MasterAI  # Usar otra IA
    # )