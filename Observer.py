from typing import Callable

class Signal:
    def

class Observer:
    def __init__(self) -> None:
        self.__connections:dict[Signal,list[dict[Callable, tuple]]] ={}
    def register(self, signal:Signal) -> None:
        self.__connections[signal] = []
    def unregister(self, signal: Signal) -> None:
        del self.__connections[signal]
    def connect(self, signal):


