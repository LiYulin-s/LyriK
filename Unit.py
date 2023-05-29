from Timer import Timer

from dbus_next.aio import MessageBus, ProxyInterface
from dbus_next.introspection import Node

import asyncio

from DBusAdaptor import DBusAdaptor


class Unit:
    def __init__(self, mpris_name: str, bus_interface: ProxyInterface) -> None:
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
        self.__song_name: str = ""
        self.__index: int = 0
        self.__original_lyrics: list = []
        self.__translations: dict = dict()

        self.__position: int
        self.__timer: Timer = Timer(0.05, self.__on_timer_triggered)
        self.__mpris_name: str = mpris_name
        self.__interface: ProxyInterface = bus_interface
        self.__adaptor: DBusAdaptor = DBusAdaptor(mpris_name, self)

    def song_name(self) -> str:
        """
        The song_name function returns the name of the song.

        :param self: Refer to the current instance of a class
        :return: The song name
        :doc-author: Trelent
        """
        return self.__song_name

    def index(self) -> int:
        """
        The index function returns the index of the current position in lyrics list.

        :param self: Represent the instance of the object itself
        :return: The index
        :doc-author: Trelent
        """
        return self.__index

    def original_lyrics(self) -> list:
        """
        The original_lyrics function returns the original lyrics of a song.

        :param self: Refer to the current instance of the class
        :return: The original lyrics of the song
        :doc-author: Trelent
        """
        return self.__original_lyrics

    def translations(self) -> dict[str, list]:
        """
        The translations function returns a dictionary of the form:
        {'language': ['translation', 'translation', ...], ...}


        :param self: Refer to the instance of the class
        :return: A dictionary of the form {'language': ['translation', 'translation']}
        :doc-author: Trelent
        """
        return self.__translations

    def __on_timer_triggered(self):
        task: asyncio.Task = asyncio.get_event_loop().create_task(self.__interface.get_positon())
        task.add_done_callback(self.__set_postion)

    def __set_postion(self, future: asyncio.Future) -> None:
        self.__position = future.result()
        return


async def create_unit(mpris_name: str) -> Unit:
    """
    The create_unit function is a coroutine that returns an instance of the Unit class.
    The function takes in one argument, mpris_name, which is a string representing the name of the MPRIS player to be controlled.
    The function uses this name to create a proxy object for that specific player's D-Bus interface and then creates an instance of Unit with it.

    :param mpris_name: str: Create the unit
    :return: A Unit object
    :doc-author: Trelent
    """
    introspection:str = '''
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
    '''
    bus: MessageBus = await MessageBus().connect()

    proxy = bus.get_proxy_object(
        f"org.mpris.MediaPlayer2.{mpris_name}", "/org/mpris/MediaPlayer2", introspection
    )
    interface: ProxyInterface = proxy.get_interface("org.mpris.MediaPlayer2.Player")
    return Unit(mpris_name, interface)
