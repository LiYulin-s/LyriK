from dbus_next.aio import MessageBus

from dbus_next.service import (ServiceInterface,
                               dbus_property,PropertyAccess ,signal)
#from dbus_next import Variant, DBusError

import asyncio

from Unit import Unit, create_unit

class DBusAdaptor(ServiceInterface):
    """
    The `DBusAdaptor` class is a service interface that adapts a `Core` object and provides properties
    that can be accessed through D-Bus.
    """
    def __init__(self, name: str, adaptee: Unit) -> None:
        """constructor of DBusAdaptor

        Args:
            name (str): the unique part of the interface name.

            adaptee (Core): the object provides all properties and accessed by this adaptor
        """
        super().__init__(f"org.LyriK.interface.{name}")
        self.__adaptee = adaptee

    @signal()
    def PropertyChanged(self) -> None:
        """
        This is a decorator function that signals when a property has been changed.
        :return: The function `PropertyChanged` is returning `None`.
        """
        return

    @dbus_property(PropertyAccess.READ)
    def SongName(self) -> 's':
        return self.__adaptee.song_name()
    
    @dbus_property(PropertyAccess.READ)
    def Index(self) -> 'i' :
        return self.__adaptee.index()
    
    @dbus_property(PropertyAccess.READ)
    def OriginalLyrics(self) -> 'as' :
        return self.__adaptee.original_lyrics()
    
    @dbus_property(PropertyAccess.READ)
    def Translations(self) -> 'a{sas}' :
        return self.__adaptee.translations()
    
async def main():
    bus = await MessageBus().connect()
    core = await create_unit("yesplaymusic")
    adaptor = DBusAdaptor("test", core)
    bus.export('/com/test',adaptor)
    await bus.request_name('com.example.name')
    await bus.wait_for_disconnect()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
