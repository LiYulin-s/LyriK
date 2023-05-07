from threading import Timer

from dbus_next.aio import MessageBus

import asyncio


class Worker:
    def __init__(self, mpris_name:str) -> None:
        self.__song_name: str = ""
        self.__index: int = 0
        self.__original_lyrics: list = []
        self.__translations: dict = dict()

        self.__position: int
        self.__timer: Timer = Timer(50,lambda: self.__set_postion(self.__position + 50))

        self.__mpris_name: str = mpris_name
        self.__introspect
        self.__connection
    def song_name(self) -> str:
        """
        The function returns the song name as a string.
        :return: The method `song_name` is returning a string which is the value of the private
        attribute `__song_name`.
        """
        return self.__song_name

    def index(self) -> int:
        return self.__index

    def original_lyrics(self) -> list:
        return self.__original_lyrics

    def translations(self) -> dict:
        """
        This function returns a dictionary of translations.
        :return: A dictionary containing translations. The method `translations` is returning the
        private attribute `__translations` of the object.
        """
        return self.__translations

    async def __get_positon(self) -> int:
        introspection = await self.__bus.introspect()
        self.__bus.get_proxy_object("")

    def __set_postion(self, position: int) -> None:
        """
        This function sets the position of an object to a given integer value.

        :param position: The `position` parameter is an integer value that represents the position of the. This method sets the value of the private attribute `__position` to the given `position`
        value
        :type position: int
        """
        self.__position = position
        return

async def create_worker(mpris_name:str) -> Worker:
    bus = await MessageBus().connect()
