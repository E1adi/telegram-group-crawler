from abc import ABC, abstractmethod
from telethon.tl.types import Message
from typing import Set


class IMessageMatcher(ABC):
    @abstractmethod
    def match(self, message: Message) -> bool:
        """Definition for a telethon Message match"""
        pass

    @abstractmethod
    def extract_ids(self, message: Message) -> Set[str | int]:
        """Based on the filters, extract the ID of the referenced channel"""
        pass
