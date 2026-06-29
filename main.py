from manim import *
import numpy as np

class FourierLatexR(Scene):
    def construct(self):
        # 1. Parámetros de la animación
        n_vectores = 60  # Más vectores = Mayor precisión para las curvas de la R
        tiempo_animacion = 10
        
        # 2. Obtener los puntos de la letra R de LaTeX
        # Usamos Tex con el símbolo de los números reales
        letra_latex = Tex(r"$\mathbb{R}$", font_size=540)
        
        # Extraemos los puntos vectoriales del primer submobject directamente
        puntos_path = letra_latex[0].get_all_points()
        
        # Convertimos los puntos de Manim (x, y, z) a números complejos (x + iy)
        # Filtramos duplicados consecutivos para limpiar la trayectoria
        puntos_r = []
        for p in puntos_path:
            c = complex(p[0], p[1])
            if not puntos_r or np.abs(puntos_r[-1] - c) > 0.01:
                puntos_r.append(c)
                
        # Aseguramos que la trayectoria sea un ciclo cerrado para Fourier
        if puntos_r:
            puntos_r.append(puntos_r[0])

        # 3. Calcular la Transformada Discreta de Fourier (DFT)
        N = len(puntos_r)
        fourier_coeffs = []
        
        for k in range(-n_vectores // 2, n_vectores // 2):
            coef = sum(puntos_r[n] * np.exp(-1j * 2 * np.pi * k * n / N) for n in range(N)) / N
            fourier_coeffs.append((abs(coef), np.angle(coef), k))
            
        # Ordenamos los círculos de mayor a menor tamaño para estabilidad visual
        fourier_coeffs.sort(key=lambda x: x[0], reverse=True)

        # 4. Estructura de vectores y rastro de Manim
        vectores_y_circulos = VGroup()
        
        # Punto invisible en la punta del último vector que dejará el rastro
        punta_movil = Dot(radius=0, fill_opacity=0)
        self.add(punta_movil)
        
        # TracedPath sigue automáticamente a 'punta_movil' sin dar errores de curvas
        rastro = TracedPath(punta_movil.get_center, stroke_color=YELLOW, stroke_width=2)
        
        tiempo = ValueTracker(0)

        def actualizar_epiciclos(mob):
            mob.submobjects.clear()
            centro = ORIGIN
            t = tiempo.get_value()
            
            for radio, fase, k in fourier_coeffs:
                angulo = k * t + fase
                siguiente_centro = centro + np.array([radio * np.cos(angulo), radio * np.sin(angulo), 0])
                
                # Dibujamos solo los círculos relativamente visibles para no saturar la pantalla
                if radio > 0.02:
                    circulo = Circle(radius=radio, color=BLUE, stroke_opacity=0.15)
                    circulo.move_to(centro)
                    mob.add(circulo)
                
                # Vector de Euler (flecha)
                vector = Line(centro, siguiente_centro, color=WHITE, stroke_width=0.5, buff=0)
                vector.add_tip(tip_width=0.05, tip_length=0.05)
                mob.add(vector)
                
                centro = siguiente_centro
                
            # Movemos el punto invisible a la punta final de la cadena de vectores
            punta_movil.move_to(centro)

        vectores_y_circulos.add_updater(actualizar_epiciclos)

        # 5. Renderizar la Escena
        self.add(vectores_y_circulos, rastro)
        
        # Hacemos que el tiempo vaya de 0 a 2pi para completar un ciclo de dibujo completo
        self.play(
            tiempo.animate.set_value(2 * np.pi), 
            run_time=tiempo_animacion, 
            rate_func=linear
        )
        self.wait(2)