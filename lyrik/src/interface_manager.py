import asyncio
import importlib
import pkgutil
from typing import Callable, Coroutine

from netwrok_interface import AbstractNetworkInterface, LyricsResponse, InternetError

from loguru import logger

from netease_music_interface import NeteaseMusicInterface


class AllNoFoundError(Exception):
    def __init__(self, title: str, album: str, artist: list, hazy_search: bool) -> None:
        self.title = title
        self.album = album
        self.artist = artist
        self.hazy_search = hazy_search

    def __str__(self) -> str:
        return f"No lyrics found for {self.title} by {self.artist} on {self.album}"


class NetworkError(Exception):
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return "Network Error."


class InterfaceManager:
    def __init__(self, path: str | None, config: dict[str]) -> None:
        for module in pkgutil.iter_modules(path=path):
            if module.name.startswith("lyrik_interface"):
                importlib.import_module(module.name)

        self.__interfaces: list[AbstractNetworkInterface] = []
        for interface_class in AbstractNetworkInterface.__subclasses__():
            if not interface_class.name() in config["Disabled"]:
                self.__interfaces.append(interface_class())

        self.__task: asyncio.Task = None

        self.__weights: dict[str, int] = {}
        for item in enumerate(config["Priority"]):
            self.__weights[item[1]] = item[0]

    @property
    def interfaces(self) -> list[AbstractNetworkInterface]:
        """
        Returns a list of all interfaces
        """
        return self.__interfaces

    async def get_lyrics(self, title: str, album: str, artist: list, hazy_search: bool) -> LyricsResponse:
        for interface in self.__interfaces:
            if not self.__task is None:
                self.__task.cancel()
            coroutines: list[Coroutine] = []
            coroutines.append(interface.get_lyrics(title, album, artist, hazy_search))
            result: list[LyricsResponse | Exception] = await asyncio.gather(*coroutines, return_exceptions=True)

            hazy_result: list[LyricsResponse] = []
            concrete_result: list[LyricsResponse] = []

            error = 0
            network_error = 0

            for result_item in result:
                if isinstance(result_item, Exception):
                    logger.critical(f"Error while getting lyrics: {result_item}")
                    error += 1
                    if isinstance(result_item, InternetError):
                        network_error += 1
                    continue
                else:
                    if result_item.hazy:
                        hazy_result.append(result_item)
                    else:
                        concrete_result.append(result_item)

            if len(concrete_result) > 0:
                return max(concrete_result, key=lambda x: self.__weights[x.interface])
            elif len(hazy_result) > 0:
                return max(hazy_result, key=lambda x: self.__weights[x.interface])
            elif error == len(result) and error == network_error:
                raise NetworkError()
            else:
                raise AllNoFoundError(title, album, artist, hazy_search)
