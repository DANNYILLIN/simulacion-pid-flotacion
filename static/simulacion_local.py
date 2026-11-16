import numpy as np

# Parámetros físicos del sistema
AREA_CELDA = 30.0 * 30.0
CONVERSION_LPM_A_CMS = 1000.0 / 60.0

class ControladorCelda:
    def __init__(self, Kc, tau_i, K_ff, setpoint, h_inicial):
        self.Kc = Kc
        self.tau_i = tau_i
        self.K_ff = K_ff
        self.setpoint = setpoint
        self.h = h_inicial
        self.integral_error = 0.0
        self.Q_out = 0.0
        self.Q_in_prev = None

    def actualizar(self, Q_in, dt):
        e = self.setpoint - self.h
        self.integral_error += e * dt
        accion_fb = self.Kc * (e + (1.0 / self.tau_i) * self.integral_error)
        
        delta_Q_in = (Q_in - self.Q_in_prev) if self.Q_in_prev is not None else 0.0
        accion_ff = self.K_ff * delta_Q_in
        self.Q_in_prev = Q_in

        self.Q_out = max(0.0, min(100.0, accion_fb + accion_ff))

        Q_in_cms = Q_in * CONVERSION_LPM_A_CMS
        Q_out_cms = self.Q_out * CONVERSION_LPM_A_CMS
        self.h += ((Q_in_cms - Q_out_cms) / AREA_CELDA) * dt
        return self.Q_out, self.h

def obtener_datos_simulacion():
    """Genera los datos numéricos puros (Usado por Flask y por ejecución local)"""
    tiempo_total = 600 
    dt = 1.0
    t_array = np.arange(0, tiempo_total, dt).tolist()

    celda1 = ControladorCelda(-62, 56, 0.8, 30.0, 29.0)
    celda2 = ControladorCelda(-76, 30, 0.8, 34.0, 34.5)
    celda3 = ControladorCelda(-85, 44, 1.0, 32.0, 33.5)

    hist_Q_feed, hist_h, hist_Q_out = [], [[], [], []], [[], [], []]

    for t in t_array:
        Q_feed = 45.0 if t < 180 else 55.0  # Disturbio en t=180s
        Q_out1, h1 = celda1.actualizar(Q_feed, dt)
        Q_out2, h2 = celda2.actualizar(Q_out1, dt)
        Q_out3, h3 = celda3.actualizar(Q_out2, dt)

        hist_Q_feed.append(Q_feed)
        hist_h[0].append(h1); hist_Q_out[0].append(Q_out1)
        hist_h[1].append(h2); hist_Q_out[1].append(Q_out2)
        hist_h[2].append(h3); hist_Q_out[2].append(Q_out3)

    return {
        "tiempo": t_array,
        "disturbio_inicial": hist_Q_feed,
        "h": hist_h,
        "q_out": hist_Q_out,
        "setpoints": [30.0, 34.0, 32.0]
    }

def ejecutar_simulacion_local():
    """Esta función solo se ejecutará cuando el profesor corra el script en su PC"""
    import matplotlib.pyplot as plt
    datos = obtener_datos_simulacion()
    
    fig, axs = plt.subplots(3, 1, figsize=(10, 10))
    disturbios = [datos["disturbio_inicial"], datos["q_out"][0], datos["q_out"][1]]
    
    for i in range(3):
        ax1 = axs[i]
        ax2 = ax1.twinx()
        
        ax1.plot(datos["tiempo"], datos["h"][i], 'b-', label='Nivel (h)')
        ax1.axhline(datos["setpoints"][i], color='r', linestyle='-', label='Setpoint')
        ax1.set_ylabel('Altura [cm]')
        ax1.set_ylim(26, 38)
        
        ax2.plot(datos["tiempo"], disturbios[i], 'c-', label='Disturbio (Q_in)')
        ax2.plot(datos["tiempo"], datos["q_out"][i], 'k-', label='Bomba (Q_out)')
        ax2.set_ylabel('Caudal [lpm]')
        ax2.set_ylim(0, 100)
        
        ax1.set_title(f'Control Feedback+Feedforward - Celda {i+1}')
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    ejecutar_simulacion_local()