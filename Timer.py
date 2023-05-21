import asyncio

class Timer:
    def __init__(self, interval: float , function, loop:asyncio.AbstractEventLoop) -> None:
        self.__interval = interval
        self.__function = function
        self.__is_running:bool = False
        self.__loop = loop
        
    def start(self):
        self.__is_running = True
        self.__loop.create_task(self.__run())

    def stop(self):
        self.__is_running = False

    async def __run(self):
        if self.__is_running :
            self.__function()
            await asyncio.sleep(self.__interval)
            asyncio.get_running_loop().create_task(self.__run())
        else:
            return
