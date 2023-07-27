import abc


class AbstractAdaptor(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def name(cls):
        pass

    @abc.abstractmethod
    def __init__(self, name: str, adaptee):
        pass

    @abc.abstractmethod
    async def create_service(self) -> None:
        pass

    @abc.abstractmethod
    async def create_interface(self, name: str) -> None:
        pass
