import pygame
import math

class Visualization:
    def __init__(self, crt_simulation):
        self.crt = crt_simulation
    
    def draw_glass_effect(self, surface, rect, alpha=30):
        """Dibuja un efecto de vidrio sobre un rectángulo"""
        glass_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # Gradiente de arriba hacia abajo
        for i in range(rect.height):
            alpha_val = int(alpha * (1 - i / rect.height))
            color = (255, 255, 255, alpha_val)
            pygame.draw.line(glass_surface, color, (0, i), (rect.width, i))
        
        surface.blit(glass_surface, rect.topleft)
    
    def draw_crt_views(self):
        """Dibuja las vistas lateral y superior del CRT con diseño moderno"""
        # Vista lateral
        lateral_rect = pygame.Rect(400, 100, 300, 150)
        self.crt.draw_rounded_rect(self.crt.screen, self.crt.WHITE, lateral_rect, 12)
        self.crt.draw_rounded_rect(self.crt.screen, self.crt.WHITE, lateral_rect, 12)
        pygame.draw.rect(self.crt.screen, self.crt.DARK_GRAY, lateral_rect, 2, border_radius=12)
    
        
        # Placas verticales en vista lateral
        plate_top = pygame.Rect(450, 120, 80, 10)
        plate_bottom = pygame.Rect(450, 210, 80, 10)
        self.crt.draw_rounded_rect(self.crt.screen, self.crt.PRIMARY_BLUE, plate_top, 3)
        self.crt.draw_rounded_rect(self.crt.screen, self.crt.DANGER_RED, plate_bottom, 3)
        
        # Trayectoria del electrón en vista lateral
        if self.crt.current_mode.value == "Manual":
            y_offset = (self.crt.vertical_voltage / self.crt.max_deflection_voltage) * 40
        else:
            y_offset = 20 * math.sin(2 * math.pi * self.crt.freq_vertical * self.crt.time)
        
        start_pos = (420, 175)
        end_pos = (680, 175 - y_offset)
        
        # Línea con gradiente
        self.draw_gradient_line(start_pos, end_pos, self.crt.SUCCESS_GREEN, self.crt.ELECTRON_YELLOW, 4)
        
        # Punto del electrón con brillo
        self.draw_glowing_circle(end_pos, self.crt.ELECTRON_YELLOW, 5, 15)
        
        # Label
        label = self.crt.font_medium.render("Vista Lateral", True, self.crt.DARK_GRAY)
        self.crt.screen.blit(label, (lateral_rect.x + 15, lateral_rect.y - 28))
        
        # Vista superior
        superior_rect = pygame.Rect(800, 100, 300, 150)
        self.crt.draw_rounded_rect(self.crt.screen, self.crt.WHITE, superior_rect, 12)
        pygame.draw.rect(self.crt.screen, self.crt.DARK_GRAY, superior_rect, 2, border_radius=12)
        
        
        # Placas horizontales en vista superior
        center_y = superior_rect.centery
        plate_width = 80

        plate_top = pygame.Rect(superior_rect.centerx - plate_width // 2, center_y - 40, plate_width, 10)
        plate_bottom = pygame.Rect(superior_rect.centerx - plate_width // 2, center_y + 30, plate_width, 10)
        self.crt.draw_rounded_rect(self.crt.screen, self.crt.PRIMARY_BLUE, plate_top, 3)
        self.crt.draw_rounded_rect(self.crt.screen, self.crt.DANGER_RED, plate_bottom, 3)
        
        # Trayectoria del electrón en vista superior
        if self.crt.current_mode.value == "Manual":
            x_offset = (self.crt.horizontal_voltage / self.crt.max_deflection_voltage) * 40
        else:
            x_offset = 20 * math.sin(2 * math.pi * self.crt.freq_horizontal * self.crt.time)
        
        start_pos = (820, center_y)
        end_pos = (1080, center_y + x_offset)
        
        # Línea con gradiente
        self.draw_gradient_line(start_pos, end_pos, self.crt.SUCCESS_GREEN, self.crt.ELECTRON_YELLOW, 4)
        
        # Punto del electrón con brillo
        self.draw_glowing_circle(end_pos, self.crt.ELECTRON_YELLOW, 5, 15)
        
        # Label
        label = self.crt.font_medium.render("Vista Superior", True, self.crt.DARK_GRAY)
        self.crt.screen.blit(label, (superior_rect.x + 15, superior_rect.y - 28))
    
    def draw_gradient_line(self, start_pos, end_pos, start_color, end_color, width):
        """Dibuja una línea con gradiente de color"""
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return
        
        segments = int(distance // 2) + 1
        for i in range(segments):
            t = i / max(segments - 1, 1)
            
            # Interpolación de color
            r = int(start_color[0] * (1 - t) + end_color[0] * t)
            g = int(start_color[1] * (1 - t) + end_color[1] * t)
            b = int(start_color[2] * (1 - t) + end_color[2] * t)
            
            # Posición actual
            x = int(start_pos[0] + dx * t)
            y = int(start_pos[1] + dy * t)
            
            # Siguiente posición
            next_t = min(1.0, (i + 1) / max(segments - 1, 1))
            next_x = int(start_pos[0] + dx * next_t)
            next_y = int(start_pos[1] + dy * next_t)
            
            pygame.draw.line(self.crt.screen, (r, g, b), (x, y), (next_x, next_y), width)
    
    def draw_glowing_circle(self, pos, color, radius, glow_radius):
        """Dibuja un círculo con efecto de brillo"""
        # Dibujar múltiples círculos con alpha decreciente para simular brillo
        for i in range(glow_radius, 0, -2):
            alpha = max(0, int(100 * (1 - i / glow_radius)))
            glow_color = (*color[:3], alpha)
            
            glow_surface = pygame.Surface((i * 2, i * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, glow_color, (i, i), i)
            self.crt.screen.blit(glow_surface, (pos[0] - i, pos[1] - i))
        
        # Círculo principal
        pygame.draw.circle(self.crt.screen, color, pos, radius)
        pygame.draw.circle(self.crt.screen, self.crt.WHITE, pos, radius // 2)
    
    def draw_crt_screen(self):
        """Dibuja la pantalla del CRT con efectos modernos"""
        
        if self.crt.paused:
            # Dibujar overlay semi-transparente de pausa
            pause_overlay = pygame.Surface((self.crt.crt_screen_size, self.crt.crt_screen_size), pygame.SRCALPHA)
            pause_overlay.fill((0, 0, 0, 100))  # Negro semi-transparente
            self.crt.screen.blit(pause_overlay, (self.crt.crt_screen_x, self.crt.crt_screen_y))
            
            # Texto de pausa
            pause_text = self.crt.font_large.render("PAUSADO", True, self.crt.WHITE)
            text_rect = pause_text.get_rect(center=(self.crt.crt_screen_x + self.crt.crt_screen_size//2, 
                                                self.crt.crt_screen_y + self.crt.crt_screen_size//2))
            self.crt.screen.blit(pause_text, text_rect)
            
        # Pantalla principal
        crt_rect = pygame.Rect(self.crt.crt_screen_x, self.crt.crt_screen_y, 
                              self.crt.crt_screen_size, self.crt.crt_screen_size)
        
        # Fondo de la pantalla CRT
        self.crt.draw_rounded_rect(self.crt.screen, self.crt.BLACK, crt_rect, 15)
        
        # Borde exterior
        border_rect = pygame.Rect(crt_rect.x - 8, crt_rect.y - 8, 
                                 crt_rect.width + 16, crt_rect.height + 16)
        self.crt.draw_rounded_rect(self.crt.screen, self.crt.DARK_GRAY, border_rect, 20)
        self.crt.draw_rounded_rect(self.crt.screen, self.crt.BLACK, crt_rect, 15)
        
        # Grid en la pantalla
        grid_color = (20, 40, 20)
        for i in range(10, self.crt.crt_screen_size, 20):
            pygame.draw.line(self.crt.screen, grid_color, 
                           (crt_rect.x + i, crt_rect.y), 
                           (crt_rect.x + i, crt_rect.y + self.crt.crt_screen_size), 1)
            pygame.draw.line(self.crt.screen, grid_color, 
                           (crt_rect.x, crt_rect.y + i), 
                           (crt_rect.x + self.crt.crt_screen_size, crt_rect.y + i), 1)
        
        # Puntos del electrón con fade y brillo
        current_time = pygame.time.get_ticks() / 1000.0
        for pos, timestamp in self.crt.electron_points:
            if self.crt.paused:
                # DURANTE PAUSA: Mostrar todos los puntos con alpha completo
                alpha = 1.0  # ← Alpha máximo durante pausa
            else:
                # Durante ejecución: cálculo normal de persistencia
                age = current_time - timestamp
                alpha = max(0, 1 - (age / self.crt.persistence_time))
            
            if alpha > 0:
                brightness = int(255 * alpha)
                
                # Efecto de brillo
                if brightness > 50:
                    self.draw_glowing_circle(pos, (brightness, brightness, 0), 2, 8)
                else:
                    pygame.draw.circle(self.crt.screen, (brightness, brightness, 0), pos, 1)
                
        # Label 
        label_text = "Pantalla del CRT"
        label = self.crt.font_medium.render(label_text, True, self.crt.DARK_GRAY)
        self.crt.screen.blit(label, (self.crt.crt_screen_x + 10, self.crt.crt_screen_y - 30))
    
    def draw_grid(self):
        """Dibuja el grid de proporciones de Lissajous con diseño moderno"""
        if self.crt.current_mode.value != "Lissajous":
            return
        
        # Título 
        title_text = "Ratios de Frecuencia"
        title = self.crt.font_medium.render(title_text, True, self.crt.DARK_GRAY)
        
        self.crt.screen.blit(title, (950, 315))
        
        # Contenedor del grid con sombra
        grid_container = pygame.Rect(950, 335, 245, 305)
        self.crt.draw_rounded_rect(self.crt.screen, self.crt.WHITE, grid_container, 12)
        pygame.draw.rect(self.crt.screen, self.crt.MEDIUM_GRAY, grid_container, 2, border_radius=12)
        
        # Grid de ratios
        for i, ratio in enumerate(self.crt.lissajous_ratios):
            if i >= 20:  # 4x5 grid
                break
            
            row = i // 4
            col = i % 4
            
            x = 955 + col * 60
            y = 340 + row * 60
            
            cell_rect = pygame.Rect(x, y, 55, 55)
            
            # Efecto hover
            if i == self.crt.selected_ratio_index:
                # Sombra para celda seleccionada
                shadow_rect = cell_rect.copy()
                shadow_rect.x += 2
                shadow_rect.y += 2
                self.crt.draw_rounded_rect(self.crt.screen, (0, 0, 0, 30), shadow_rect, 8)
                
                # Celda seleccionada con gradiente
                self.crt.draw_rounded_rect(self.crt.screen, self.crt.PRIMARY_BLUE, cell_rect, 8)
                self.draw_glass_effect(self.crt.screen, cell_rect, 40)
                text_color = self.crt.WHITE
            else:
                # Celda normal
                self.crt.draw_rounded_rect(self.crt.screen, self.crt.LIGHT_GRAY, cell_rect, 8)
                text_color = self.crt.DARK_GRAY
                
                # Efecto
                mouse_pos = pygame.mouse.get_pos()
                if cell_rect.collidepoint(mouse_pos):
                    hover_surface = pygame.Surface(cell_rect.size, pygame.SRCALPHA)
                    hover_surface.fill((*self.crt.PRIMARY_BLUE[:3], 30))
                    self.crt.screen.blit(hover_surface, cell_rect.topleft)
            
            pygame.draw.rect(self.crt.screen, self.crt.DARK_GRAY, cell_rect, 1, border_radius=8)
            
            # Texto del ratio
            ratio_text = f"{ratio[0]}:{ratio[1]}"
            text_surface = self.crt.font_small.render(ratio_text, True, text_color)
            text_rect = text_surface.get_rect(center=cell_rect.center)
            self.crt.screen.blit(text_surface, text_rect)
    
    def draw_control_panel(self):
        """Dibuja el panel de control """
        # Fondo del panel
        control_panel_rect = pygame.Rect(20, 10, self.crt.control_panel_width, 680)
        
        # Panel principal 
        self.crt.draw_rounded_rect(self.crt.screen, self.crt.WHITE, control_panel_rect, 15)
        pygame.draw.rect(self.crt.screen, self.crt.DARK_GRAY, control_panel_rect, 2, border_radius=15)
        
        
        # Título
        title_rect = pygame.Rect(30, 25, self.crt.control_panel_width - 20, 50)
        self.crt.draw_rounded_rect(self.crt.screen, self.crt.PRIMARY_BLUE, title_rect, 10)
        self.draw_glass_effect(self.crt.screen, title_rect, 50)
        
        title = self.crt.font_title.render("CONTROLES CRT", True, self.crt.WHITE)
        title_text_rect = title.get_rect(center=title_rect.center)
        self.crt.screen.blit(title, title_text_rect)
        
        # Sliders
        self.crt.slider_manager.draw_slider(self.crt.slider_manager.acceleration_slider, True)
        self.crt.slider_manager.draw_slider(self.crt.slider_manager.vertical_slider, self.crt.current_mode.value == "Manual")
        self.crt.slider_manager.draw_slider(self.crt.slider_manager.horizontal_slider, self.crt.current_mode.value == "Manual")
        self.crt.slider_manager.draw_slider(self.crt.slider_manager.persistence_slider, True)
        self.crt.slider_manager.draw_slider(self.crt.slider_manager.freq_vertical_slider, self.crt.current_mode.value == "Lissajous")
        self.crt.slider_manager.draw_slider(self.crt.slider_manager.freq_horizontal_slider, self.crt.current_mode.value == "Lissajous")
        
        # Botones de modo
        manual_active = self.crt.current_mode.value == "Manual"
        lissajous_active = self.crt.current_mode.value == "Lissajous"
        
        # Botón Manual
        if manual_active:
            self.crt.draw_rounded_rect(self.crt.screen, self.crt.SUCCESS_GREEN, self.crt.slider_manager.manual_button, 10)
        else:
            self.crt.draw_rounded_rect(self.crt.screen, self.crt.LIGHT_GRAY, self.crt.slider_manager.manual_button, 10)
        
        pygame.draw.rect(self.crt.screen, self.crt.DARK_GRAY, self.crt.slider_manager.manual_button, 2, border_radius=10)
        
        # Botón Lissajous
        if lissajous_active:
            self.crt.draw_rounded_rect(self.crt.screen, self.crt.WARNING_ORANGE, self.crt.slider_manager.lissajous_button, 10)
        else:
            self.crt.draw_rounded_rect(self.crt.screen, self.crt.LIGHT_GRAY, self.crt.slider_manager.lissajous_button, 10)
        
        pygame.draw.rect(self.crt.screen, self.crt.DARK_GRAY, self.crt.slider_manager.lissajous_button, 2, border_radius=10)
        
        # Botón reset 
        self.crt.draw_rounded_rect(self.crt.screen, self.crt.DANGER_RED, self.crt.slider_manager.reset_button, 8)
        pygame.draw.rect(self.crt.screen, self.crt.DARK_GRAY, self.crt.slider_manager.reset_button, 2, border_radius=6)
        
        # Texto de botones 
        manual_text_color = self.crt.WHITE if manual_active else self.crt.DARK_GRAY
        lissajous_text_color = self.crt.WHITE if lissajous_active else self.crt.DARK_GRAY
        
        manual_text = self.crt.font_medium.render("Modo Manual", True, manual_text_color)
        manual_rect = manual_text.get_rect(center=self.crt.slider_manager.manual_button.center)
        self.crt.screen.blit(manual_text, manual_rect)
        
        lissajous_text = self.crt.font_small.render("Modo Lissajous", True, lissajous_text_color)
        lissajous_rect = lissajous_text.get_rect(center=self.crt.slider_manager.lissajous_button.center)
        self.crt.screen.blit(lissajous_text, lissajous_rect)
        
        reset_text = self.crt.font_small.render("Reset", True, self.crt.WHITE)
        reset_rect = reset_text.get_rect(center=self.crt.slider_manager.reset_button.center)
        self.crt.screen.blit(reset_text, reset_rect)
        
        # Panel de estado 
        y_offset = 500
        state_panel = pygame.Rect(30, y_offset, self.crt.control_panel_width - 20, 180)
        self.crt.draw_rounded_rect(self.crt.screen, self.crt.LIGHT_GRAY, state_panel, 12)
        pygame.draw.rect(self.crt.screen, self.crt.MEDIUM_GRAY, state_panel, 1, border_radius=12)
        
        # Título del estado
        state_title_rect = pygame.Rect(40, y_offset + 10, 100, 25)
        self.crt.draw_rounded_rect(self.crt.screen, self.crt.SECONDARY_BLUE, state_title_rect, 6)
        state_title = self.crt.font_medium.render("ESTADO", True, self.crt.WHITE)
        state_title_text_rect = state_title.get_rect(center=state_title_rect.center)
        self.crt.screen.blit(state_title, state_title_text_rect)
        
        # Estado de pausa
        pause_y = y_offset + 15
        pause_text = f"PAUSA: {'ACTIVADA' if self.crt.paused else 'DESACTIVADA'}"
        pause_surface = self.crt.font_small.render(pause_text, True, 
                                                self.crt.DANGER_RED if self.crt.paused else self.crt.SUCCESS_GREEN)
        self.crt.screen.blit(pause_surface, (170, pause_y))
        
        # Valores actuales con iconos de colores
        values = [
            ("Aceleración", f"{self.crt.acceleration_voltage:.0f} V", self.crt.PRIMARY_BLUE),
            ("Vertical", f"{self.crt.vertical_voltage:.1f} V", self.crt.SUCCESS_GREEN),
            ("Horizontal", f"{self.crt.horizontal_voltage:.1f} V", self.crt.DANGER_RED),
            ("Persistencia", f"{self.crt.persistence_time:.1f} s", self.crt.GRAY)
        ]
        
        if self.crt.current_mode.value == "Lissajous":
            values.extend([
                ("Freq V", f"{self.crt.freq_vertical:.1f} Hz", self.crt.WARNING_ORANGE),
                ("Freq H", f"{self.crt.freq_horizontal:.1f} Hz", self.crt.WARNING_ORANGE)
            ])
        
        for i, (label, value, color) in enumerate(values):
            value_y = y_offset + 45 + i * 22
            
            # Indicador de color
            color_indicator = pygame.Rect(45, value_y + 3, 8, 12)
            self.crt.draw_rounded_rect(self.crt.screen, color, color_indicator, 2)
            
            # Texto del valor
            label_text = self.crt.font_tiny.render(f"{label}:", True, self.crt.GRAY)
            value_text = self.crt.font_small.render(value, True, self.crt.DARK_GRAY)
            
            self.crt.screen.blit(label_text, (60, value_y))
            self.crt.screen.blit(value_text, (150, value_y))