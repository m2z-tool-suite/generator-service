from abc import ABC, abstractmethod


class DataGenerator(ABC):
    """
    Interface contract for data generation
    """

    @abstractmethod
    def generate():
        pass
