"""X-Ray Engine text xml Parser by wzyddg

"""

__version__ = "1.0.0"
__author__ = "wzyddg"

from .xmlxReader import *
from .xRayTextAnalyzer import *
from .entityDefinition import *
from .xmlFileGenerator import *

__all__ = [
    "parse_xray_xml",
    "generateOutputXml",
    "TextEntity",
    "rusLettersString",
    "actionPattern",
    "lineBreakPattern",
    "placeholderPattern",
    "scriptPlaceHolderPattern",
    "rusLetCpl",
    "actionCpl",
    "placeholderCpl",
    "scriptCpl",
    "allSeparateTextCpl",
    "getRecommendLangText",
    "allSeparateTextCpl"
]
