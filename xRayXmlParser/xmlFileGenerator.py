from .entityDefinition import *
from .xRayTextAnalyzer import *


def generateOutputXml(filePath: str, texts: Dict[str, str]):
    fileText = '<?xml version="1.0" encoding="utf-8"?>\n<string_table>\n'
    for textId in texts:
        fileText = fileText+'\t<string id="' + \
            escapeXmlContentString(textId)+'">\n'
        if isinstance(texts[textId], set):
            texts[textId] = "".join(texts[textId])

        # add break:\n every 1000 char so it can be loaded into game
        # maybe protect placeholder later
        fileText = fileText+'\t\t<text>' + \
            '\n'.join(splitTextToPiecesAtLength(
                escapeXmlContentString(texts[textId]), 1000))+'</text>\n'
        fileText = fileText+'\t</string>\n'
    fileText = fileText+'</string_table>\n'
    file = open(filePath, "w", encoding="utf-8")
    file.write(fileText)
    file.close()


def generateOutputFileFromString(filePath: str, text: str, needXmlHeader: bool = True,  encoding: str = "utf-8"):
    if needXmlHeader:
        encoding = "utf-8"
        if not text.strip().startswith("<?xml"):
            text = '<?xml version="1.0" encoding="utf-8"?>\n'+text.strip()
    file = open(filePath, "w", encoding=encoding)
    file.write(text)
    file.close()
