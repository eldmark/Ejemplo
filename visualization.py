import pygame
import math

class Visualization:
    def __init__(self, crt_simulation):
        self.crt = crt_simulation
    
    def draw_crt_views(self):
        """Dibuja las vistas lateral y superior del CRT"""
        # Vista lateral
        lateral_rect = pygame.Rect(400, 100, 300, 150)
        pygame.draw.rect(self.crt.screen, self.crt.LIGHT_GRAY, lateral_rect)
        pygame.draw.rect(self.crt.screen, self.crt.BLACK, lateral_rect, 2)
        
        # Placas verticales en vista lateral
        plate_top = pygame.Rect(450, 120, 80, 8)
        plate_bottom = pygame.Rect(450, 212, 80, 8)
        pygame.draw.rect(self.crt.screen, self.crt.GRAY, plate_top)
        pygame.draw.rect(self.crt.screen, self.crt.GRAY, plate_bottom)
        
        # Trayectoria del electrón en vista lateral
        if self.crt.current_mode.value == "Manual":
            y_offset = (self.crt.vertical_voltage / self.crt.max_deflection_voltage) * 40
        else:
            y_offset = 20 * math.sin(2 * math.pi * self.crt.freq_vertical * self.crt.time)
        
        start_pos = (420, 175)
        end_pos = (680, 175 - y_offset)
        pygame.draw.line(self.crt.screen, self.crt.GREEN, start_pos, end_pos, 3)
        pygame.draw.circle(self.crt.screen, self.crt.YELLOW, end_pos, 4)
        
        # Label
        label = self.crt.font_medium.render("Vista Lateral", True, self.crt.BLACK)
        self.crt.screen.blit(label, (lateral_rect.x + 10, lateral_rect.y - 25))
        
        # Vista superior
        superior_rect = pygame.Rect(800, 100, 300, 150)
        pygame.draw.rect(self.crt.screen, self.crt.LIGHT_GRAY, superior_rect)
        pygame.draw.rect(self.crt.screen, self.crt.BLACK, superior_rect, 2)
        
        # Placas horizontales en vista superior (centradas)
        center_y = superior_rect.centery  # Centro vertical del rectángulo
        plate_height = 80
        
        plate_left = pygame.Rect(850, center_y - plate_height // 2, 8, plate_height)
        plate_right = pygame.Rect(1042, center_y - plate_height // 2, 8, plate_height)
        pygame.draw.rect(self.crt.screen, self.crt.GRAY, plate_left)
        pygame.draw.rect(self.crt.screen, self.crt.GRAY, plate_right)
        
        # Trayectoria del electrón en vista superior
        if self.crt.current_mode.value == "Manual":
            x_offset = (self.crt.horizontal_voltage / self.crt.max_deflection_voltage) * 40
        else:
            x_offset = 20 * math.sin(2 * math.pi * self.crt.freq_horizontal * self.crt.time)
        
        start_pos = (820, center_y)
        end_pos = (1080, center_y + x_offset)
        pygame.draw.line(self.crt.screen, self.crt.GREEN, start_pos, end_pos, 3)
        pygame.draw.circle(self.crt.screen, self.crt.YELLOW, end_pos, 4)
        
        # Label
        label = self.crt.font_medium.render("Vista Superior", True, self.crt.BLACK)
        self.crt.screen.blit(label, (superior_rect.x + 10, superior_rect.y - 25))
    
    def draw_crt_screen(self):
        """Dibuja la pantalla del CRT"""
        # Pantalla principal
        crt_rect = pygame.Rect(self.crt.crt_screen_x, self.crt.crt_screen_y, self.crt.crt_screen_size, self.crt.crt_screen_size)
        pygame.draw.rect(self.crt.screen, self.crt.BLACK, crt_rect)
        pygame.draw.rect(self.crt.screen, self.crt.GREEN, crt_rect, 2)
        
        # Puntos del electrón con fade basado en persistencia
        current_time = pygame.time.get_ticks() / 1000.0
        for pos, timestamp in self.crt.electron_points:
            age = current_time - timestamp
            alpha = max(0, 1 - (age / self.crt.persistence_time))
            
            # Crear color con alpha
            brightness = int(255 * alpha)
            color = (brightness, brightness, 0)  # Amarillo que se desvanece
            
            if brightness > 0:
                pygame.draw.circle(self.crt.screen, color, pos, 2)
        
        # Label
        label = self.crt.font_medium.render("Pantalla del CRT (LISSAJOUS)", True, self.crt.BLACK)
        self.crt.screen.blit(label, (self.crt.crt_screen_x, self.crt.crt_screen_y - 25))
    
    def draw_grid(self):
        """Dibuja el grid de proporciones de Lissajous"""
        if self.crt.current_mode.value != "Lissajous":
            return
        
        # Título
        title = self.crt.font_medium.render("Ratios de Frecuencia", True, self.crt.BLACK)
        self.crt.screen.blit(title, (1000, 450 - 30))
        
        # Grid
        for i, ratio in enumerate(self.crt.lissajous_ratios):
            if i >= 24:  # 6x4 grid
                break
            
            row = i // 6
            col = i % 6
            
            x = 1000 + col * 60
            y = 450 + row * 60
            
            cell_rect = pygame.Rect(x, y, 60 - 2, 60 - 2)
            
            # Color de fondo
            if i == self.crt.selected_ratio_index:
                pygame.draw.rect(self.crt.screen, self.crt.BLUE, cell_rect)
            else:
                pygame.draw.rect(self.crt.screen, self.crt.LIGHT_GRAY, cell_rect)
            
            pygame.draw.rect(self.crt.screen, self.crt.BLACK, cell_rect, 1)
            
            # Texto del ratio
            ratio_text = f"{ratio[0]}:{ratio[1]}"
            text_surface = self.crt.font_small.render(ratio_text, True, self.crt.BLACK)
            text_rect = text_surface.get_rect(center=cell_rect.center)
            self.crt.screen.blit(text_surface, text_rect)
    
    def draw_control_panel(self):
        """Dibuja el panel de control"""
        # Fondo del panel
        control_panel_rect = pygame.Rect(20, 20, self.crt.control_panel_width, 760)
        pygame.draw.rect(self.crt.screen, self.crt.LIGHT_GRAY, control_panel_rect)
        pygame.draw.rect(self.crt.screen, self.crt.BLACK, control_panel_rect, 2)
        
        # Título
        title = self.crt.font_large.render("CONTROLES CRT", True, self.crt.BLACK)
        self.crt.screen.blit(title, (40, 40))
        
        # Sliders
        self.crt.slider_manager.draw_slider(self.crt.slider_manager.acceleration_slider, True)
        self.crt.slider_manager.draw_slider(self.crt.slider_manager.vertical_slider, self.crt.current_mode.value == "Manual")
        self.crt.slider_manager.draw_slider(self.crt.slider_manager.horizontal_slider, self.crt.current_mode.value == "Manual")
        self.crt.slider_manager.draw_slider(self.crt.slider_manager.persistence_slider, True)
        self.crt.slider_manager.draw_slider(self.crt.slider_manager.freq_vertical_slider, self.crt.current_mode.value == "Lissajous")
        self.crt.slider_manager.draw_slider(self.crt.slider_manager.freq_horizontal_slider, self.crt.current_mode.value == "Lissajous")
        
        # Botones de modo
        manual_color = self.crt.ORANGE if self.crt.current_mode.value == "Manual" else self.crt.GRAY
        lissajous_color = self.crt.ORANGE if self.crt.current_mode.value == "Lissajous" else self.crt.GRAY
        
        pygame.draw.rect(self.crt.screen, manual_color, self.crt.slider_manager.manual_button)
        pygame.draw.rect(self.crt.screen, self.crt.BLACK, self.crt.slider_manager.manual_button, 2)
        
        pygame.draw.rect(self.crt.screen, lissajous_color, self.crt.slider_manager.lissajous_button)
        pygame.draw.rect(self.crt.screen, self.crt.BLACK, self.crt.slider_manager.lissajous_button, 2)
        
        # Botón reset
        pygame.draw.rect(self.crt.screen, self.crt.RED, self.crt.slider_manager.reset_button)
        pygame.draw.rect(self.crt.screen, self.crt.BLACK, self.crt.slider_manager.reset_button, 2)
        
        # Texto de botones
        manual_text = self.crt.font_medium.render("Modo Manual", True, self.crt.BLACK)
        manual_rect = manual_text.get_rect(center=self.crt.slider_manager.manual_button.center)
        self.crt.screen.blit(manual_text, manual_rect)
        
        lissajous_text = self.crt.font_small.render("Modo Lissajous", True, self.crt.BLACK)
        lissajous_rect = lissajous_text.get_rect(center=self.crt.slider_manager.lissajous_button.center)
        self.crt.screen.blit(lissajous_text, lissajous_rect)
        
        reset_text = self.crt.font_small.render("Reset", True, self.crt.BLACK)
        reset_rect = reset_text.get_rect(center=self.crt.slider_manager.reset_button.center)
        self.crt.screen.blit(reset_text, reset_rect)
        
        # Estado actual
        y_offset = 560
        state_title = self.crt.font_medium.render("ESTADO", True, self.crt.BLACK)
        self.crt.screen.blit(state_title, (40, y_offset))
        
        mode_text = f"MODO: {self.crt.current_mode.value.upper()}"
        mode_surface = self.crt.font_small.render(mode_text, True, self.crt.BLACK)
        self.crt.screen.blit(mode_surface, (40, y_offset + 30))
        
        # Valores actuales
        values = [
            f"Aceleración: {self.crt.acceleration_voltage:.0f} V",
            f"Vertical: {self.crt.vertical_voltage:.1f} V",
            f"Horizontal: {self.crt.horizontal_voltage:.1f} V",
            f"Persistencia: {self.crt.persistence_time:.1f} s"
        ]
        
        if self.crt.current_mode.value == "Lissajous":
            values.extend([
                f"Freq V: {self.crt.freq_vertical:.1f} Hz",
                f"Freq H: {self.crt.freq_horizontal:.1f} Hz"
            ])
        
        for i, value in enumerate(values):
            text_surface = self.crt.font_small.render(value, True, self.crt.BLACK)
            self.crt.screen.blit(text_surface, (40, y_offset + 60 + i * 20))