# modo responsavel por definir uma interface comum dividida por todos os controles do robo, para que o robo possa trata-lo de forma polymorphica

from abc import ABC, abstractmethod
from typing import Tuple


class BaseController(ABC):
    # abstrai a interface para que o controle seguidor de marcador. qualque controle conectado ao robo deve implementar reset() e compute_control() com essa exata assinatura

    @abstractmethod
    def reset(self) -> None:
        # reta qualquer estado interno
        raise NotImplementedError

    @abstractmethod
    def compute_control(
        self,
        x: float,
        y: float,
        theta: float,
        target_x: float,
        target_y: float,
        dt: float
    ) -> Tuple[float, float]:
        # computa o controle de output (v velocidade linear, velocidade angular) para dirigir o robo do (x,y, theta) para (trget_x, target_y)
        
        raise NotImplementedError
