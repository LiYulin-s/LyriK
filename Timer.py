import asyncio

from typing import Callable


class Timer:
    def __init__(self, interval: float, function: Callable, loop: asyncio.AbstractEventLoop) -> None:
        """
        The __init__ function is the constructor for the class. It takes in three arguments:
        interval - The time between calls to function, in seconds.
        function - The function to call every interval seconds.
        loop     - An asyncio event loop object.

        :param self: Represent the instance of the class
        :param interval: float: Set the time between each call of the function
        :param function: Callable Store the function that will be called every interval
        :param loop:asyncio.AbstractEventLoop: Pass in the event loop that will be used to run the task
        :return: None
        :doc-author: Trelent
        """
        self.__interval = interval
        self.__function = function
        self.__is_running: bool = False
        self.__loop = loop

    def start(self):
        self.__is_running = True
        self.__loop.create_task(self.__run())

    def stop(self):
        """
        The stop function sets the is_running variable to False, which will cause the run function to stop running.

        :param self: Represent the instance of the class
        :return: The value of the is_running property
        :doc-author: Trelent
        """
        self.__is_running = False

    async def __run(self):
        if self.__is_running:
            self.__function()
            await asyncio.sleep(self.__interval)
            self.__loop.create_task(self.__run())
        else:
            return
