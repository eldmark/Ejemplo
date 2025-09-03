# Simulación de un Tubo de Rayos Catódicos (CRT)

Este proyecto es una simulación interactiva de un Tubo de Rayos Catódicos (CRT) desarrollada en Python utilizando la biblioteca Pygame.

## ¿Qué se hizo?

- Se implementó una interfaz gráfica que simula el funcionamiento de un CRT, permitiendo visualizar y manipular el comportamiento del haz de electrones.
- Se incluyeron dos modos de operación:
  - **Modo Manual:** Permite controlar manualmente los voltajes de deflexión vertical y horizontal, así como el voltaje de aceleración y la persistencia.
  - **Modo Lissajous:** Permite generar figuras de Lissajous variando las frecuencias de los voltajes de deflexión, con una cuadrícula para seleccionar diferentes proporciones de frecuencia.
- Se agregaron controles deslizantes (sliders) y botones para cambiar de modo, reiniciar la simulación y ajustar los parámetros físicos.
- Se visualizan las trayectorias del haz de electrones en vistas lateral, superior y en la pantalla del CRT, con persistencia configurable.

## Requisitos
- Python 3.x
- Pygame

## Ejecución

1. Instala las dependencias:
   ```bash
   pip install pygame
   ```
2. Ejecuta el archivo principal:
   ```bash
   python main.py
   ```

## Autor
- [Tu Nombre]
