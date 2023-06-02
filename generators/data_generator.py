from abc import ABC, abstractmethod


class DataGenerator(ABC):
    """
    Interface contract for data generation
    """

    @abstractmethod
    def generate():
        pass

    @abstractmethod
    def fill_meta_description():
        pass

    @abstractmethod
    def replace_placeholder():
        pass