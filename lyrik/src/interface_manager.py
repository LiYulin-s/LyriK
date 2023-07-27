import asyncio
import importlib
import pkgutil
from typing import Callable, Coroutine

from netwrok_interface import AbstractNetworkInterface, LyricsResponse

from loguru import logger

class InterfaceManager:
    def __init__(self, calllback:Callable, path: str, config: dict[str]) -> None:
        for module in pkgutil.iter_modules():
            if module.name.startswith("lyrik_interface"):
                importlib.import_module(module.name)

        self.__interfaces: list[AbstractNetworkInterface] = []
        for interface_class in AbstractNetworkInterface.__subclasses__():
            if not interface_class.name() in config["DisabledInterface"]:
                self.__interfaces.append(interface_class())
        
        self.__task: asyncio.Task = None
        self.__callback:Callable = calllback

        self.__weights: dict[str, int] = {}
        for item in enumerate(config["Priority"]):
            self.__weights[item[1]] = item[0]


    @property
    def interfaces(self) -> list[AbstractNetworkInterface]:
        """
        Returns a list of all interfaces
        """
        return self.__interfaces
    
    async def get_lyrics(self, title: str, album: str, artist: list, hazy_search: bool, callback: Callable):
        for interface in self.__interfaces:
            if not self.__task is None:
                self.__task.cancel()
            coroutines: list[Coroutine] = []
            coroutines.append(interface.get_lyrics(title, album, artist, hazy_search))
            result: list[LyricsResponse|Exception] = await asyncio.gather(*coroutines, return_exceptions=True)
            
            hazy_result: list[LyricsResponse] = []
            concrete_result: list[LyricsResponse] = []

            for result_item in result:
                if isinstance(result_item, Exception):
                    logger.critical(f"Error while getting lyrics: {result_item}")
                    continue
                else:
                    if result_item.hazy:
                        hazy_result.append(result_item)
                    else:
                        concrete_result.append(result_item)

            if len(concrete_result) > 0:
                callback(concrete_result[0])

    def callback_lyrics(self)