# 🎮 Hex Game - Proyecto de IA
Clásico juego Hex con inteligencia artificial, diseñado para explorar estrategias de juego adversarial. Implementa múltiples modos de juego y algoritmos IA con visualización interactiva.

## 🤖 IA Implementadas:

✨ **Cerebro Cuántico - MasterAI**
- ⚡ **Mini-Max con Poda Alpha-Beta** 
- 🧩 **Poda Inteligente** basada en conexiones potenciales, con memoización.
- 🗺️ **Algoritmo A*** modificado para caminos hexagonales
- 🤹 **Hilos Mágicos**: Paralelización limitada con `asgiref.sync` + `asyncio` (¡Python hace lo que puede!) 

🤯 **Sistema ¿Experto? MrHuman (😅)** con:
  - Patrones de juego "creativos" que yo, la "maestra estratega y experta", diseñé
  - Ocasionales errores estratégicos (¡Para hacerlo más humano! Definitivamente no es porque sé tanto del juego como quien nunca lo ha jugado 🙈)
  - Decisiones *casi* racionales que harían llorar (de frustración) a un profesor de teoría de juegos

🍀 Random AI:
  - 🎪 Caos controlado en forma de algoritmo
  - 🧪 Grupo de control perfecto
  - ⏱️ ¡Más rápido que tu reflexión al jugar!

# ⚙️ Mecánicas Centrales del Juego:
  ### 🎲 **Algoritmo Mini-Max**  
Estrategia para juegos de dos jugadores que **maximiza** las ganancias propias y **minimiza** las del rival. Explora recursivamente un árbol de posibles movimientos, simulando turnos alternados ("si yo hago X, el rival podría hacer Y..."). Ideal para juegos con información perfecta como ajedrez o Hex.  

  ### ✂️ **Poda Alpha-Beta**  
Optimización del Mini-Max que **elimina ramas inútiles** del árbol de decisiones. Usa umbrales (alpha = mejor máximo actual, beta = mejor mínimo actual) para descartar movimientos que no cambiarán el resultado final. ¡Reduce tiempo de cálculo hasta en un 90% sin afectar la calidad de la decisión!  

  ### 📦 **Memoización**  
Técnica de almacenamiento **cache** para evitar cálculos repetidos. Guarda resultados de funciones costosas en una "libreta de apuntes" (diccionario/hashmap), usando los parámetros de entrada como clave. Usado por ejemplo en Fibonacci recursivo: `fib(5)` se calcula una vez, no 15.  

  ### 🔗 **Disjoint Set (Union-Find)**  
Estructura que gestiona **grupos desconectados** con dos operaciones clave:  
1. **Union**: Fusiona dos conjuntos ("conecta" nodos)  
2. **Find**: Verifica si dos elementos están en el mismo grupo  

Con **compresión de camino** y **unión por rango**, logra operaciones casi constantes (O(α(n))). Usado en detección de victoria en Hex en tiempo real.
Responsable de la **magia detrás del tablero 🪄**:
   - ¡Detección de victoria en O(1) usando **Disjoint Set Union**! 
   - Cada movimiento actualiza un sistema de uniones que verifica si conectas los bordes opuestos.

# 📚 Documentación Técnica
🧩 **Estructura del Tablero**:
- Matriz **hexagonal** usando coordenadas axiales (q, r) y un `size` configurable para un tablero de `sizexsize`.
- Sistema de **conversión pixel↔axial** para interacción precisa con la interfaz visual.  

**Componentes Clave**:  
- `player*_positions`: Listas dinámicas de fichas colocadas  
- `disjoint_set`: Detecta conexiones ganadoras en tiempo real  
- `longest_virtual_paths`: Rastrea caminos potenciales para cada jugador 

🧬 **Flujo del Juego**:
1. Inicialización de componentes
2. Bucle principal de Pygame
3. Gestión de eventos y actualización de estado
4. Renderizado condicional basado en modo de juego
5. Post-procesamiento de resultados

# 🚀 Características Principales
- **Modos de Juego**:
  - 👥 Jugador vs Jugador (Local)
  - 🤖 Jugador vs IA (3 tipos diferentes)
  - ⚔️ IA vs IA (Combates automatizados)

- **Personalización**:
  - 🎨 Selección de colores para cada jugador
  - ✏️ Nombres personalizados
  - 📊 Registro histórico de partidas

# 🖥 Interfaz Gráfica
- **Sistema de Menús Dinámico**:
  - 🌀 Animaciones fluidas en transiciones
  - 🎯 Interacción táctil con el tablero hexagonal
  - 📈 Panel de estado en tiempo real

- **Elementos Visuales**:
   - **🔍 Tamaño Recomendado**: 
      - ¡El default! (1000x800px)
      - Redimensionar puede causar viajes interdimensionales de hexágonos
  - **✨ Efecto Hover**:
    - Brillo suave en celdas disponibles
    - Advertencia: Puede generar adicción a pasar el mouse
  - **🤖 Teatro IA**:
    - 🎭 40+ frases creativas mientras "piensa" como por ejemplo:
        - *"Calculando dominación mundial..."* 🌍
        - *"Derritiendo cerebro cuántico..."* 🧠🔥
        - *¡Jaque mate en 3 movimientos!* (spoiler: casi nunca es cierto) ♟️
    - 🖱️ Simulación de movimiento humano (la IA mueve el mouse alrededor hasta su posición)

# 🕹 Modo de Uso
1. **Menú Principal**:
   - ✏️ Edita nombres de jugadores
   - 🎨 Selecciona colores
   - ⚙️ Elige modo de juego

2. **Durante el Juego**:
   - 🖱️ Click izquierdo para colocar fichas
   - 🚀 Space/Enter para pausa
   - 📌 Botones flotantes de control

3. **Post-Juego**:
   - 👁️ Ver estado final del tablero
   - 🔄 Reintentar misma configuración
   - 📊 Registrar resultados

# 🛠️ Extensibilidad del Sistema
**Para crear una nueva IA**:
1. Crear tu propio script, te recomiendo guardarlo en la carpeta `ai/`
2. Implementar método `get_best_move(game) -> (row, col)` y ponerle prop `NAME` 
3. Registrar en `AI_REGISTRY` de `game/configs.py`

Todos requisitos indispensables o tendrás un BOOOM 💥 garantizado.

**Ejemplo Esqueleto**:
```python
class TuSuperIA():
    NAME = "Super IA"
    
    def get_best_move(self, game):
        # Lógica brillante aquí
        return (random.randint(0, game.size-1), random.randint(0, game.size-1))  # IA pro 😎
```

# 🧪 Debugger Integrado:
Se encuentra en `debugger/debug_scenarios.py`.

**Capacidades Clave**:  
- 🎲 **Escenarios Preconfigurados**: 10+ tableros con patrones estratégicos  
- 🔄 **Simulación Automatizada**: Prueba IAs en diferentes configuraciones   
- 🚨 **Detección de Errores**: Identifica movimientos inválidos en tiempo real  

# **📁 Estructura de Carpetas**:
  /  
  ├── 🎮 main.py              # Motor principal  
  ├── 📁 game/               # Corazón del juego  
  │       ├── ⚙️ configs.py       # Constantes y IA Registry  
  │       ├── 🧩 game_logic.py    # Lógica del tablero y DSU  
  │       └── 🎨 ui.py           # Sistema gráfico y conversores axiales  
  │  
  ├── 🤖 ai/                 # Cerebros artificiales  
  │       ├── 🎲 rand_ai.py      # IA Caótica  
  │       ├── 🧠 master_ai.py    # Algoritmo Maestro  
  │       └── 😅 mr_human.py     # "Experto" estratégico  
  │  
  ├── 🖼️ assets/             # Recursos multimedia  
  │       ├── ✒️ arial.ttf       # Fuente principal  
  │       └── 🔷 hex_icon.ico    # Icono del juego  
  |       └── (...)                # Más fuentes
  │  
  ├── 🐞 debugger/           # Herramientas de desarrollo  
  │         └── 🔧 debug_scenarios.py  # Banco de pruebas IA  
  │  
  └── 📊 records/            # Historial  
            └️ 📜 rec.py           # Gestor de récords y estadísticas  

# ⚠️ Nota sobre el Historial
**📜 Registro de Partidas**:
- ¡Funciona!... *Mayormente* 🪲
- Al regresar al menú principal desde historial:
  - 63% de probabilidad de éxito
  - 37% de reinicio mágico (¡Nueva función no documentada!)

Ante tal problema, la solución es un reinicio nuclear total automático 💥. Hace BOOOM 💣 pero funciona y ya sabes como dicen...
  - *"Si funciona, no lo toques"* - Ley de Schrödinger del Código
  
 # 📦 Instalación y Requisitos
 **Requisitos del Sistema**:
- Python 3.8+
- Pygame 2.1+
- asgiref 3.8+
- numpy 2.2+
  
** ⚒️ Instalación**:
```bash
git clone https://github.com/yesi07111/HexGame.git
cd HexGame
pip install -r requirements.txt
python main.py
```
