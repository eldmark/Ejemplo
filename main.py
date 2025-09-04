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
        
        self.WIDTH = 1200
        self.HEIGHT = 720
        
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Simulación de un Tubo de Rayos Catódicos")
        
        # Paleta de colores 
        self.WHITE = (255, 255, 255)
        self.BLACK = (20, 20, 25)
        self.DARK_GRAY = (45, 45, 55)
        self.GRAY = (80, 85, 95)
        self.LIGHT_GRAY = (240, 242, 245)
        self.MEDIUM_GRAY = (180, 185, 190)
        
        self.PRIMARY_BLUE = (59, 130, 246)  
        self.SECONDARY_BLUE = (37, 99, 235)
        self.SUCCESS_GREEN = (34, 197, 94)
        self.WARNING_ORANGE = (251, 146, 60)
        self.DANGER_RED = (239, 68, 68)
        self.CRT_GREEN = (0, 255, 127)  
        self.ELECTRON_YELLOW = (255, 235, 59)
        
        self.GLASS_EFFECT = (255, 255, 255, 30)
        self.SHADOW_COLOR = (0, 0, 0, 50)
        
        # Fuentes
        try:
            self.font_title = pygame.font.Font(None, 32)
            self.font_large = pygame.font.Font(None, 28)
            self.font_medium = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 20)
            self.font_tiny = pygame.font.Font(None, 16)
        except:
            # Fallback si las fuentes no están disponibles
            self.font_title = pygame.font.Font(None, 32)
            self.font_large = pygame.font.Font(None, 28)
            self.font_medium = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 20)
            self.font_tiny = pygame.font.Font(None, 16)
        
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
        
        self.paused = False  # Estado de pausa
        
        # Rangos para los controles
        self.max_voltage = 1000.0
        self.max_deflection_voltage = 500.0
        
        # Posiciones y tamaños de los elementos de la interfaz
        self.control_panel_width = 350
        
        # Pantalla del CRT y puntos
        self.crt_screen_size = 350
        self.crt_screen_x = 580
        self.crt_screen_y = 300
        self.electron_points = []
        
        # Grid de proporciones de Lissajous
        self.lissajous_ratios = [
            (1, 1), (1, 2), (2, 1), (1, 3), 
            (3, 1), (2, 3), (3, 2), (1, 4), 
            (4, 1), (3, 4), (4, 3), (2, 5),
            (5, 2), (3, 5), (5, 3), (4, 5), 
            (5, 4), (1, 6), (6, 1), (5, 6)
        ]
        self.selected_ratio_index = 0
        
        # Inicializar componentes
        self.slider_manager = SliderManager(self)
        self.visualization = Visualization(self)
        self.calculos = Calculos(self)
        
        # Clock para controlar FPS
        self.clock = pygame.time.Clock()
        
        
    def draw_rounded_rect(self, surface, color, rect, radius):
        """Dibuja un rectángulo con esquinas redondeadas"""
        if radius > min(rect.width, rect.height) // 2:
            radius = min(rect.width, rect.height) // 2
        
        # Crear superficie temporal para el rectángulo redondeado
        temp_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(temp_surface, color, (0, 0, rect.width, rect.height), border_radius=radius)
        surface.blit(temp_surface, rect.topleft)
    
    def draw_shadow(self, surface, rect, offset=(3, 3), radius=15):
        """Dibuja"""
        shadow_rect = rect.copy()
        shadow_rect.x += offset[0]
        shadow_rect.y += offset[1]
        
        # Crear superficie para la sombra
        shadow_surface = pygame.Surface((rect.width + radius * 2, rect.height + radius * 2), pygame.SRCALPHA)
        
        # Dibujar múltiples rectángulos con alpha decreciente para simular desenfoque
        for i in range(radius):
            alpha = max(0, 20 - i)
            color = (*self.BLACK[:3], alpha)
            shadow_rect_blur = pygame.Rect(radius - i, radius - i, rect.width + i * 2, rect.height + i * 2)
            pygame.draw.rect(shadow_surface, color, shadow_rect_blur, border_radius=8)
        
        surface.blit(shadow_surface, (shadow_rect.x - radius, shadow_rect.y - radius))
        
    def handle_events(self):
        """Maneja todos los eventos de pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Manejar redimensionamiento de ventana
            elif event.type == pygame.VIDEORESIZE:
                self.WIDTH, self.HEIGHT = event.size
                self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
                # Aquí podrías ajustar las posiciones de los elementos si quieres
                # que se adapten al nuevo tamaño de ventana
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Click izquierdo
                    self.handle_click(event.pos)
            
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:  # Arrastrando
                    self.handle_drag(event.pos)
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                # Controles de voltaje con flechas (solo en modo Manual y sin pausa)
                elif self.current_mode == Mode.MANUAL and not self.paused:
                    step = 51  # Paso de ajuste
                    # Flecha ARRIBA: aumentar voltaje vertical
                    if event.key == pygame.K_UP:
                        self.vertical_voltage = min(self.vertical_voltage + step, self.max_deflection_voltage)
                        self.slider_manager.update_sliders_from_values()
                    
                    # Flecha ABAJO: disminuir voltaje vertical  
                    elif event.key == pygame.K_DOWN:
                        self.vertical_voltage = max(self.vertical_voltage - step, -self.max_deflection_voltage)
                        self.slider_manager.update_sliders_from_values()
                    
                    # Flecha DERECHA: aumentar voltaje horizontal
                    elif event.key == pygame.K_RIGHT:
                        self.horizontal_voltage = min(self.horizontal_voltage + step, self.max_deflection_voltage)
                        self.slider_manager.update_sliders_from_values()
                    
                    # Flecha IZQUIERDA: disminuir voltaje horizontal
                    elif event.key == pygame.K_LEFT:
                        self.horizontal_voltage = max(self.horizontal_voltage - step, -self.max_deflection_voltage)
                        self.slider_manager.update_sliders_from_values()
        
        return True
    def handle_continuous_keys(self):
        """Maneja teclas mantenidas presionadas"""
        if self.current_mode != Mode.MANUAL or self.paused:
            return
        
        keys = pygame.key.get_pressed()
        step = 5  # Paso más pequeño para manejo continuo
        
        # Flechas para voltaje vertical
        if keys[pygame.K_UP]:
            self.vertical_voltage = min(self.vertical_voltage + step, self.max_deflection_voltage)
        elif keys[pygame.K_DOWN]:
            self.vertical_voltage = max(self.vertical_voltage - step, -self.max_deflection_voltage)
        
        # Flechas para voltaje horizontal
        if keys[pygame.K_RIGHT]:
            self.horizontal_voltage = min(self.horizontal_voltage + step, self.max_deflection_voltage)
        elif keys[pygame.K_LEFT]:
            self.horizontal_voltage = max(self.horizontal_voltage - step, -self.max_deflection_voltage)
        
        # Actualizar sliders continuamente
        self.slider_manager.update_sliders_from_values()
    
    def handle_click(self, pos):
        """Maneja los clicks del mouse"""
        if self.paused:
            return
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
        if pos[0] >= 950 and pos[1] >= 320:
            col = (pos[0] - 950) // 60
            row = (pos[1] - 320) // 60
            
            if 0 <= col < 4 and 0 <= row < 5:
                index = row * 4 + col
                if index < len(self.lissajous_ratios):
                    self.selected_ratio_index = index
                    ratio = self.lissajous_ratios[index]
                    self.freq_horizontal = ratio[0]
                    self.freq_vertical = ratio[1]
                    self.slider_manager.update_sliders_from_values()
                    self.electron_points = []  # Limpiar pantalla
    
    def reset_simulation(self):
        """Reinicia la simulación con valores predeterminados"""
        
        if self.paused:
            return
        
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
        current_time = pygame.time.get_ticks() / 1000.0
        
        if self.paused:
            # Durante pausa: NO eliminar puntos basados en persistencia
            # Solo mantener todos los puntos existentes
            return
        
        # Solo ejecutar si NO está pausado
        if self.current_mode == Mode.LISSAJOUS:
            self.time += dt
        
        # Calcular nueva posición del electrón
        electron_pos = self.calculos.calculate_electron_position()
        
        # Agregar punto con timestamp
        self.electron_points.append((electron_pos, current_time))
        
        # Remover puntos antiguos basado en persistencia (solo si no está pausado)
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
            self.handle_continuous_keys()
            self.update_simulation(dt)
            
            # Fondo con gradiente sutil
            self.screen.fill(self.LIGHT_GRAY)
            
            # Dibujar gradiente de fondo sutil
            for y in range(0, self.HEIGHT, 4):
                alpha = int(10 * (1 - y / self.HEIGHT))
                color = (self.WHITE[0], self.WHITE[1], self.WHITE[2], alpha)
                temp_surf = pygame.Surface((self.WIDTH, 4), pygame.SRCALPHA)
                temp_surf.fill(color)
                self.screen.blit(temp_surf, (0, y))
            
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