import pygame
import math
import sys
from enum import Enum
from visualization import Visualization
from calculos import Calculos
from slider import SliderManager

class Mode(Enum):
    MANUAL = "Manual"
    LISSAJOUS = "Lissajous"

class CRTSimulation:
    def __init__(self):
        pygame.init()
        
        # Configuración de la ventana
        self.WIDTH = 1400
        self.HEIGHT = 900
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Simulación de un Tubo de Rayos Catódicos")
        
        # Colores
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (200, 200, 200)
        self.BLUE = (100, 150, 255)
        self.GREEN = (100, 255, 100)
        self.ORANGE = (255, 165, 0)
        self.RED = (255, 100, 100)
        self.YELLOW = (255, 255, 0)
        
        # Fuentes
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 28)
        
        # Modo actual
        self.current_mode = Mode.MANUAL
        
        # Variables físicas del CRT (valores predeterminados)
        self.acceleration_voltage = 1000.0  # V
        self.vertical_voltage = 0.0  # V
        self.horizontal_voltage = 0.0  # V
        self.persistence_time = 1.0  # segundos
        
        # Variables para modo Lissajous
        self.freq_vertical = 1.0  # Hz
        self.freq_horizontal = 1.0  # Hz
        self.phase_vertical = 0.0  # radianes
        self.phase_horizontal = 0.0  # radianes
        self.time = 0.0
        
        # Rangos para los controles
        self.max_voltage = 1000.0
        self.max_deflection_voltage = 500.0
        
        # Posiciones y tamaños de los elementos de la interfaz
        self.control_panel_width = 350
        
        # Pantalla del CRT y puntos
        self.crt_screen_size = 300
        self.crt_screen_x = 650
        self.crt_screen_y = 420
        self.electron_points = []
        
        # Grid de proporciones de Lissajous
        self.lissajous_ratios = [
            (1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (2, 3),
            (3, 2), (1, 4), (4, 1), (3, 4), (4, 3), (2, 5),
            (5, 2), (3, 5), (5, 3), (4, 5), (5, 4), (1, 6),
            (6, 1), (5, 6)
        ]
        self.selected_ratio_index = 0
        
        # Inicializar componentes
        self.slider_manager = SliderManager(self)
        self.visualization = Visualization(self)
        self.calculos = Calculos(self)
        
        # Clock para controlar FPS
        self.clock = pygame.time.Clock()
        
    def handle_events(self):
        """Maneja todos los eventos de pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Click izquierdo
                    self.handle_click(event.pos)
            
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:  # Arrastrando
                    self.handle_drag(event.pos)
        
        return True
    
    def handle_click(self, pos):
        """Maneja los clicks del mouse"""
        # Botones de modo
        if self.slider_manager.manual_button.collidepoint(pos):
            self.current_mode = Mode.MANUAL
            self.electron_points = []  # Limpiar pantalla
        elif self.slider_manager.lissajous_button.collidepoint(pos):
            self.current_mode = Mode.LISSAJOUS
            self.electron_points = []
        elif self.slider_manager.reset_button.collidepoint(pos):
            self.reset_simulation()
        
        # Grid de proporciones (solo en modo Lissajous)
        elif self.current_mode == Mode.LISSAJOUS:
            self.handle_grid_click(pos)
        
        # Sliders
        self.slider_manager.handle_slider_click(pos)
    
    def handle_drag(self, pos):
        """Maneja el arrastre de sliders"""
        self.slider_manager.handle_slider_click(pos)
    
    def handle_grid_click(self, pos):
        """Maneja clicks en el grid de proporciones"""
        if pos[0] >= 1000 and pos[1] >= 450:
            col = (pos[0] - 1000) // 60
            row = (pos[1] - 450) // 60
            
            if 0 <= col < 6 and 0 <= row < 4:
                index = row * 6 + col
                if index < len(self.lissajous_ratios):
                    self.selected_ratio_index = index
                    ratio = self.lissajous_ratios[index]
                    self.freq_horizontal = ratio[0]
                    self.freq_vertical = ratio[1]
                    self.slider_manager.update_sliders_from_values()
                    self.electron_points = []  # Limpiar pantalla
    
    def reset_simulation(self):
        """Reinicia la simulación con valores predeterminados"""
        # Limpiar pantalla
        self.electron_points = []
        self.time = 0.0
        
        # Restaurar valores predeterminados
        self.acceleration_voltage = 1000.0
        self.vertical_voltage = 0.0
        self.horizontal_voltage = 0.0
        self.persistence_time = 1.0
        self.freq_vertical = 1.0
        self.freq_horizontal = 1.0
        self.phase_vertical = 0.0
        self.phase_horizontal = 0.0
        
        # Restaurar ratio seleccionado
        self.selected_ratio_index = 0
        
        # Actualizar sliders para reflejar los valores restaurados
        self.slider_manager.update_sliders_from_values()
    
    def update_simulation(self, dt):
        """Actualiza la simulación"""
        if self.current_mode == Mode.LISSAJOUS:
            self.time += dt
        
        # Calcular nueva posición del electrón
        electron_pos = self.calculos.calculate_electron_position()
        
        # Agregar punto con timestamp
        current_time = pygame.time.get_ticks() / 1000.0
        self.electron_points.append((electron_pos, current_time))
        
        # Remover puntos antiguos basado en persistencia
        self.electron_points = [
            (pos, timestamp) for pos, timestamp in self.electron_points
            if current_time - timestamp <= self.persistence_time
        ]
    
    def run(self):
        """Ejecuta la simulación principal"""
        running = True
        
        while running:
            dt = self.clock.tick(60) / 1000.0  # 60 FPS
            
            running = self.handle_events()
            self.update_simulation(dt)
            
            # Dibujar todo
            self.screen.fill(self.WHITE)
            
            self.visualization.draw_control_panel()
            self.visualization.draw_crt_views()
            self.visualization.draw_crt_screen()
            self.visualization.draw_grid()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    simulation = CRTSimulation()
    simulation.run()