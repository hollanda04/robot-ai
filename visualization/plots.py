# modulo responsavel pelo uso do matplotlib para gerar o plots de telemetria apos o robo completar o percurso, mostrando perfis de velocidade, erros angulares e trajetoria. basicamente responsavel pelos graficos finais

from typing import List, Dict, Any
import math

def show_performance_plots(telemetry: List[Dict[str, Any]], stats: Dict[str, Any]):
   # crias e mostra a telemetria dos graficos de performanse usando matplolib
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("\n[Aviso] Matplotlib não está instalado. Não é possível gerar os gráficos.")
        print("Para visualizar a telemetria graficamente, instale as dependências executando:")
        print("pip install matplotlib numpy\n")
        return

    if not telemetry:
        print("[Aviso] Sem dados de telemetria para plotar.")
        return

    # Extrai arrays de telemetria
    times = np.array([log['time'] for log in telemetry])
    xs = np.array([log['x'] for log in telemetry])
    ys = np.array([log['y'] for log in telemetry])
    speeds = np.array([log['speed'] for log in telemetry])
    errors = np.array([log['angle_error_deg'] for log in telemetry])
    controllers = np.array([log['controller'] for log in telemetry])

    # Setup da figura e campo
    fig = plt.figure(figsize=(12, 8))
    fig.patch.set_facecolor('#1a1b26')
    plt.suptitle("Análise de Telemetria do Explorador 2D", fontsize=16, color='#f3f4f6', weight='bold')

    # estilo
    text_color = '#f3f4f6'
    grid_color = '#2e303e'
    pid_color = '#eab308'    # amarelo
    fuzzy_color = '#a855f7'  # roxo

    # --- Plot 1: Trajectoria 2D ---
    ax1 = plt.subplot(2, 2, (1, 3)) # Spans left column
    ax1.set_facecolor('#11121a')
    ax1.grid(True, color=grid_color, linestyle='--', alpha=0.5)
    
    # seguimentos de plot com cores diferentes baseada no tipo de controle utilizado
    start_idx = 0
    for i in range(1, len(controllers)):
        if controllers[i] != controllers[start_idx] or i == len(controllers) - 1:
            segment_x = xs[start_idx:i+1]
            segment_y = ys[start_idx:i+1]
            color = pid_color if controllers[start_idx] == 'PID' else fuzzy_color
            if start_idx == 0 or controllers[start_idx] not in ax1.get_legend_handles_labels()[1]:
                label = controllers[start_idx]
            else:
                label = None
            ax1.plot(segment_x, segment_y, color=color, linewidth=2.5, label=label)
            start_idx = i

    # Inverte o Y-axis pois o Pygame Y coordinates vao para baixo
    ax1.invert_yaxis()
    ax1.set_title("Trajetória do Robô no Espaço 2D", color=text_color, fontsize=12, weight='bold')
    ax1.set_xlabel("Coordenada X (pixels)", color=text_color)
    ax1.set_ylabel("Coordenada Y (pixels)", color=text_color)
    ax1.tick_params(colors=text_color)
    ax1.legend(facecolor='#1e1e24', edgecolor=grid_color, labelcolor=text_color)

    # --- Plot 2: perfil de velocidade durante o tempo? apos o tempo? no decorrer do tempo? sobre o tempo? ---
    ax2 = plt.subplot(2, 2, 2)
    ax2.set_facecolor('#11121a')
    ax2.grid(True, color=grid_color, linestyle='--', alpha=0.5)
    
    # Plot seguimentos de velocidade
    start_idx = 0
    for i in range(1, len(controllers)):
        if controllers[i] != controllers[start_idx] or i == len(controllers) - 1:
            segment_t = times[start_idx:i+1]
            segment_v = speeds[start_idx:i+1]
            color = pid_color if controllers[start_idx] == 'PID' else fuzzy_color
            ax2.plot(segment_t, segment_v, color=color, linewidth=2)
            start_idx = i
            
    ax2.set_title("Perfil de Velocidade", color=text_color, fontsize=12, weight='bold')
    ax2.set_xlabel("Tempo (segundos)", color=text_color)
    ax2.set_ylabel("Velocidade (px/s)", color=text_color)
    ax2.tick_params(colors=text_color)

    # --- Plot 3: erro de rumo sobre o tempo ---
    ax3 = plt.subplot(2, 2, 4)
    ax3.set_facecolor('#11121a')
    ax3.grid(True, color=grid_color, linestyle='--', alpha=0.5)
    
    # Plot segmento de erros
    start_idx = 0
    for i in range(1, len(controllers)):
        if controllers[i] != controllers[start_idx] or i == len(controllers) - 1:
            segment_t = times[start_idx:i+1]
            segment_e = errors[start_idx:i+1]
            color = pid_color if controllers[start_idx] == 'PID' else fuzzy_color
            ax3.plot(segment_t, segment_e, color=color, linewidth=1.5)
            start_idx = i
            
    ax3.axhline(0, color='#ef4444', linestyle=':', alpha=0.8, label='Erro Zero')
    ax3.set_title("Erro de Orientação (Ângulo)", color=text_color, fontsize=12, weight='bold')
    ax3.set_xlabel("Tempo (segundos)", color=text_color)
    ax3.set_ylabel("Erro Angular (graus)", color=text_color)
    ax3.tick_params(colors=text_color)

    # Ajuste de layout e mostrar
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    plt.show()
