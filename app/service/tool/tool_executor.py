from abc import ABC, abstractmethod


class ToolExecutor(ABC):
    @abstractmethod
    def execute(self,question:str):

        pass