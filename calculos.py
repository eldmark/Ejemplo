import math

class Calculos:
    def __init__(self, crt_simulation):
        self.crt = crt_simulation
    
    def calculate_electron_position(self):
        """Calcula la posición del electrón en la pantalla del CRT"""
        if self.crt.current_mode.value == "Manual":
            # En modo manual, la posición es directamente proporcional al voltaje
            x_deflection = (self.crt.horizontal_voltage / self.crt.max_deflection_voltage) * (self.crt.crt_screen_size / 2)
            y_deflection = (self.crt.vertical_voltage / self.crt.max_deflection_voltage) * (self.crt.crt_screen_size / 2)
        else:
            # En modo Lissajous, usar funciones sinusoidales
            x_deflection = (self.crt.crt_screen_size / 2.2) * math.sin(2 * math.pi * self.crt.freq_horizontal * self.crt.time + self.crt.phase_horizontal)
            y_deflection = (self.crt.crt_screen_size / 2.2) * math.sin(2 * math.pi * self.crt.freq_vertical * self.crt.time + self.crt.phase_vertical)
        
        # Convertir a coordenadas de pantalla
        screen_x = self.crt.crt_screen_x + self.crt.crt_screen_size // 2 + x_deflection
        screen_y = self.crt.crt_screen_y + self.crt.crt_screen_size // 2 - y_deflection  # Y invertida
        
        return int(screen_x), int(screen_y)