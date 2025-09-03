import pygame
import math
import sys
from enum import Enum

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
        
        # Variables físicas del CRT
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
        self.setup_interface_elements()
        
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
        
        # Clock para controlar FPS
        self.clock = pygame.time.Clock()
        
    def setup_interface_elements(self):
        """Configura las posiciones de todos los elementos de la interfaz"""
        # Panel de control
        self.control_panel_rect = pygame.Rect(20, 20, self.control_panel_width, 760)
        
        # Sliders
        slider_x = 40
        slider_width = 280
        slider_height = 20
        
        self.acceleration_slider = {
            'rect': pygame.Rect(slider_x, 120, slider_width, slider_height),
            'value': self.acceleration_voltage / self.max_voltage,
            'label': 'V. Aceleración'
        }
        
        self.vertical_slider = {
            'rect': pygame.Rect(slider_x, 170, slider_width, slider_height),
            'value': (self.vertical_voltage + self.max_deflection_voltage) / (2 * self.max_deflection_voltage),
            'label': 'V. Vertical'
        }
        
        self.horizontal_slider = {
            'rect': pygame.Rect(slider_x, 220, slider_width, slider_height),
            'value': (self.horizontal_voltage + self.max_deflection_voltage) / (2 * self.max_deflection_voltage),
            'label': 'V. Horizontal'
        }
        
        self.persistence_slider = {
            'rect': pygame.Rect(slider_x, 270, slider_width, slider_height),
            'value': self.persistence_time / 5.0,
            'label': 'Persistencia'
        }
        
        self.freq_vertical_slider = {
            'rect': pygame.Rect(slider_x, 320, slider_width, slider_height),
            'value': self.freq_vertical / 10.0,
            'label': 'Frecuencia Vertical'
        }
        
        self.freq_horizontal_slider = {
            'rect': pygame.Rect(slider_x, 370, slider_width, slider_height),
            'value': self.freq_horizontal / 10.0,
            'label': 'Frecuencia Horizontal'
        }
        
        # Botones
        self.manual_button = pygame.Rect(40, 450, 120, 40)
        self.lissajous_button = pygame.Rect(180, 450, 120, 40)
        self.reset_button = pygame.Rect(110, 500, 80, 30)
        
        # Grid de proporciones (para modo Lissajous)
        self.grid_start_x = 1000
        self.grid_start_y = 450
        self.grid_cell_size = 60
        
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
        if self.manual_button.collidepoint(pos):
            self.current_mode = Mode.MANUAL
            self.electron_points = []  # Limpiar pantalla
        elif self.lissajous_button.collidepoint(pos):
            self.current_mode = Mode.LISSAJOUS
            self.electron_points = []
        elif self.reset_button.collidepoint(pos):
            self.reset_simulation()
        
        # Grid de proporciones (solo en modo Lissajous)
        elif self.current_mode == Mode.LISSAJOUS:
            self.handle_grid_click(pos)
        
        # Sliders
        self.handle_slider_click(pos)
    
    def handle_drag(self, pos):
        """Maneja el arrastre de sliders"""
        self.handle_slider_click(pos)
    
    def handle_slider_click(self, pos):
        """Maneja los clicks en los sliders"""
        sliders = [
            self.acceleration_slider,
            self.vertical_slider if self.current_mode == Mode.MANUAL else None,
            self.horizontal_slider if self.current_mode == Mode.MANUAL else None,
            self.persistence_slider,
            self.freq_vertical_slider if self.current_mode == Mode.LISSAJOUS else None,
            self.freq_horizontal_slider if self.current_mode == Mode.LISSAJOUS else None
        ]
        
        for slider in sliders:
            if slider and slider['rect'].collidepoint(pos):
                # Calcular nuevo valor basado en posición del mouse
                relative_x = pos[0] - slider['rect'].x
                slider['value'] = max(0, min(1, relative_x / slider['rect'].width))
                self.update_values_from_sliders()
                break
    
    def handle_grid_click(self, pos):
        """Maneja clicks en el grid de proporciones"""
        if pos[0] >= self.grid_start_x and pos[1] >= self.grid_start_y:
            col = (pos[0] - self.grid_start_x) // self.grid_cell_size
            row = (pos[1] - self.grid_start_y) // self.grid_cell_size
            
            if 0 <= col < 6 and 0 <= row < 4:
                index = row * 6 + col
                if index < len(self.lissajous_ratios):
                    self.selected_ratio_index = index
                    ratio = self.lissajous_ratios[index]
                    self.freq_horizontal = ratio[0]
                    self.freq_vertical = ratio[1]
                    self.update_sliders_from_values()
                    self.electron_points = []  # Limpiar pantalla
    
    def update_values_from_sliders(self):
        """Actualiza los valores físicos basado en los sliders"""
        self.acceleration_voltage = self.acceleration_slider['value'] * self.max_voltage
        
        if self.current_mode == Mode.MANUAL:
            self.vertical_voltage = (self.vertical_slider['value'] - 0.5) * 2 * self.max_deflection_voltage
            self.horizontal_voltage = (self.horizontal_slider['value'] - 0.5) * 2 * self.max_deflection_voltage
        
        self.persistence_time = self.persistence_slider['value'] * 5.0
        
        if self.current_mode == Mode.LISSAJOUS:
            self.freq_vertical = self.freq_vertical_slider['value'] * 10.0
            self.freq_horizontal = self.freq_horizontal_slider['value'] * 10.0
    
    def update_sliders_from_values(self):
        """Actualiza los sliders basado en los valores físicos"""
        self.acceleration_slider['value'] = self.acceleration_voltage / self.max_voltage
        self.vertical_slider['value'] = (self.vertical_voltage + self.max_deflection_voltage) / (2 * self.max_deflection_voltage)
        self.horizontal_slider['value'] = (self.horizontal_voltage + self.max_deflection_voltage) / (2 * self.max_deflection_voltage)
        self.persistence_slider['value'] = self.persistence_time / 5.0
        self.freq_vertical_slider['value'] = self.freq_vertical / 10.0
        self.freq_horizontal_slider['value'] = self.freq_horizontal / 10.0
    
    def reset_simulation(self):
        """Reinicia la simulación"""
        self.electron_points = []
        self.time = 0.0
    
    def calculate_electron_position(self):
        """Calcula la posición del electrón en la pantalla del CRT"""
        if self.current_mode == Mode.MANUAL:
            # En modo manual, la posición es directamente proporcional al voltaje
            x_deflection = (self.horizontal_voltage / self.max_deflection_voltage) * (self.crt_screen_size / 2)
            y_deflection = (self.vertical_voltage / self.max_deflection_voltage) * (self.crt_screen_size / 2)
        else:
            # En modo Lissajous, usar funciones sinusoidales
            x_deflection = (self.crt_screen_size / 2.2) * math.sin(2 * math.pi * self.freq_horizontal * self.time + self.phase_horizontal)
            y_deflection = (self.crt_screen_size / 2.2) * math.sin(2 * math.pi * self.freq_vertical * self.time + self.phase_vertical)
        
        # Convertir a coordenadas de pantalla
        screen_x = self.crt_screen_x + self.crt_screen_size // 2 + x_deflection
        screen_y = self.crt_screen_y + self.crt_screen_size // 2 - y_deflection  # Y invertida
        
        return int(screen_x), int(screen_y)
    
    def update_simulation(self, dt):
        """Actualiza la simulación"""
        if self.current_mode == Mode.LISSAJOUS:
            self.time += dt
        
        # Calcular nueva posición del electrón
        electron_pos = self.calculate_electron_position()
        
        # Agregar punto con timestamp
        current_time = pygame.time.get_ticks() / 1000.0
        self.electron_points.append((electron_pos, current_time))
        
        # Remover puntos antiguos basado en persistencia
        self.electron_points = [
            (pos, timestamp) for pos, timestamp in self.electron_points
            if current_time - timestamp <= self.persistence_time
        ]
    
    def draw_slider(self, slider, enabled=True):
        """Dibuja un slider"""
        color = self.GRAY if enabled else self.LIGHT_GRAY
        
        # Fondo del slider
        pygame.draw.rect(self.screen, color, slider['rect'])
        pygame.draw.rect(self.screen, self.BLACK, slider['rect'], 2)
        
        # Handle del slider
        if enabled:
            handle_x = slider['rect'].x + slider['value'] * slider['rect'].width
            handle_rect = pygame.Rect(handle_x - 5, slider['rect'].y - 5, 10, slider['rect'].height + 10)
            pygame.draw.rect(self.screen, self.BLUE, handle_rect)
        
        # Label
        label_color = self.BLACK if enabled else self.GRAY
        label_surface = self.font_small.render(slider['label'], True, label_color)
        self.screen.blit(label_surface, (slider['rect'].x, slider['rect'].y - 20))
    
    def draw_crt_views(self):
        """Dibuja las vistas lateral y superior del CRT"""
        # Vista lateral
        lateral_rect = pygame.Rect(400, 100, 300, 150)
        pygame.draw.rect(self.screen, self.LIGHT_GRAY, lateral_rect)
        pygame.draw.rect(self.screen, self.BLACK, lateral_rect, 2)
        
        # Placas verticales en vista lateral
        plate_top = pygame.Rect(450, 120, 80, 8)
        plate_bottom = pygame.Rect(450, 212, 80, 8)
        pygame.draw.rect(self.screen, self.GRAY, plate_top)
        pygame.draw.rect(self.screen, self.GRAY, plate_bottom)
        
        # Trayectoria del electrón en vista lateral
        if self.current_mode == Mode.MANUAL:
            y_offset = (self.vertical_voltage / self.max_deflection_voltage) * 40
        else:
            y_offset = 20 * math.sin(2 * math.pi * self.freq_vertical * self.time)
        
        start_pos = (420, 175)
        end_pos = (680, 175 - y_offset)
        pygame.draw.line(self.screen, self.GREEN, start_pos, end_pos, 3)
        pygame.draw.circle(self.screen, self.YELLOW, end_pos, 4)
        
        # Label
        label = self.font_medium.render("Vista Lateral", True, self.BLACK)
        self.screen.blit(label, (lateral_rect.x + 10, lateral_rect.y - 25))
        
        # Vista superior
        superior_rect = pygame.Rect(800, 100, 300, 150)
        pygame.draw.rect(self.screen, self.LIGHT_GRAY, superior_rect)
        pygame.draw.rect(self.screen, self.BLACK, superior_rect, 2)
        
        # Placas horizontales en vista superior
        plate_left = pygame.Rect(850, 160, 8, 80)
        plate_right = pygame.Rect(992, 160, 8, 80)
        pygame.draw.rect(self.screen, self.GRAY, plate_left)
        pygame.draw.rect(self.screen, self.GRAY, plate_right)
        
        # Trayectoria del electrón en vista superior
        if self.current_mode == Mode.MANUAL:
            x_offset = (self.horizontal_voltage / self.max_deflection_voltage) * 40
        else:
            x_offset = 20 * math.sin(2 * math.pi * self.freq_horizontal * self.time)
        
        start_pos = (820, 175)
        end_pos = (1080, 175 + x_offset)
        pygame.draw.line(self.screen, self.GREEN, start_pos, end_pos, 3)
        pygame.draw.circle(self.screen, self.YELLOW, end_pos, 4)
        
        # Label
        label = self.font_medium.render("Vista Superior", True, self.BLACK)
        self.screen.blit(label, (superior_rect.x + 10, superior_rect.y - 25))
    
    def draw_crt_screen(self):
        """Dibuja la pantalla del CRT"""
        # Pantalla principal
        crt_rect = pygame.Rect(self.crt_screen_x, self.crt_screen_y, self.crt_screen_size, self.crt_screen_size)
        pygame.draw.rect(self.screen, self.BLACK, crt_rect)
        pygame.draw.rect(self.screen, self.GREEN, crt_rect, 2)
        
        # Puntos del electrón con fade basado en persistencia
        current_time = pygame.time.get_ticks() / 1000.0
        for pos, timestamp in self.electron_points:
            age = current_time - timestamp
            alpha = max(0, 1 - (age / self.persistence_time))
            
            # Crear color con alpha
            brightness = int(255 * alpha)
            color = (brightness, brightness, 0)  # Amarillo que se desvanece
            
            if brightness > 0:
                pygame.draw.circle(self.screen, color, pos, 2)
        
        # Label
        label = self.font_medium.render("Pantalla del CRT (LISSAJOUS)", True, self.BLACK)
        self.screen.blit(label, (self.crt_screen_x, self.crt_screen_y - 25))
    
    def draw_grid(self):
        """Dibuja el grid de proporciones de Lissajous"""
        if self.current_mode != Mode.LISSAJOUS:
            return
        
        # Título
        title = self.font_medium.render("Ratios de Frecuencia", True, self.BLACK)
        self.screen.blit(title, (self.grid_start_x, self.grid_start_y - 30))
        
        # Grid
        for i, ratio in enumerate(self.lissajous_ratios):
            if i >= 24:  # 6x4 grid
                break
            
            row = i // 6
            col = i % 6
            
            x = self.grid_start_x + col * self.grid_cell_size
            y = self.grid_start_y + row * self.grid_cell_size
            
            cell_rect = pygame.Rect(x, y, self.grid_cell_size - 2, self.grid_cell_size - 2)
            
            # Color de fondo
            if i == self.selected_ratio_index:
                pygame.draw.rect(self.screen, self.BLUE, cell_rect)
            else:
                pygame.draw.rect(self.screen, self.LIGHT_GRAY, cell_rect)
            
            pygame.draw.rect(self.screen, self.BLACK, cell_rect, 1)
            
            # Texto del ratio
            ratio_text = f"{ratio[0]}:{ratio[1]}"
            text_surface = self.font_small.render(ratio_text, True, self.BLACK)
            text_rect = text_surface.get_rect(center=cell_rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def draw_control_panel(self):
        """Dibuja el panel de control"""
        # Fondo del panel
        pygame.draw.rect(self.screen, self.LIGHT_GRAY, self.control_panel_rect)
        pygame.draw.rect(self.screen, self.BLACK, self.control_panel_rect, 2)
        
        # Título
        title = self.font_large.render("CONTROLES CRT", True, self.BLACK)
        self.screen.blit(title, (40, 40))
        
        # Sliders
        self.draw_slider(self.acceleration_slider, True)
        self.draw_slider(self.vertical_slider, self.current_mode == Mode.MANUAL)
        self.draw_slider(self.horizontal_slider, self.current_mode == Mode.MANUAL)
        self.draw_slider(self.persistence_slider, True)
        self.draw_slider(self.freq_vertical_slider, self.current_mode == Mode.LISSAJOUS)
        self.draw_slider(self.freq_horizontal_slider, self.current_mode == Mode.LISSAJOUS)
        
        # Botones de modo
        manual_color = self.ORANGE if self.current_mode == Mode.MANUAL else self.GRAY
        lissajous_color = self.ORANGE if self.current_mode == Mode.LISSAJOUS else self.GRAY
        
        pygame.draw.rect(self.screen, manual_color, self.manual_button)
        pygame.draw.rect(self.screen, self.BLACK, self.manual_button, 2)
        
        pygame.draw.rect(self.screen, lissajous_color, self.lissajous_button)
        pygame.draw.rect(self.screen, self.BLACK, self.lissajous_button, 2)
        
        # Botón reset
        pygame.draw.rect(self.screen, self.RED, self.reset_button)
        pygame.draw.rect(self.screen, self.BLACK, self.reset_button, 2)
        
        # Texto de botones
        manual_text = self.font_medium.render("Modo Manual", True, self.BLACK)
        manual_rect = manual_text.get_rect(center=self.manual_button.center)
        self.screen.blit(manual_text, manual_rect)
        
        lissajous_text = self.font_small.render("Modo Lissajous", True, self.BLACK)
        lissajous_rect = lissajous_text.get_rect(center=self.lissajous_button.center)
        self.screen.blit(lissajous_text, lissajous_rect)
        
        reset_text = self.font_small.render("Reset", True, self.BLACK)
        reset_rect = reset_text.get_rect(center=self.reset_button.center)
        self.screen.blit(reset_text, reset_rect)
        
        # Estado actual
        y_offset = 560
        state_title = self.font_medium.render("ESTADO", True, self.BLACK)
        self.screen.blit(state_title, (40, y_offset))
        
        mode_text = f"MODO: {self.current_mode.value.upper()}"
        mode_surface = self.font_small.render(mode_text, True, self.BLACK)
        self.screen.blit(mode_surface, (40, y_offset + 30))
        
        # Valores actuales
        values = [
            f"Aceleración: {self.acceleration_voltage:.0f} V",
            f"Vertical: {self.vertical_voltage:.1f} V",
            f"Horizontal: {self.horizontal_voltage:.1f} V",
            f"Persistencia: {self.persistence_time:.1f} s"
        ]
        
        if self.current_mode == Mode.LISSAJOUS:
            values.extend([
                f"Freq V: {self.freq_vertical:.1f} Hz",
                f"Freq H: {self.freq_horizontal:.1f} Hz"
            ])
        
        for i, value in enumerate(values):
            text_surface = self.font_small.render(value, True, self.BLACK)
            self.screen.blit(text_surface, (40, y_offset + 60 + i * 20))
    
    def run(self):
        """Ejecuta la simulación principal"""
        running = True
        
        while running:
            dt = self.clock.tick(60) / 1000.0  # 60 FPS
            
            running = self.handle_events()
            self.update_simulation(dt)
            
            # Dibujar todo
            self.screen.fill(self.WHITE)
            
            self.draw_control_panel()
            self.draw_crt_views()
            self.draw_crt_screen()
            self.draw_grid()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    simulation = CRTSimulation()
    simulation.run()