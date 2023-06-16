from typing import Callable

import weakref

from weakreflist import WeakList

import asyncio

class Signal:
    def __init__(self) -> None:
        pass  

class Observer:
    def __init__(self, loop: None|asyncio.AbstractEventLoop) -> None:
        self.__connections:weakref.WeakKeyDictionary[Signal,list[dict[Callable, tuple]]] = weakref.WeakKeyDictionary()

    def register(self, signal:Signal) -> None:
        self.__connections[signal] = WeakList()

    def unregister(self, signal: Signal) -> None:
        del self.__connections[weakref.proxy(signal)]

    def connect(self, signal: Signal, slot: Callable):
        self.__connections[weakref.proxy(signal)].append(weakref.proxy(slot))

    def disconnect(self, slot: Callable):


class Connection:
    def __