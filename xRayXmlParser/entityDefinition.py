from abc import ABC, abstractmethod
from typing import Any, Dict, List


class TextEntity(ABC):

    def __init__(self, id: str, texts: Dict[str, str] = []) -> None:
        super().__init__()
        self.id = id
        self.texts = texts
