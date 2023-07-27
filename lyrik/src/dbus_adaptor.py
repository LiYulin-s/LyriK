import abc

from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, dbus_property, PropertyAccess, signal

import asyncio

from mpris_watcher import MprisWatcher
from adaptor import AbstractAdaptor


class DBusAdaptor(AbstractAdaptor, ServiceInterface):
    """
    The `DBusAdaptor` class is a service interface that adapts a `Core` object and provides properties
    that can be accessed through D-Bus.
    """

    @classmethod
    def name(cls):
        return "DBusAdaptor"

    def __init__(self, bus: MessageBus, name: str, adaptee: MprisWatcher) -> None:
        ServiceInterface.__init__(self, f"org.LyriK.interface.{name}")
        self.__adaptee: MprisWatcher = adaptee
        self.__bus = bus
        self.__name = name

    @dbus_property(PropertyAccess.READ)
    def Title(self) -> "s":
        return self.__adaptee.title

    @dbus_property(PropertyAccess.READ)
    def Index(self) -> "i":
        return self.__adaptee.index

    @dbus_property(PropertyAccess.READ)
    def TranslationIndexes(self) -> "a{si}":
        return self.__adaptee.translations_indexes

    @dbus_property(PropertyAccess.READ)
    def OriginalLyrics(self) -> "aa{is}":
        return self.__adaptee.original_lyrics

    @dbus_property(PropertyAccess.READ)
    def Translations(self) -> "a{saa{is}}":
        return self.__adaptee.translations
    
    @signal()
    def Updated(self) -> None:
        return
    
    async def create_service(self) -> None:
        self.__bus.export("/", self)
        await self.__bus.request_name(f"org.LyriK")
        await self.__bus.wait_for_disconnect()

    async def create_interface(self, name: str) -> None:
        pass


async def main():
    bus: MessageBus = await MessageBus().connect()
    core = MprisWatcher(bus, "yesplaymusic")
    adaptor = DBusAdaptor(bus,"test",core)
    core.add_callable(adaptor.Updated())
    asyncio.get_event_loop().create_task(core.polling())
    bus.export("/com/test", adaptor)
    await bus.request_name("com.example.name")
    await bus.wait_for_disconnect()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
