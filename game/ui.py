import math
import sys
import pygame
from game.configs import *

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = BUTTON_COLOR
        self.hover = False

    def update_hover(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)
        self.color = BUTTON_HOVER_COLOR if self.hover else BUTTON_COLOR

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
        font = pygame.font.SysFont('Arial', 24)
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):  # Verificación directa
                return self.action
        return None
    
class Dropdown:
    def __init__(self, x, y, width, height, options, other_dropdown=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options  # Lista de índices de colores
        self.selected = 0
        self.active = False
        self.other = other_dropdown
        self.available = options.copy()

    def update_available(self):
        if self.other:
            self.available = [
                c for c in self.options 
                if c != self.other.selected and c not in [self.other.selected]
            ]

    def draw(self, screen):
        # Botón principal
        pygame.draw.rect(screen, COLORS[self.selected], self.rect, border_radius=5)
        font = pygame.font.SysFont('Arial', 24)
        text = font.render(COLOR_NAMES[self.selected], True, (255,255,255))
        screen.blit(text, (self.rect.x + 10, self.rect.centery - 12))
        
        # Opciones
        if self.active:
            y = self.rect.bottom
            for color_idx in self.available:
                rect = pygame.Rect(self.rect.x, y, self.rect.width, 30)
                pygame.draw.rect(screen, COLORS[color_idx], rect)
                text = font.render(COLOR_NAMES[color_idx], True, (255,255,255))
                screen.blit(text, (rect.x + 10, rect.centery - 10))
                y += 30

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.active:
                # Manejar clic dentro de las opciones
                rel_y = event.pos[1] - self.rect.bottom
                idx = rel_y // 30
                if 0 <= idx < len(self.available):
                    self.selected = self.available[idx]
                    self.active = False
                    return True
            elif self.rect.collidepoint(event.pos):
                self.active = not self.active
                return True  # Indicar que se manejó el evento
        return False

class TextInput:
    def __init__(self, x, y, width, height, default_text=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = default_text
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def draw(self, screen):
        color = (255, 255, 255) if self.active else (200, 200, 200)
        pygame.draw.rect(screen, color, self.rect, 2, border_radius=5)
        
        font = pygame.font.SysFont('Arial', 24)
        text_surf = font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surf, (self.rect.x + 10, self.rect.centery - 12))
        
        # Dibujar cursor
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 10 + text_surf.get_width()
            pygame.draw.line(screen, (255, 255, 255), 
                           (cursor_x, self.rect.y + 5),
                           (cursor_x, self.rect.bottom - 5), 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        
        if self.active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.cursor_visible = True
                self.cursor_timer = 0
            
            # Actualizar parpadeo del cursor
            if event.type == pygame.USEREVENT + 1:
                self.cursor_timer = (self.cursor_timer + 1) % 30
                self.cursor_visible = self.cursor_timer < 15

class TextDropdown:
    def __init__(self, x, y, width, height, options):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected = 0
        self.active = False

    def draw(self, screen):
        # Botón principal
        pygame.draw.rect(screen, (255, 255, 255), self.rect, border_radius=5)
        font = pygame.font.SysFont('Arial', 24)
        text = font.render(self.options[self.selected], True, (0, 0, 0))
        screen.blit(text, (self.rect.x + 10, self.rect.centery - 12))
        
        # Opciones
        if self.active:
            y = self.rect.bottom
            for idx, option in enumerate(self.options):
                rect = pygame.Rect(self.rect.x, y, self.rect.width, 30)
                pygame.draw.rect(screen, (200, 200, 200), rect)
                text = font.render(option, True, (0, 0, 0))
                screen.blit(text, (rect.x + 10, rect.centery - 10))
                y += 30

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.active:
                rel_y = event.pos[1] - self.rect.bottom
                idx = rel_y // 30
                if 0 <= idx < len(self.options):
                    self.selected = idx
                    self.active = False
                    return True
            elif self.rect.collidepoint(event.pos):
                self.active = not self.active
                return True
        return False

# Función de conversión de coordenadas 
def axial_to_pixel(r, q, radius):
    screen_width, screen_height = pygame.display.get_surface().get_size()
    x = radius * (3**0.5) * (q + r/2) + MARGIN_LEFT
    y = radius * 1.5 * r + (screen_height - (GRID_SIZE * radius * 1.5)) / 2
    return (x, y)

def pixel_to_axial(x, y, radius):
    screen_width, screen_height = pygame.display.get_surface().get_size()
    x -= MARGIN_LEFT
    y -= (screen_height - (GRID_SIZE * radius * 1.5)) / 2
    r = (x * (3**0.5/3) - (y / 3)) / radius
    q = (y * 2/3) / radius
    # Asegurar que está dentro del tablero
    q = max(0, min(GRID_SIZE-1, round(q)))
    r = max(0, min(GRID_SIZE-1, round(r)))
    return int(round(q)), int(round(r)) 

def show_ia_config(screen):
    screen_rect = screen.get_rect()
    left_x = screen_rect.centerx - 350
    right_x = screen_rect.centerx + 50
    y_start = 200
    
    play_order_options = ["Jugar primero", "Jugar segundo"]
    ia_options = [ia.NAME for ia in AI_REGISTRY]  # Nombres de todas las IAs
        
    # Dropdowns y labels
    dropdown_order = TextDropdown(left_x, y_start + 40, 300, 40, play_order_options)
    dropdown_ia = TextDropdown(right_x, y_start + 40, 300, 40, ia_options)
    
    continuar_btn = Button(screen_rect.centerx - 100, 400, 200, 50, "Continuar", "CONTINUAR")
    volver_btn = Button(screen_rect.centerx - 100, 470, 200, 50, "Volver al menú", "VOLVER")

    while True:
        mouse_pos = pygame.mouse.get_pos()
        continuar_btn.update_hover(mouse_pos)
        volver_btn.update_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            handled = dropdown_order.handle_event(event) or dropdown_ia.handle_event(event)
            
            action = continuar_btn.handle_click(event)
            if action == "CONTINUAR":
                return {
                    'order': dropdown_order.selected,
                    'ia_type': dropdown_ia.selected
                }
            
            action = volver_btn.handle_click(event)
            if action == "VOLVER":
                return None

        # Dibujado
        screen.fill(BG_COLOR)
        
        # Título
        title_font = pygame.font.SysFont('Arial', 48, bold=True)
        title_surf = title_font.render("Configuración vs IA", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(screen_rect.centerx, 100))
        screen.blit(title_surf, title_rect)

        # Etiquetas
        font = pygame.font.SysFont('Arial', 24)
        # Orden de juego (izquierda)
        label_order = font.render("Orden de Juego:", True, (255, 255, 255))
        screen.blit(label_order, (left_x, y_start))
        
        # Seleccionar oponente (derecha)
        label_ia = font.render("Seleccionar Oponente:", True, (255, 255, 255))
        screen.blit(label_ia, (right_x, y_start))

        dropdown_order.draw(screen)
        dropdown_ia.draw(screen)
        continuar_btn.draw(screen)
        volver_btn.draw(screen)

        pygame.display.flip()

def show_ai_vs_ai_config(screen):    
    screen_rect = screen.get_rect()
    y_start = 200
    dropdown_width = 300
    
    # Posicionar dropdowns
    left_x = screen_rect.centerx - 350
    right_x = screen_rect.centerx + 50
    
    # Obtener nombres de IAs
    ai_options = [ai.NAME for ai in AI_REGISTRY]
    
    # Crear componentes
    dropdown_p0 = TextDropdown(left_x, y_start + 40, dropdown_width, 40, ai_options)
    dropdown_p1 = TextDropdown(right_x, y_start + 40, dropdown_width, 40, ai_options)
    
    continuar_btn = Button(screen_rect.centerx - 100, 400, 200, 50, "Continuar", "CONTINUAR")
    volver_btn = Button(screen_rect.centerx - 100, 470, 200, 50, "Volver", "VOLVER")

    while True:
        mouse_pos = pygame.mouse.get_pos()
        continuar_btn.update_hover(mouse_pos)
        volver_btn.update_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Manejar dropdowns
            handled = dropdown_p0.handle_event(event) or dropdown_p1.handle_event(event)
            
            # Manejar botones
            action = continuar_btn.handle_click(event) or volver_btn.handle_click(event)
            if action == "CONTINUAR":
                return {
                    'ai_p0': AI_REGISTRY[dropdown_p0.selected],
                    'ai_p1': AI_REGISTRY[dropdown_p1.selected]
                }
            elif action == "VOLVER":
                return None

        # Dibujar
        screen.fill(BG_COLOR)
        
        # Título
        title_font = pygame.font.SysFont('Arial', 48, bold=True)
        title = title_font.render("Configuración IA vs IA", True, (255,255,255))
        screen.blit(title, (screen_rect.centerx - title.get_width()//2, 100))
        
        # Etiquetas
        font = pygame.font.SysFont('Arial', 24)
        screen.blit(font.render("IA Jugador 0:", True, (255,255,255)), (left_x, y_start))
        screen.blit(font.render("IA Jugador 1:", True, (255,255,255)), (right_x, y_start))
        
        dropdown_p0.draw(screen)
        dropdown_p1.draw(screen)
        continuar_btn.draw(screen)
        volver_btn.draw(screen)
        
        pygame.display.flip()

def draw_board(screen, game, radius):
    screen.fill(BG_COLOR)
    
    # Dibujar hexágonos base
    for q in range(GRID_SIZE):
        for r in range(GRID_SIZE):
            x, y = axial_to_pixel(q, r, radius)
            color = (50, 50, 50) if game.board[q][r] is None else COLORS[game.players.colors[game.board[q][r]]]           
            points = []
            for i in range(6):
                angle_deg = 60 * i + 30
                angle_rad = math.radians(angle_deg)
                px = x + radius * math.cos(angle_rad)
                py = y + radius * math.sin(angle_rad)
                points.append((px, py))
            
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, (200, 200, 200), points, 2)

    # Dibujar hover effect completo 
    if not game.winner:
        mouse_pos = pygame.mouse.get_pos()
        q, r = pixel_to_axial(*mouse_pos, radius)
        if 0 <= q < GRID_SIZE and 0 <= r < GRID_SIZE and game.board[q][r] is None:
            x, y = axial_to_pixel(q, r, radius)
            
            hover_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            points = []
            for i in range(6):
                angle_deg = 60 * i + 30
                angle_rad = math.radians(angle_deg)
                px = radius + radius * math.cos(angle_rad)
                py = radius + radius * math.sin(angle_rad)
                points.append((px, py))
            
            pygame.draw.polygon(hover_surface, HOVER_COLOR, points)
            screen.blit(hover_surface, (x - radius, y - radius))

    # Dibujar camino ganador
    if game.winner and game.winning_path:
        path_points = [axial_to_pixel(q, r, radius) for q, r in game.winning_path]
        if len(path_points) >= 2:
            pygame.draw.lines(screen, (255, 215, 0), False, path_points, 5)

def confirm_dialog(screen, message):
    screen_width, screen_height = screen.get_size()
    dialog_width = 400
    dialog_height = 150
    dialog_rect = pygame.Rect(
        (screen_width - dialog_width) // 2,
        (screen_height - dialog_height) // 2,
        dialog_width,
        dialog_height
    )
    
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    
    pygame.draw.rect(screen, (50, 50, 50), dialog_rect, border_radius=10)
    pygame.draw.rect(screen, (100, 100, 100), dialog_rect, 2, border_radius=10)
    
    font = pygame.font.SysFont('Arial', 24)
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(dialog_rect.centerx, dialog_rect.y + 40))
    screen.blit(text, text_rect)
    
    # Botones con acciones definidas
    btn_yes = Button(dialog_rect.centerx - 110, dialog_rect.bottom - 60, 100, 40, "Sí", "yes")
    btn_no = Button(dialog_rect.centerx + 10, dialog_rect.bottom - 60, 100, 40, "No", "no")
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        btn_yes.update_hover(mouse_pos)
        btn_no.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            action_yes = btn_yes.handle_click(event)
            action_no = btn_no.handle_click(event)
            
            if action_yes == "yes":
                return True
            if action_no == "no":
                return False
        
        btn_yes.draw(screen)
        btn_no.draw(screen)
        pygame.display.update()

def show_result(screen, winner_name, color):
    screen.fill(BG_COLOR)
    font = pygame.font.SysFont('Arial', 72)
    text = font.render(f"¡{winner_name} Gana!", True, color)
    text_rect = text.get_rect(center=(screen.get_width()/2, screen.get_height()/3))
    screen.blit(text, text_rect)
    
    buttons = [
        Button(screen.get_width()/2 - 150, screen.get_height()/2, 300, 50, "Reintentar", "retry"),
        Button(screen.get_width()/2 - 150, screen.get_height()/2 + 70, 300, 50, "Menú Principal", "menu"),
        Button(screen.get_width()/2 - 150, screen.get_height()/2 + 140, 300, 50, "Salir", "exit")
    ]
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        for btn in buttons:
            btn.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.VIDEOEXPOSE:  # Redibujar al restaurar ventana
                screen.fill(BG_COLOR)
                screen.blit(text, text_rect)
                for btn in buttons:
                    btn.draw(screen)
                pygame.display.flip()
            
            for btn in buttons:
                action = btn.handle_click(event)
                if action:
                    return action

        for btn in buttons:
            btn.draw(screen)
        
        pygame.display.flip()

def show_menu(screen):
    config = PlayerConfig()
    screen_rect = screen.get_rect()
    
    # Centrar elementos dinámicamente
    inputs = [
        TextInput(screen_rect.centerx - 250, 200, 200, 40, config.names[0]),
        TextInput(screen_rect.centerx + 50, 200, 200, 40, config.names[1])
    ]
    
    # Dropdowns con posiciones relativas
    dropdown1 = Dropdown(screen_rect.centerx - 250, 260, 200, 40, list(range(len(COLORS))))
    dropdown2 = Dropdown(screen_rect.centerx + 50, 260, 200, 40, list(range(len(COLORS))))
    dropdown1.other = dropdown2
    dropdown2.other = dropdown1
    dropdown1.selected = config.colors[0]
    dropdown2.selected = config.colors[1]
    dropdowns = [dropdown1, dropdown2]

    # Botones centrados
    game_buttons = [
    Button(screen_rect.centerx - 150, 400, 300, 50, "Jugar vs Jugador", "PVP"),
    Button(screen_rect.centerx - 150, 470, 300, 50, "Jugar vs IA", "PVAI"),
    Button(screen_rect.centerx - 150, 540, 300, 50, "IA vs IA", "AIVAI"),  # Nuevo botón
    Button(screen_rect.centerx - 150, 610, 300, 50, "Historial", "RECORDS"),
    Button(screen_rect.centerx - 150, 680, 300, 50, "Salir", "EXIT")
]

    pygame.time.set_timer(pygame.USEREVENT + 1, 100)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        # Actualizar hover de todos los botones
        for btn in game_buttons:
            btn.update_hover(mouse_pos)

        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Manejar inputs
            for inp in inputs:
                inp.handle_event(event)
            
            # Manejar dropdowns primero
            dropdown_handled = False
            for dropdown in dropdowns:
                if dropdown.handle_event(event):
                    dropdown_handled = True
                    config.colors = [dropdowns[0].selected, dropdowns[1].selected]
                    dropdown.other.update_available()
            
            # Manejar botones solo si no hay dropdown activo
            if not dropdown_handled:
                for btn in game_buttons:
                    action = btn.handle_click(event)
                    if action == "RECORDS":
                        show_records(screen)
                    elif action == "EXIT":
                        pygame.quit()
                        sys.exit()
                    elif action in ["PVP", "PVAI", "AIVAI"]: 
                        config.names = [inputs[0].text, inputs[1].text]
                        return action, config

        # Dibujado
        screen.fill(BG_COLOR)
        
        # Título
        title_font = pygame.font.SysFont('Arial', 72, bold=True)
        title_surf = title_font.render("HEX GAME", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(screen_rect.centerx, 100))
        screen.blit(title_surf, title_rect)

        # Elementos de UI
        for inp in inputs:
            inp.draw(screen)
        
        # Dibujar botones primero
        for btn in game_buttons:
            btn.draw(screen)

        # Dibujar dropdowns después para que queden encima
        for i, dropdown in enumerate(dropdowns):
            # Etiqueta jugador con nombre actualizado
            font = pygame.font.SysFont('Arial', 24)
            label_text = f"{config.names[i]}:"
            label = font.render(label_text, True, (255,255,255))
            screen.blit(label, (dropdown.rect.x - 90, dropdown.rect.centery - 12))
            dropdown.draw(screen)

        pygame.display.flip()

def show_records(screen):
    screen_rect = screen.get_rect()
    btn_back = Button(screen_rect.centerx - 100, screen_rect.height - 100, 200, 50, "Volver al Menú", "MENU")
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        btn_back.update_hover(mouse_pos)  # Actualizar hover cada frame

        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Manejar TODOS los eventos relevantes
            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION]:
                action = btn_back.handle_click(event)
                if action == "MENU":
                    return

        # Dibujado completo
        screen.fill(BG_COLOR)
        
        # Título
        title_font = pygame.font.SysFont('Arial', 48, bold=True)
        title = title_font.render("HISTORIAL DE PARTIDAS", True, (255,255,255))
        screen.blit(title, (screen_rect.centerx - title.get_width()//2, 50))
        
        # Registros
        font = pygame.font.SysFont('Arial', 24)
        y = 150
        try:
            with open("records.txt", "r") as f:
                for line in f:
                    parts = line.strip().split(';')
                    if len(parts) == 3:
                        players, wins_j1, wins_j2 = parts
                        player1, player2 = players.split(',')
                        text = font.render(
                            f"{player1} vs {player2}: {wins_j1} - {wins_j2}", 
                            True, (255,255,255)
                        )
                        screen.blit(text, (screen_rect.centerx - text.get_width()//2, y))
                        y += 40
        except FileNotFoundError:
            # Posicionamiento vertical mejorado
            error_text = font.render("No hay registros de partidas aún", True, (255,255,255))
            screen.blit(error_text, (screen_rect.centerx - error_text.get_width()//2, screen_rect.centery - 50))

        # Botón siempre visible
        btn_back.draw(screen)
        
        pygame.display.flip()