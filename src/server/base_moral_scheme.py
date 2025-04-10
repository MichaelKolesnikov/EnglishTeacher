import numpy
import numpy as np
from .OpenAIInterface import OpenAIInterface
from typing import Optional


class BaseMoralScheme:
    def __init__(
            self,
            base_intentions: np.ndarray,
            changed_message: Optional[str] = None,
            appraisals: Optional[np.ndarray] = None,
            feelings: Optional[np.ndarray] = None
    ) -> None:
        """
        Базовая моральная схема.
        
        Args:
            base_intentions (np.ndarray): Базисные векторы семантического пространства.
            changed_message (Optional[str]): Начальный prompt (по умолчанию None).
            appraisals (Optional[np.ndarray]): Вектор оценок (если не задан, заполняется нулями).
            feelings (Optional[np.ndarray]): Вектор чувств (если не задан, заполняется 0.5).
        """
        print(f"changed_message:\n{changed_message}")
        self.base_intentions = base_intentions

        # размер семантического пространства
        self.space_size = len(base_intentions)

        # константы для формул
        self.p_const = 0.03
        self.r_const = 0.1

        self.appraisals_state = np.zeros(self.space_size // 2)
        self.feelings_state = np.zeros(self.space_size // 2)
        # Интерфейс для взаимодействия в openAI через прокси
        self.oai_interface = OpenAIInterface()

        # векторы appraisals и feelings
        if appraisals is None:
            self.appraisals = np.zeros(self.space_size)
        else:
            self.appraisals = appraisals

        if feelings is None:
            self.feelings = np.empty(self.space_size)
            self.feelings.fill(0.5)
        else:
            self.feelings = feelings

        self.appraisals = (
            np.full(self.space_size, 0.0)
            if appraisals is None
            else appraisals
        )

        self.feelings = (
            np.full(self.space_size, 0.5)
            if feelings is None
            else feelings
        )

    @staticmethod
    def euc_dist(a: np.ndarray, b: np.ndarray) -> numpy.floating:
        """
        Вычисляет расстояние между двумя векторами. Пока используем евклидову метрику
        Далее, возможно, надо сделать параметр настраиваемым для использования других 
        метрик
        
        Args:
            a (np.ndarray): Первый вектор
            b (np.ndarray): Второй вектор
        
        Returns:
            float: Евклидово расстояние между векторами.
        
        Raises:
            ValueError: Если векторы имеют разную длину.
        """
        if a.shape != b.shape:
            raise ValueError("Векторы должны иметь одинаковую длину")
        return np.linalg.norm(a - b)

    def get_base_intentions(self) -> np.ndarray:
        """Возвращает базовые векторы пространства."""
        return self.base_intentions

    def update_vectors(self, action: np.ndarray):
        """
        Обновляет векторы оценок (appraisals) и чувств (feelings) 
        на основе действия (action).

        Args:
            action (np.ndarray): Вектор изменений, влияющий на оценки.
        """
        self.appraisals = (
                (1 - self.r_const) * self.appraisals + self.r_const * action
        )

        self.feelings = (
                (1 - self.p_const) * self.feelings
                + self.p_const * (self.appraisals - self.feelings)
        )

        mid = self.space_size // 2
        self.appraisals_state = self.appraisals[:mid] - self.appraisals[mid:]
        self.feelings_state = self.feelings[:mid] - self.feelings[mid:]

    def get_appraisals(self) -> np.ndarray:
        """Возвращает вектор оценок."""
        return self.appraisals

    def get_feelings(self) -> np.ndarray:
        """Возвращает вектор оценок."""
        return self.feelings

    def get_appraisals_state(self) -> np.ndarray:
        """Возвращает текущее состояние оценок."""
        return self.appraisals_state

    def get_feelings_state(self) -> np.ndarray:
        """Возвращает текущее состояние чувств."""
        return self.feelings_state
