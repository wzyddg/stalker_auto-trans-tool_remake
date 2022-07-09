"""Web Translator by wzyddg

"""

__version__ = "1.0.0"
__author__ = "wzyddg"

from .entityDefinition import *
from .TranslatorImpl import *

__all__ = [
    "BaiduTranslator",
    "TransmartQQTranslator",
    "DeepLTranslator"
]
