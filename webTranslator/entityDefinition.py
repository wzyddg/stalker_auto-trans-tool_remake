from abc import ABC, abstractmethod
from typing import Any, Dict, List
import xRayXmlParser
import re


class WebTranslator(ABC):

    noRusPattern = re.compile("[^"+xRayXmlParser.rusLettersString+"]*")

    autoLangCode = "ezauto"

    @abstractmethod
    def doTranslate(self, text: str, fromLang: str, toLang: str, isRetry: bool = False) -> str:
        """ interface main function method
        """

    @abstractmethod
    def getApiLangCode(self, textLang: str) -> str:
        pass

    def detectLang(self, text: str) -> str:
        # "chs", "eng", "rus"
        noRus = self.noRusPattern.fullmatch(text)
        if noRus is None:
            return "rus"
        else:
            return "eng"

    def __init__(self):
        self.timedOutGap = 5
        self.eachRequestGap = 1
        self.lastRequest = 0
