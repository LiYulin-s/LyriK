import asyncio

import pylrc

from pylrc.classes import Lyrics, LyricLine

from dbus_next.aio import MessageBus, ProxyInterface
from dbus_next.signature import Variant
from dbus_next.errors import DBusError

from typing import Callable

from netwrok_interface import AbstractNetworkInterface, LyricsResponse
from netease_music_interface import NeteaseMusicInterface
from interface_manager import InterfaceManager, NetworkError, AllNoFoundError

class MprisWatcher:
    introspection: str = """
        <!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN" "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">
    <node>
        <interface name="org.freedesktop.DBus.Introspectable">
            <method name="Introspect">
                <arg name="data" direction="out" type="s" />
            </method>
        </interface>
        <interface name="org.freedesktop.DBus.Peer">
            <method name="GetMachineId">
                <arg direction="out" name="machine_uuid" type="s" />
            </method>
            <method name="Ping" />
        </interface>
        <interface name="org.freedesktop.DBus.Properties">
            <method name="Get">
                <arg direction="in" type="s" />
                <arg direction="in" type="s" />
                <arg direction="out" type="v" />
            </method>
            <method name="Set">
                <arg direction="in" type="s" />
                <arg direction="in" type="s" />
                <arg direction="in" type="v" />
            </method>
            <method name="GetAll">
                <arg direction="in" type="s" />
                <arg direction="out" type="a{sv}" />
            </method>
            <signal name="PropertiesChanged">
                <arg type="s" />
                <arg type="a{sv}" />
                <arg type="as" />
            </signal>
        </interface>
        <interface name="org.mpris.MediaPlayer2">
            <property name="CanQuit" type="b" access="read" />
            <property name="Fullscreen" type="b" access="readwrite" />
            <property name="CanSetFullscreen" type="b" access="read" />
            <property name="CanRaise" type="b" access="read" />
            <property name="HasTrackList" type="b" access="read" />
            <property name="Identity" type="s" access="read" />
            <property name="DesktopEntry" type="s" access="read" />
            <property name="SupportedUriSchemes" type="as" access="read" />
            <property name="SupportedMimeTypes" type="as" access="read" />
            <method name="Raise" />
            <method name="Quit" />
        </interface>
        <interface name="org.mpris.MediaPlayer2.Player">
            <property name="CanControl" type="b" access="read" />
            <property name="CanPause" type="b" access="read" />
            <property name="CanPlay" type="b" access="read" />
            <property name="CanSeek" type="b" access="read" />
            <property name="CanGoNext" type="b" access="read" />
            <property name="CanGoPrevious" type="b" access="read" />
            <property name="Metadata" type="a{sv}" access="read" />
            <property name="MaximumRate" type="d" access="read" />
            <property name="MinimumRate" type="d" access="read" />
            <property name="Rate" type="d" access="readwrite" />
            <property name="Shuffle" type="b" access="readwrite" />
            <property name="Volume" type="d" access="readwrite" />
            <property name="Position" type="x" access="read" />
            <property name="LoopStatus" type="s" access="readwrite" />
            <property name="PlaybackStatus" type="s" access="read" />
            <method name="Next" />
            <method name="Previous" />
            <method name="Pause" />
            <method name="PlayPause" />
            <method name="Stop" />
            <method name="Play" />
            <method name="Seek">
                <arg direction="in" type="x" />
            </method>
            <method name="SetPosition">
                <arg direction="in" type="o" />
                <arg direction="in" type="x" />
            </method>
            <method name="OpenUri">
                <arg direction="in" type="s" />
            </method>
            <signal name="Seeked">
                <arg type="x" />
            </signal>
        </interface>
    </node>
        """

    @classmethod
    def parse_lyrics(cls, lrc: str) -> list[dict[int:str]]:
        lyrics: list[dict[int, str]] = []
        for line in pylrc.parse(lrc):
            lyrics.append({int(line.time * 1000000): line.text})
        return lyrics

    def __init__(self, bus: MessageBus, mpris_name: str) -> None:
        """
        The __init__ function is called when the class is instantiated.
        It sets up the initial state of the object, and does any other
        startup-type things that need to be done.

        :param self: Refer to the current object
        :param mpris_name: str: Identify the player that is currently playing
        :param bus_interface: ProxyInterface: Create a interface object
        :return: None
        :doc-author: Trelent
        """

        self.__title: str = ""
        self.__album: str = ""
        self.__artist: list = []
        self.__playback: str = ""

        self.__mpris_name: str = mpris_name

        self.__network_interface: InterfaceManager = InterfaceManager(None, {"Disabled": [], "Priority": ["NeteaseMusicInterface"]})

        self.__position = 0

        self.__index: int = -1
        self.__translations_indexes: dict[str:int] = {}

        self.__original_lyrics: list[dict[int:str]] = []
        self.__translations: dict[str, list[dict[int:str]]] = {}

        self.__callback: list[Callable] = []

        self.__proxy = bus.get_proxy_object(
            f"org.mpris.MediaPlayer2.{mpris_name}",
            "/org/mpris/MediaPlayer2",
            self.introspection,
        )
        self.__interface: ProxyInterface = self.__proxy.get_interface(
            "org.mpris.MediaPlayer2.Player"
        )
        self.position_changed: asyncio.Event = asyncio.Event()
        self.song_changed: asyncio.Event = asyncio.Event()

    def add_callable(self, func: Callable) -> None:
        """
        This function is used to add callable functions to the class.
        They will be called when the index or lyrics is changed.

        :param func: Callable: The function to call
        :return: None
        :doc-author: Trelent
        """

        self.__callback.append(func)

    def __update_lyrics(self, reponse: LyricsResponse) -> None:
        self.__original_lyrics = self.parse_lyrics(reponse.lyrics)
        self.__original_lyrics.sort(key=lambda x: list(x.items())[0][0])
        if reponse.translation is not None:
            translation: dict[str : list[dict[int:str]]] = {}
            for pair in reponse.translation.items():
                translation[pair[0]] = self.parse_lyrics(pair[1])
            self.__translations = translation
        else:
            self.__translations = {}

    def __update_index(self) -> None:
        for i in range(len(self.__original_lyrics)):
            if list(self.__original_lyrics[i].keys())[0] > self.__position:
                self.__index = i - 1
                break
        for item in self.__translations.items():
            for i in range(len(self.__original_lyrics)):
                if list(item[1][i].keys())[0] > self.__position:
                    self.__translations_indexes[item[0]] = i - 1
                    break


    @property
    def title(self) -> str:
        """
        The title function returns the name of the song.

        :param self: Refer to the current instance of a class
        :return: The song name
        :doc-author: Trelent
        """
        return self.__title

    @property
    def index(self) -> int:
        """
        The index function returns the index of the current position in lyrics list.

        :param self: Represent the instance of the object itself
        :return: The index
        :doc-author: Trelent
        """
        return self.__index

    @property
    def translations_indexes(self) -> dict[str:int]:
        return self.__translations_indexes

    @property
    def original_lyrics(self) -> list:
        """
        The original_lyrics function returns the original lyrics of a song.

        :param self: Refer to the current instance of the class
        :return: The original lyrics of the song
        :doc-author: Trelent
        """
        return self.__original_lyrics

    @property
    def translations(self) -> dict[str, list]:
        """
        The translations function returns a dictionary of the form:
        {'language': ['translation', 'translation', ...], ...}


        :param self: Refer to the instance of the class
        :return: A dictionary of the form {'language': ['translation', 'translation']}
        :doc-author: Trelent
        """
        return self.__translations

    async def polling(self):
        try:
            while True:
                metadata: dict[str:Variant] = await self.__interface.get_metadata()
                position: int = await self.__interface.get_position()
                playback: str = await self.__interface.get_playback_status()
                self.__playback = playback

                if (
                    metadata["xesam:title"].value != self.__title
                    or metadata["xesam:artist"].value != self.__artist
                ):
                    self.__title = metadata["xesam:title"].value
                    self.__album = metadata["xesam:album"].value
                    self.__artist = metadata["xesam:artist"].value
                    response: LyricsResponse = await self.__network_interface.get_lyrics(
                        self.__title, self.__album, self.__artist, True
                    )
                    if response is None:
                        self.__index = -1
                        self.__original_lyrics = []
                        self.__translations = {}
                    else:
                        self.__update_lyrics(response)

                    self.song_changed.set()

                if position != self.__position:
                    self.__position = position
                    self.__update_index()
                    self.position_changed.set()
        except DBusError as e:
            print(f"Error: {e}")

async def main():
    bus = await MessageBus().connect()
    a = MprisWatcher(bus, "yesplaymusic")
    await a.polling()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
