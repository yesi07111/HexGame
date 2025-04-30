import sys
import time
import pygame
import random
import threading

from game.ui import *
from game.configs import *
from game.game_logic import HexGame
from records.rec import GameRecords

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Hex Game - IA Project")
    clock = pygame.time.Clock()
    RECORDS = GameRecords()
    HUMAN_PLAYER = None

    def create_buttons():
        return [
            Button(WIDTH - 180, 20, 160, 30, "Menú Principal", "MENU"),
            Button(WIDTH - 180, 60, 160, 30, "Salir", "EXIT")
        ]

    in_menu = True
    game = None
    
    while True:
        if in_menu:
            try:
                game_mode, players = show_menu(screen)
                ia_config = None
                
                # Modificar esta sección para manejar todos los modos
                if game_mode == "PVAI":
                    ia_config = show_ia_config(screen)
                elif game_mode == "AIVAI":
                    ia_config = show_ai_vs_ai_config(screen)  # Nueva función
                    
                if ia_config is None:  # Si se cancela cualquier configuración
                    in_menu = True
                    continue
                
                print(f"\n\n--- NUEVO JUEGO ---")
                print(f"Modo: {game_mode}")
                print(f"Jugadores: {players.names}")
                print(f"Colores: {[COLOR_NAMES[c] for c in players.colors]}")
                game = HexGame(GRID_SIZE, game_mode, players)

                # Configuración para todos los modos
                if game_mode == "PVAI":
                    # Modificar para usar nombre de IA seleccionada
                    order_option = ia_config['order']
                    ai_class = AI_REGISTRY[ia_config['ia_type']]  # Obtener clase de IA
                    
                    ai_player = 1 if order_option == 0 else 0
                    human_player = 1 - ai_player
                    HUMAN_PLAYER = human_player
                    
                    game.players.names[ai_player] = ai_class.NAME  # Usar nombre de la clase
                    game.ai = ai_class(ai_player)  # Crear instancia
                    game.current_player = human_player if order_option == 0 else ai_player
                    
                elif game_mode == "AIVAI":
                    # Configurar ambas IAs
                    game.ai = ia_config['ai_p1'](1)  # IA para jugador 1
                    game.ai2 = ia_config['ai_p0'](0)  # IA para jugador 0
                    
                    # Actualizar nombres
                    game.players.names[0] = ia_config['ai_p0'].NAME
                    game.players.names[1] = ia_config['ai_p1'].NAME
                    game.current_player = 0  # Empezar con jugador 0
                    HUMAN_PLAYER = -1  # Ningún jugador humano
                
                in_menu = False
            except Exception as e:
                print(f"Error: {str(e)}")
                pygame.quit()
                sys.exit()

        mouse_pos = pygame.mouse.get_pos()
        buttons = create_buttons()
        
        # --- Manejo de eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Manejar botones UI
            for btn in buttons:
                action = btn.handle_click(event)
                if action == "MENU":
                    if confirm_dialog(screen, "¿Perderás el progreso actual?"):
                        in_menu = True
                        game = None
                elif action == "EXIT":
                    if confirm_dialog(screen, "¿Seguro que quieres salir?"):
                        pygame.quit()
                        sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    if confirm_dialog(screen, "¿Volver al menú principal?"):
                        in_menu = True
                        game = None
                    
            # Manejar clics humanos SOLO en modos PVP y PVAI
            if game and not game.winner and game.game_mode in ["PVP", "PVAI"] and HUMAN_PLAYER == game.current_player:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Verificar si es turno humano
                    if game.players.names[game.current_player] != "Mr. Tie":
                        x, y = event.pos
                        r, q = pixel_to_axial(x, y, HEX_RADIUS)
                        
                        if 0 <= q < GRID_SIZE and 0 <= r < GRID_SIZE and game.is_valid_move(r, q):
                            print(f"✅ Ficha colocada exitosamente en ({r}, {q})")
                            if game.place_piece(r, q, game.current_player):
                                game.check_win(game.current_player)
                                
                                if game.winner is None:
                                    # Cambiar turno solo si es humano
                                    game.ai_thinking = False
                                    game.current_player = 1 - game.current_player
                                    print(f"🔄 Turno de: {game.players.names[game.current_player]}")
                                else:
                                    print("🎉 ¡Jugador humano gana!")
                            else:
                                print("❌ Movimiento inválido")

        # --- Lógica IA ---
        # Dentro de la sección de lógica IA:
        if game and not game.winner and game.game_mode in ["PVAI", "AIVAI"] and (HUMAN_PLAYER != game.current_player or game.game_mode == "AIVAI"):
            # Determinar IA actual CORREGIDO
            current_ai = None
            if game.game_mode == "PVAI":
                current_ai = game.ai
            # En la sección de lógica IA:
            elif game.game_mode == "AIVAI":
                current_ai = game.ai2 if game.current_player == 0 else game.ai

            if current_ai and game.ai_thinking == False:
                # Iniciar proceso de pensamiento IA
                game.ai_thinking = True
                game.current_ia_message = IA_MESSAGES[0]
                game.message_index = 0
                game.last_message_update = time.time()
                game.ai_target = None
                
                # Crear copia segura del estado del juego
                game_copy = game.copy()
                
                def calculate_move():
                    game.ai_target = current_ai.get_best_move(game_copy)
                    try:    
                        # Verificar validez del movimiento
                        if not game_copy.is_valid_move(*game.ai_target):
                            print(f"🤖 [IA - {game.ai.NAME}] ¡Movimiento inválido! ({game.ai_target[0]}, {game.ai_target[1]}) Escogiendo otro movimiento.")
                            try:
                                game.ai_target = game.ai.annoying_move(game, 1 - game.current_player, game.longest_virtual_paths[game.current_player][1])
                                print(f"🤖 [IA - {game.ai.NAME}] Escogido movimiento molesto ({game.ai_target[0]}, {game.ai_target[1]}).")
                            except:
                                game.ai_target = game.random_valid_move()
                                print(f"🤖 [IA - {game.ai.NAME}] Escogido aleatorio: ({game.ai_target[0]}, {game.ai_target[1]}).")
                            
                    except Exception as e:
                        print(f"🤖 [IA - {game.ai.NAME}] ❌ Error: {str(e)}")
                        try:
                            game.ai_target = game.ai.annoying_move(game, 1 - game.current_player, game.longest_virtual_paths[game.current_player][1])
                            print(f"🤖 [IA - {game.ai.NAME}] Escogido movimiento molesto ({game.ai_target[0]}, {game.ai_target[1]}).")
                        except:
                            game.ai_target = game.random_valid_move()
                            print(f"🤖 [IA - {game.ai.NAME}] Escogido aleatorio: ({game.ai_target[0]}, {game.ai_target[1]}).")
                                              
                    game.ai_thinking = None
                    game.ai_animating = True
                    game.ai_progress = 0
                    game.ai_start_pos = pygame.mouse.get_pos()
                
                game.ai_thread = threading.Thread(target=calculate_move, daemon=True)
                game.ai_thread.start()
            
            elif game.ai_thinking:
                # Actualizar mensaje cada 3 segundos
                current_time = time.time()
                if current_time - game.last_message_update > 3:
                    game.message_index = random.randint(0, len(IA_MESSAGES) - 1)
                    game.current_ia_message = IA_MESSAGES[game.message_index]
                    game.last_message_update = current_time

        # --- Animación IA ---
        if game and hasattr(game, 'ai_animating') and game.ai_animating:
            if game.ai_progress < AI_ANIMATION_STEPS:
                if game.ai_target is None:
                    game.ai_target = game.random_valid_move()
                    print(f"❌ Error IA: Movimiento inválido asi que escogiendo random en {game.ai_target}")
                target_x, target_y = axial_to_pixel(*game.ai_target, HEX_RADIUS)
                
                # Configurar velocidad diferente para AIVAI
                if game.game_mode == "AIVAI":
                    animation_steps = AI_ANIMATION_STEPS * 1.2  # 3 veces más lento
                    progress = game.ai_progress / animation_steps
                else:
                    progress = game.ai_progress / AI_ANIMATION_STEPS
                    
                current_x = game.ai_start_pos[0] + (target_x - game.ai_start_pos[0]) * progress
                current_y = game.ai_start_pos[1] + (target_y - game.ai_start_pos[1]) * progress
                
                # Solo mover mouse en modos no AIVAI
                if game.game_mode != "AIVAI":
                    pygame.mouse.set_pos((int(current_x), int(current_y)))
                
                game.ai_progress += 1
            else:
                # Dentro del bloque de animación IA:
                if game.is_valid_move(*game.ai_target):
                    print(f"✅ {game.players.names[game.current_player]} colocó ficha en {game.ai_target}")
                    if game.place_piece(*game.ai_target, game.current_player):
                        game.check_win(game.current_player)
                        
                        if game.winner is None:
                            game.current_player = 1 - game.current_player
                            print(f"🔄 Turno de {game.players.names[game.current_player]}")
                            if game.game_mode == "AIVAI":
                                game.ai_thinking = False
                        else:
                            print(f"🎉 ¡{game.players.names[game.current_player]} gana!")
                    else:
                        print("❌ Error IA: Movimiento inválido")
                
                # Resetear estado IA
                if game.game_mode == "AIVAI":
                    game.ai_thinking = False
                del game.ai_animating
                del game.ai_target
                del game.ai_progress
                del game.ai_start_pos

        # --- Dibujado ---
        screen.fill(BG_COLOR)
        if game:
            draw_board(screen, game, HEX_RADIUS)
            
            # UI
            for btn in buttons:
                btn.draw(screen)
            
            # Estado del juego
            if not game.winner:
                font = pygame.font.SysFont('Arial', 24)
                # Mostrar mensaje IA si está pensando
                if game.ai_thinking:
                    text = font.render(game.current_ia_message, True, COLORS[game.players.colors[1]])
                    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 50))
                # Mostrar turno actual
                turn_text = f"Turno: {game.players.names[game.current_player]}"
                text_color = COLORS[game.players.colors[game.current_player]]
                screen.blit(font.render(turn_text, True, text_color), (20, 20))

            # Manejar victoria
            if game.winner is not None:
                winner_name = game.players.names[game.winner]
                RECORDS.save_record(winner_name, game.players.names[1 - game.winner])
                result = show_result(screen, winner_name, COLORS[game.players.colors[game.winner]])
                
                if result == 'retry':
                    game = HexGame(GRID_SIZE, game_mode, game.players)
                elif result == 'menu':
                    in_menu = True
                elif result == 'exit':
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()