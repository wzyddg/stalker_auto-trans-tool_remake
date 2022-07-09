from .entityDefinition import *
from .xRayTextAnalyzer import *


def generateOutputXml(filePath: str, texts: Dict[str, str]):
    fileText = '<?xml version="1.0" encoding="utf-8"?>\n<string_table>\n'
    for textId in texts:
        fileText = fileText+'\t<string id="' + \
            escapeXmlContentString(textId)+'">\n'
        fileText = fileText+'\t\t<text>' + \
            escapeXmlContentString(texts[textId])+'</text>\n'
        fileText = fileText+'\t</string>\n'
    fileText = fileText+'</string_table>\n'

    file = open(filePath, "w", encoding="utf-8")
    file.write(fileText)
    file.close()


def generateOutputXmlFromString(filePath: str, text: str):
    if not text.strip().startswith("<?xml"):
        text = '<?xml version="1.0" encoding="utf-8"?>\n'+text.strip()
    file = open(filePath, "w", encoding="utf-8")
    file.write(text)
    file.close()
