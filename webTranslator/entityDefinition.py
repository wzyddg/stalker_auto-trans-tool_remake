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
        
    def resultFilter(self, sourceText: str, resultText: str) -> str:
        return resultText

    def __init__(self):
        self.timedOutGap = 10
        self.eachRequestGap = 1
        self.lastRequest = 0

    def cutSentenceWithLineEnds(self, text: str, lineEnds: list[str] = ["?", ".", "!"]) -> list[str]:
        lineEndPtn = re.compile("["+"".join(lineEnds)+"]+")
        seps = lineEndPtn.findall(text)
        pieces = lineEndPtn.split(text)
        assert len(pieces) == len(seps) + \
            1, "separator and pieces count won't match"
        sentences = []
        for i in range(len(seps)):
            sentences.append(pieces[i]+seps[i])
        if len(sentences) > 0:
            sentences[-1] = sentences[-1]+pieces[-1]
        return sentences
