from ai.mr_human import MrHuman
from ai.rand_ai import RandomAI
from ai.master_ai import MasterAI

# Registro de todas las IAs disponibles
AI_REGISTRY = [MasterAI, MrHuman, RandomAI]

# Configuraciones y constantes
WIDTH, HEIGHT = 1000, 800
GRID_SIZE = 11
HEX_RADIUS = 30
MARGIN_LEFT = 150

COLOR_NAMES = {
    0: "Rojo", 1: "Azul", 2: "Verde", 
    3: "Amarillo", 4: "Morado", 5: "Cian"
}

COLORS = [
    (255, 0, 0), (0, 0, 255), (0, 255, 0),
    (255, 255, 0), (128, 0, 128), (0, 255, 255)
]

BG_COLOR = (28, 28, 28)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 150, 200)
HOVER_COLOR = (255, 255, 100, 100)
HEX_NEIGHBORS = [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)]
AI_ANIMATION_STEPS = 30

# Lista de mensajes divertidos para la IA
IA_MESSAGES = [
    "La IA está pensando...", "Calculando dominación mundial", 
    "Buscando tu debilidad", "Revisando manual de estrategia",
    "Optimizando neuronas hexagonales", "Derritiendo cerebro cuántico",
    "Trazando ruta de victoria", "Bloqueando tus esperanzas",
    "Aprendiendo de tus errores", "Replicando patrones ganadores",
    "Ejecutando protocolo win.exe", "Analizando partidas históricas",
    "Simulando futuros posibles", "Codificando jugada maestra",
    "Desafía mi intelecto, humano", "La derrota te espera",
    "Calibrando algoritmo genético", "Explorando espacio de posibilidades",
    "Sintetizando estrategia óptima", "¡Jaque mate en 3 movimientos!",
     "Analizando tablero...", "Calculando jugada óptima",
    "Evaluando patrones ganadores", "Bloqueando rutas enemigas",
    "Optimizando estrategia", "Simulando posibles contraataques",
    "Buscando puntos críticos", "Fortaleciendo conexiones",
    "Contemplando sabiduría ancestral", "Recalculando trayectoria",
    "Desafíame de nuevo, humano", "Aprendiendo de tus errores",
    "Ejecutando protocolo de victoria", "Revisando biblioteca de estrategias",
    "Sintonizando neuronas artificiales", "Generando jugada maestra",
    "Explorando espacio de soluciones", "Validando camino óptimo",
    "Cristalizando pensamiento estratégico", "Armando emboscada hexadecimal"
]

class PlayerConfig:
    def __init__(self):
        self.names = ["Jugador 1", "Jugador 2"]
        self.colors = [0, 1]  # Índices de COLORS


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

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> None:
        rootX = self.find(x)
        rootY = self.find(y)

        if rootX != rootY:
            self.leftmost_index[rootY] = min(
                self.leftmost_index[rootY], self.leftmost_index[rootX]
            )
            self.uppermost_index[rootY] = min(
                self.uppermost_index[rootY], self.uppermost_index[rootX]
            )

            self.rightmost_index[rootY] = max(
                self.rightmost_index[rootY], self.rightmost_index[rootX]
            )
            self.bottommost_index[rootY] = max(
                self.bottommost_index[rootY], self.bottommost_index[rootX]
            )

            self.parent[rootX] = rootY

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)