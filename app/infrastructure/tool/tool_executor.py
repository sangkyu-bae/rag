from abc import ABC, abstractmethod


class ToolExecutor(ABC):
    @abstractmethod
    def _execute(self,question:str):

        pass