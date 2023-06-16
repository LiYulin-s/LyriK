from dbus_next.aio import MessageBus

from DBusAdaptor import DBusAdaptor

from Unit import Unit,create_unit

import asyncio

async def main():
    """
    This function creates a Unit object for a given mpris media player name.

    :param mpris_name: The name of the media player that you want to control using the MPRIS (Media
    Player Remote Interfacing Specification) protocol. Examples of media players that support MPRIS
    include VLC, Spotify, and Rhythmbox
    :type mpris_name: str
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
        "org.mpris.MediaPlayer2.yesplaymusic", "/org/mpris/MediaPlayer2", introspection
    )
    interface = proxy.get_interface("org.mpris.MediaPlayer2.Player")
    pos = await interface.get_position()
    unit = await create_unit("yesplay")
    adaptor = DBusAdaptor("yesplay",unit)
    return pos


task = asyncio.get_event_loop().create_task(main())
task.add_done_callback(lambda future: print(f"Position: {future.result()}"))
asyncio.get_event_loop().run_until_complete(task)
