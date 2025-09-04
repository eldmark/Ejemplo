import pygame
import math

class SliderManager:
    def __init__(self, crt_simulation):
        self.crt = crt_simulation
        self.setup_interface_elements()
    
    def setup_interface_elements(self):
        """Configura las posiciones de todos los elementos de la interfaz"""
        # Sliders con mejor espaciado
        slider_x = 50
        slider_width = 280
        slider_height = 20
        
        self.acceleration_slider = {
            'rect': pygame.Rect(slider_x, 120, slider_width, slider_height),
            'value': self.crt.acceleration_voltage / self.crt.max_voltage,
            'label': 'V. Aceleración',
            'color': self.crt.PRIMARY_BLUE,
            'unit': 'V'
        }
        
        self.vertical_slider = {
            'rect': pygame.Rect(slider_x, 160, slider_width, slider_height),
            'value': (self.crt.vertical_voltage + self.crt.max_deflection_voltage) / (2 * self.crt.max_deflection_voltage),
            'label': 'V. Vertical',
            'color': self.crt.SUCCESS_GREEN,
            'unit': 'V'
        }
        
        self.horizontal_slider = {
            'rect': pygame.Rect(slider_x, 210, slider_width, slider_height),
            'value': (self.crt.horizontal_voltage + self.crt.max_deflection_voltage) / (2 * self.crt.max_deflection_voltage),
            'label': 'V. Horizontal',
            'color': self.crt.DANGER_RED,
            'unit': 'V'
        }
        
        self.persistence_slider = {
            'rect': pygame.Rect(slider_x, 260, slider_width, slider_height),
            'value': (self.crt.persistence_time - 0.1) / 9.9,  # Mapear de 0.1-10 a 0-1
            'label': 'Persistencia',
            'color': self.crt.GRAY,
            'unit': 's'
        }
        
        self.freq_vertical_slider = {
            'rect': pygame.Rect(slider_x, 310, slider_width, slider_height),
            'value': self.crt.freq_vertical / 10.0,
            'label': 'Frecuencia Vertical',
            'color': self.crt.WARNING_ORANGE,
            'unit': 'Hz'
        }
        
        self.freq_horizontal_slider = {
            'rect': pygame.Rect(slider_x, 360, slider_width, slider_height),
            'value': self.crt.freq_horizontal / 10.0,
            'label': 'Frecuencia Horizontal',
            'color': self.crt.WARNING_ORANGE,
            'unit': 'Hz'
        }
        
        # Botones
        self.manual_button = pygame.Rect(50, 400, 120, 40)
        self.lissajous_button = pygame.Rect(220, 400, 120, 40)
        self.reset_button = pygame.Rect(150, 450, 90, 30)
    
    def handle_slider_click(self, pos):
        """Maneja los clicks en los sliders"""
        if self.crt.paused:
            return
        
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
    
    def get_slider_value(self, slider):
        """Obtiene el valor actual del slider formateado"""
        if slider == self.acceleration_slider:
            return f"{self.crt.acceleration_voltage:.0f}"
        elif slider == self.vertical_slider:
            return f"{self.crt.vertical_voltage:.1f}"
        elif slider == self.horizontal_slider:
            return f"{self.crt.horizontal_voltage:.1f}"
        elif slider == self.persistence_slider:
            return f"{self.crt.persistence_time:.1f}"
        elif slider == self.freq_vertical_slider:
            return f"{self.crt.freq_vertical:.1f}"
        elif slider == self.freq_horizontal_slider:
            return f"{self.crt.freq_horizontal:.1f}"
        return "0"
    
    def draw_gradient_rect(self, surface, rect, color1, color2, vertical=True):
        """Dibuja un rectángulo con gradiente"""
        if vertical:
            for y in range(rect.height):
                t = y / rect.height
                r = int(color1[0] * (1-t) + color2[0] * t)
                g = int(color1[1] * (1-t) + color2[1] * t)
                b = int(color1[2] * (1-t) + color2[2] * t)
                pygame.draw.line(surface, (r, g, b), 
                               (rect.x, rect.y + y), (rect.x + rect.width, rect.y + y))
        else:
            for x in range(rect.width):
                t = x / rect.width
                r = int(color1[0] * (1-t) + color2[0] * t)
                g = int(color1[1] * (1-t) + color2[1] * t)
                b = int(color1[2] * (1-t) + color2[2] * t)
                pygame.draw.line(surface, (r, g, b), 
                               (rect.x + x, rect.y), (rect.x + x, rect.y + rect.height))
    
    def draw_slider(self, slider, enabled=True):
        """Dibuja un slider con diseño moderno y simple"""
        # Label con mejor tipografía
        label_color = self.crt.DARK_GRAY if enabled else self.crt.GRAY
        label_surface = self.crt.font_small.render(slider['label'], True, label_color)
        self.crt.screen.blit(label_surface, (slider['rect'].x, slider['rect'].y - 20))
        
        # Valor actual en el lado derecho
        value_text = f"{self.get_slider_value(slider)} {slider['unit']}"
        value_surface = self.crt.font_tiny.render(value_text, True, label_color)
        value_rect = value_surface.get_rect()
        value_rect.topright = (slider['rect'].right, slider['rect'].y - 20)
        self.crt.screen.blit(value_surface, value_rect)
        
        # Track del slider con diseño elegante
        track_rect = slider['rect'].copy()
        track_rect.height = 8
        track_rect.y += 6  # Centrar verticalmente
        
        # Track de fondo
        track_bg_color = self.crt.MEDIUM_GRAY if enabled else self.crt.LIGHT_GRAY
        self.crt.draw_rounded_rect(self.crt.screen, track_bg_color, track_rect, 4)
        
        if self.crt.paused:
            enabled = False
        
        # Track activo (parte llena)
        if enabled and slider['value'] > 0:
            active_width = int(slider['value'] * track_rect.width)
            active_rect = pygame.Rect(track_rect.x, track_rect.y, active_width, track_rect.height)
            
            # Color del slider
            slider_color = slider['color']
            self.crt.draw_rounded_rect(self.crt.screen, slider_color, active_rect, 4)
            
            # Efecto de brillo sutil en el track activo
            highlight_rect = pygame.Rect(active_rect.x, active_rect.y, active_rect.width, 2)
            highlight_color = tuple(min(255, c + 40) for c in slider_color)
            self.crt.draw_rounded_rect(self.crt.screen, highlight_color, highlight_rect, 2)
        
        # Handle del slider (perilla)
        if enabled:
            handle_x = slider['rect'].x + slider['value'] * slider['rect'].width
            handle_y = slider['rect'].y + slider['rect'].height // 2
            
            # Handle principal simple
            handle_center = (int(handle_x), handle_y)
            
            # Círculo exterior blanco
            pygame.draw.circle(self.crt.screen, self.crt.WHITE, handle_center, 10)
            pygame.draw.circle(self.crt.screen, slider['color'], handle_center, 10, 3)
            
            # Círculo interior con color del slider
            pygame.draw.circle(self.crt.screen, slider['color'], handle_center, 6)
            
            # Punto central blanco
            pygame.draw.circle(self.crt.screen, self.crt.WHITE, handle_center, 2)
    
    def draw_scale_marks(self, slider):
        """Dibuja marcas de escala en sliders importantes"""
        track_rect = slider['rect'].copy()
        track_rect.height = 8
        track_rect.y += 6
        
        # Dibujar 5 marcas de escala
        for i in range(5):
            x = track_rect.x + (i / 4) * track_rect.width
            y1 = track_rect.bottom + 3
            y2 = y1 + 5
            
            pygame.draw.line(self.crt.screen, self.crt.GRAY, (x, y1), (x, y2), 1)
            
            # Etiquetas para valores extremos
            if i == 0:
                if slider == self.acceleration_slider:
                    text = "0V"
                elif slider == self.persistence_slider:
                    text = "0.1s"
                text_surface = self.crt.font_tiny.render(text, True, self.crt.GRAY)
                text_rect = text_surface.get_rect()
                text_rect.centerx = int(x)
                text_rect.top = y2 + 2
                self.crt.screen.blit(text_surface, text_rect)
            elif i == 4:
                if slider == self.acceleration_slider:
                    text = "1000V"
                elif slider == self.persistence_slider:
                    text = "10s"
                text_surface = self.crt.font_tiny.render(text, True, self.crt.GRAY)
                text_rect = text_surface.get_rect()
                text_rect.centerx = int(x)
                text_rect.top = y2 + 2
                self.crt.screen.blit(text_surface, text_rect)