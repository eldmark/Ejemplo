import pygame

class SliderManager:
    def __init__(self, crt_simulation):
        self.crt = crt_simulation
        self.setup_interface_elements()
    
    def setup_interface_elements(self):
        """Configura las posiciones de todos los elementos de la interfaz"""
        # Sliders
        slider_x = 40
        slider_width = 280
        slider_height = 20
        
        self.acceleration_slider = {
            'rect': pygame.Rect(slider_x, 120, slider_width, slider_height),
            'value': self.crt.acceleration_voltage / self.crt.max_voltage,
            'label': 'V. Aceleración'
        }
        
        self.vertical_slider = {
            'rect': pygame.Rect(slider_x, 170, slider_width, slider_height),
            'value': (self.crt.vertical_voltage + self.crt.max_deflection_voltage) / (2 * self.crt.max_deflection_voltage),
            'label': 'V. Vertical'
        }
        
        self.horizontal_slider = {
            'rect': pygame.Rect(slider_x, 220, slider_width, slider_height),
            'value': (self.crt.horizontal_voltage + self.crt.max_deflection_voltage) / (2 * self.crt.max_deflection_voltage),
            'label': 'V. Horizontal'
        }
        
        self.persistence_slider = {
            'rect': pygame.Rect(slider_x, 270, slider_width, slider_height),
            'value': (self.crt.persistence_time - 0.1) / 9.9,  # Mapear de 0.1-10 a 0-1
            'label': 'Persistencia'
        }
        
        self.freq_vertical_slider = {
            'rect': pygame.Rect(slider_x, 320, slider_width, slider_height),
            'value': self.crt.freq_vertical / 10.0,
            'label': 'Frecuencia Vertical'
        }
        
        self.freq_horizontal_slider = {
            'rect': pygame.Rect(slider_x, 370, slider_width, slider_height),
            'value': self.crt.freq_horizontal / 10.0,
            'label': 'Frecuencia Horizontal'
        }
        
        # Botones
        self.manual_button = pygame.Rect(40, 450, 120, 40)
        self.lissajous_button = pygame.Rect(180, 450, 120, 40)
        self.reset_button = pygame.Rect(110, 500, 80, 30)
    
    def handle_slider_click(self, pos):
        """Maneja los clicks en los sliders"""
        sliders = [
            self.acceleration_slider,
            self.vertical_slider if self.crt.current_mode.value == "Manual" else None,
            self.horizontal_slider if self.crt.current_mode.value == "Manual" else None,
            self.persistence_slider,
            self.freq_vertical_slider if self.crt.current_mode.value == "Lissajous" else None,
            self.freq_horizontal_slider if self.crt.current_mode.value == "Lissajous" else None
        ]
        
        for slider in sliders:
            if slider and slider['rect'].collidepoint(pos):
                # Calcular nuevo valor basado en posición del mouse
                relative_x = pos[0] - slider['rect'].x
                slider['value'] = max(0, min(1, relative_x / slider['rect'].width))
                self.update_values_from_sliders()
                break
    
    def update_values_from_sliders(self):
        """Actualiza los valores físicos basado en los sliders"""
        self.crt.acceleration_voltage = self.acceleration_slider['value'] * self.crt.max_voltage
        
        if self.crt.current_mode.value == "Manual":
            self.crt.vertical_voltage = (self.vertical_slider['value'] - 0.5) * 2 * self.crt.max_deflection_voltage
            self.crt.horizontal_voltage = (self.horizontal_slider['value'] - 0.5) * 2 * self.crt.max_deflection_voltage
        
        # Persistencia de 0.1 a 10 segundos
        self.crt.persistence_time = 0.1 + (self.persistence_slider['value'] * 9.9)
        
        if self.crt.current_mode.value == "Lissajous":
            self.crt.freq_vertical = self.freq_vertical_slider['value'] * 10.0
            self.crt.freq_horizontal = self.freq_horizontal_slider['value'] * 10.0
    
    def update_sliders_from_values(self):
        """Actualiza los sliders basado en los valores físicos"""
        self.acceleration_slider['value'] = self.crt.acceleration_voltage / self.crt.max_voltage
        self.vertical_slider['value'] = (self.crt.vertical_voltage + self.crt.max_deflection_voltage) / (2 * self.crt.max_deflection_voltage)
        self.horizontal_slider['value'] = (self.crt.horizontal_voltage + self.crt.max_deflection_voltage) / (2 * self.crt.max_deflection_voltage)
        
        # Mapear persistencia de 0.1-10 a 0-1
        self.persistence_slider['value'] = (self.crt.persistence_time - 0.1) / 9.9
        
        self.freq_vertical_slider['value'] = self.crt.freq_vertical / 10.0
        self.freq_horizontal_slider['value'] = self.crt.freq_horizontal / 10.0
    
    def draw_slider(self, slider, enabled=True):
        """Dibuja un slider"""
        color = self.crt.GRAY if enabled else self.crt.LIGHT_GRAY
        
        # Fondo del slider
        pygame.draw.rect(self.crt.screen, color, slider['rect'])
        pygame.draw.rect(self.crt.screen, self.crt.BLACK, slider['rect'], 2)
        
        # Handle del slider
        if enabled:
            handle_x = slider['rect'].x + slider['value'] * slider['rect'].width
            handle_rect = pygame.Rect(handle_x - 5, slider['rect'].y - 5, 10, slider['rect'].height + 10)
            pygame.draw.rect(self.crt.screen, self.crt.BLUE, handle_rect)
        
        # Label
        label_color = self.crt.BLACK if enabled else self.crt.GRAY
        label_surface = self.crt.font_small.render(slider['label'], True, label_color)
        self.crt.screen.blit(label_surface, (slider['rect'].x, slider['rect'].y - 20))