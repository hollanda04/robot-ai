import math
from typing import Tuple


class PIDController:
    """
    Controlador PID responsável por gerar os comandos de movimento
    do personagem até um waypoint definido pelo algoritmo de busca
    (BFS ou A*).

    O PID controla apenas a orientação do personagem.
    """

    def __init__(
        self,
        kp_theta: float = 6.0,
        ki_theta: float = 0.02,
        kd_theta: float = 0.4,
        max_v: float = 120.0,
        max_w: float = 4.0,
        integral_limit: float = 5.0,
        goal_tolerance: float = 5.0
    ):

        # Ganho proporcional
        # Responsável por corrigir o erro atual.
        self.kp_theta = kp_theta

        # Ganho integral
        # Acumula erros passados.
        self.ki_theta = ki_theta

        # Ganho derivativo
        # Considera a velocidade de variação do erro.
        self.kd_theta = kd_theta

        # Velocidade linear máxima.
        self.max_v = max_v

        # Velocidade angular máxima.
        self.max_w = max_w

        # Limite da integral para evitar windup.
        self.integral_limit = integral_limit

        # Distância mínima para considerar que o waypoint foi alcançado.
        self.goal_tolerance = goal_tolerance

        # Armazena o erro da iteração anterior.
        self.prev_error_theta = None

        # Acumulador do termo integral.
        self.integral_theta = 0.0

        # Valor filtrado do derivativo.
        self.filtered_derivative = 0.0

        # Fator do filtro exponencial.
        self.derivative_filter = 0.8

    def reset(self):
        """
        Reinicia todos os estados internos do controlador.
        Deve ser chamado ao iniciar uma nova busca ou partida.
        """

        self.prev_error_theta = None
        self.integral_theta = 0.0
        self.filtered_derivative = 0.0

    def compute_control(
        self,
        x: float,
        y: float,
        theta: float,
        target_x: float,
        target_y: float,
        dt: float
    ) -> Tuple[float, float]:

        """
        Calcula as velocidades linear (v)
        e angular (w) do personagem.
        """

        # Proteção contra divisão por zero.
        if dt <= 0:
            return 0.0, 0.0

        # Diferença entre posição atual e alvo.
        dx = target_x - x
        dy = target_y - y

        # Distância até o waypoint.
        distance = math.hypot(dx, dy)

        # Se estiver suficientemente próximo,
        # considera que chegou ao waypoint.
        if distance < self.goal_tolerance:
            return 0.0, 0.0

        # Calcula o ângulo desejado.
        target_theta = math.atan2(dy, dx)

        # Erro angular.
        error_theta = target_theta - theta

        # Normaliza o erro para o intervalo [-π, π].
        error_theta = (
            (error_theta + math.pi)
            % (2 * math.pi)
            - math.pi
        )

        # --------------------------
        # TERMO INTEGRAL
        # --------------------------

        # Acumula o erro ao longo do tempo.
        self.integral_theta += error_theta * dt

        # Limita a integral para evitar windup.
        self.integral_theta = max(
            -self.integral_limit,
            min(self.integral_theta, self.integral_limit)
        )

        # --------------------------
        # TERMO DERIVATIVO
        # --------------------------

        if self.prev_error_theta is None:

            derivative_theta = 0.0

        else:

            # Derivada do erro.
            raw_derivative = (
                error_theta - self.prev_error_theta
            ) / dt

            # Filtro exponencial para suavizar ruídos.
            self.filtered_derivative = (
                self.derivative_filter
                * self.filtered_derivative
                + (1.0 - self.derivative_filter)
                * raw_derivative
            )

            derivative_theta = self.filtered_derivative

        # Armazena erro atual para próxima iteração.
        self.prev_error_theta = error_theta

        # --------------------------
        # EQUAÇÃO PID
        # --------------------------

        w_unsat = (
            self.kp_theta * error_theta
            + self.ki_theta * self.integral_theta
            + self.kd_theta * derivative_theta
        )

        # Limita velocidade angular.
        w = max(
            -self.max_w,
            min(w_unsat, self.max_w)
        )

        # --------------------------
        # VELOCIDADE LINEAR
        # --------------------------

        # Quanto mais alinhado com o alvo,
        # maior a velocidade.
        angle_scaling = max(
            0.0,
            math.cos(error_theta)
        )

        # Reduz velocidade ao se aproximar.
        speed_factor = math.tanh(distance / 25.0)

        v = (
            self.max_v
            * speed_factor
            * angle_scaling
        )

        # Se estiver muito desalinhado,
        # gira primeiro e só depois avança.
        if abs(error_theta) > math.radians(45):
            v = 0.0

        # Diminui velocidade durante curvas.
        turn_factor = (
            1.0
            - min(abs(w) / self.max_w, 1.0)
        )

        v *= turn_factor

        return v, w
