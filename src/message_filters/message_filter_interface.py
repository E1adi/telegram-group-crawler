from abc import ABC, abstractmethod
from telethon.tl.types import Message

class ReferencedChannelMessageFilter(ABC):
    @abstractmethod
    def filter(self, message: Message) -> bool:
        '''Definitaion for a telethon Message filter'''
        pass

    @abstractmethod
    def extract_ids(self, message: Message) -> set[str | int]:
        '''Based on the filters, extract the ID of the referenced channel'''
        pass