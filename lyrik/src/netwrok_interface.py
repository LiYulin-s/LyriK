import abc
import asyncio
import json

import aiohttp
from loguru import logger


class LyricsResponse:
    def __init__(
        self, hazy_search: bool, lyrics: str, translation: dict[str:str] or None
    ):
        self.hazy = hazy_search
        self.lyrics = lyrics
        self.translation = translation

    def __repr__(self) -> str:
        return f"<network_interface.LyricsResponse lyrics='{self.lyrics}' hazy={self.hazy} translation={self.translation}>"


class AbstractNetworkInterface(abc.ABC):
    @abc.abstractclassmethod
    def name(cls) -> str:
        pass

    @abc.abstractmethod
    async def get_lyrics(
        self, title: str, album: str, artist: list, hazy_search=True
    ) -> LyricsResponse:
        pass


class NoFoundError(Exception):
    def __init__(
        self,
        interface: AbstractNetworkInterface,
        title: str,
        artist: list[str],
        album: str,
    ) -> None:
        self.__interface = interface
        self.__title = title
        self.__artist = artist
        self.__album = album

    def __str__(self) -> str:
        return f'{self.__interface} cannot find lyrics for "{self.__title}" by "{self.__artist}" on "{self.__album}".'


class InternetError(Exception):
    def __init__(self, interface: AbstractNetworkInterface) -> None:
        self.__interface = interface

    def __str__(self) -> str:
        return f"{self.__interface} cannot connect to the internet."
