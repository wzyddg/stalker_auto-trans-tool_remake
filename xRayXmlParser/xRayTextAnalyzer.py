import re
from typing import Any, Dict, List, Tuple
from .entityDefinition import *

rusLettersString = "АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщъЫыьЭэЮюЯяЬ"
actionPattern = r"[()\"']?[\s]*\$\$[\s]*[Aa][Cc][Tt][_a-zA-Z0-9]*[\s]*\$\$[\s]*[()\"']?"

# add descriptor, actually not just placeholder, it's a placeholder detector, members' order matter in a group
placeholderPattern = r"%+(?:(?:[a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)+%+)|(?:[.0-9]*[A-Za-z](?:\[[a-z0-9,]*?\])?))[\s]*"
scriptPlaceHolderPattern = r"(?<!\$)\$[a-zA-Z0-9_" + \
    rusLettersString + "]+[ ,.!?\"]?"
lineBreakPattern = r"(?:\n|\\n)+"
allInOnePattern = '(?:' + actionPattern + ')|(?:' + placeholderPattern + \
    ')|(?:' + scriptPlaceHolderPattern + ')|(?:' + lineBreakPattern + ')'

rusLetCpl = re.compile("[" + rusLettersString + "]")
actionCpl = re.compile(actionPattern)
placeholderCpl = re.compile(placeholderPattern)
scriptCpl = re.compile(scriptPlaceHolderPattern)
allSeparateTextCpl = re.compile(allInOnePattern)

noLettersPattern = re.compile("[^a-zA-Z"+rusLettersString+"]*")

scriptLineSensitivePtn = re.compile(
    r"(exec|write|load|(?<!de)script(?!ion)|call|set(?![Tt]ext)|open|sound|effect|abort|print|console|cmd|return)")
scriptMatchSensitivePtn = re.compile(r'("[\s]*return)')


def getRecommendLangText(entity: TextEntity, targetLang: str) -> Tuple[str]:
    blackList = []
    for lang in entity.texts:
        if lang == "text":
            return (lang, entity.texts[lang])
    recOrder = ["eng", "rus", "ukr"]
    for lang in recOrder:
        #
        if lang == targetLang or lang not in entity.texts:
            continue
        if not lang == "rus" and entity.texts[lang].strip().startswith("==="):
            continue
        if lang == "eng" and len(rusLetCpl.findall(entity.texts[lang])) > 0:
            blackList.append(lang)
            continue

        # this lang passed all test
        return (lang, entity.texts[lang])

    # insurance
    for lang in entity.texts and lang not in blackList:
        return (lang, entity.texts[lang])

    assert 1 > 2, "No Recommended Language"


def shouldPieceBeTranslated(piece: str) -> bool:
    res = noLettersPattern.fullmatch(piece)
    return res is None


def escapeXmlContentString(text: str) -> str:
    replaced = re.sub('&', '&amp;', text)
    replaced = re.sub('"', '&quot;', replaced)
    replaced = re.sub("'", '&apos;', replaced)
    replaced = re.sub('<', '&lt;', replaced)
    return avoid_error_normalizer(replaced)


def avoid_error_normalizer(text: str) -> str:
    text = text.strip()
    # this is a non-space blank character, avoid error but still empty
    if len(text) == 0:
        text = ' '
    return text


def getGameplayPotentialTexts(text: str) -> set[str]:
    gpptn = re.compile(
        r"<(?:text|bio|title|name)(?:| [ \S]*?[^/]) *?>([^<>]*?)</(?:text|bio|title|name)>")
    res = gpptn.findall(text)
    hintptn = re.compile(r'(?:hint|name)=((?:"[^"]*")|'+r"(?:'[^']*'))")
    res2 = hintptn.findall(text)
    res3 = []
    for hint in res2:
        if len(hint) > 2:
            res3.append(hint[1:-1])
    for gpp in res:
        if len(gpp.strip()) > 0:
            res3.append(gpp.strip())
    return set(res3)


def splitTextToPiecesAtLength(text: str, pieLen: int) -> list[str]:
    if len(text) == 0:
        return [""]

    res = []
    for i in range(int(len(text)/pieLen)):
        res.append(text[i*pieLen:(i+1)*pieLen])

    res.append(text[int(len(text)/pieLen)*pieLen:])

    return res


def getLtxPotentialTexts(text: str) -> set[str]:
    res = set()
    lines = text.split("\n")

    for line in lines:
        line = re.sub(';[\s\S]*', '', line).strip()
        pieces = line.split("=")
        if len(pieces) < 2:
            continue
        if "description" in pieces[0] or pieces[0].startswith("inv_name"):
            res.add("=".join(pieces[1:]).strip())

    return res


def getScriptPotentialTexts(text: str) -> set[str]:
    res = set()

    lines = text.split("\n")

    for line in lines:
        # some pre filter
        line = re.sub(r'--[\s\S]*$', '', line).strip()

        isOpen = False
        onGoing = ''
        isEscape = False

        lineSet = set()

        for i in range(len(line)):
            if line[i] == '"':
                if not isOpen:
                    onGoing = '"'
                    isOpen = True
                    continue

                # now open
                if isEscape:
                    onGoing = onGoing + '"'
                    isEscape = False
                else:
                    onGoing = onGoing + line[i]
                    isOpen = False
                    # res.add(onGoing)

                    # match check
                    if len(scriptMatchSensitivePtn.findall(onGoing)) == 0 and len(onGoing[1:-1].strip()) > 0:
                        lineSet.add(onGoing)

                continue

            if isOpen:
                if '\\' == line[i]:
                    if isEscape:
                        onGoing = onGoing + '\\'
                        isEscape = False
                    else:
                        isEscape = True
                elif 'n' == line[i]:
                    if isEscape:
                        onGoing = onGoing + '\n'
                        isEscape = False
                    else:
                        onGoing = onGoing + 'n'
                else:
                    onGoing = onGoing + line[i]

        # post line check
        sortedLM = list(lineSet)
        sortedLM.sort(key=lambda x: len(x), reverse=True)
        sacLine = line
        for lm in sortedLM:
            sacLine = sacLine.replace(lm, "")
        normLine = sacLine.lower()
        if len(scriptLineSensitivePtn.findall(normLine)) > 0:
            continue
        else:
            res = set(sortedLM+list(res))

    return res


def escapeLiteralText(text: str) -> str:
    return text.replace("\\", '\\\\').replace("\n", '\\n').replace('"', '\\"')


def replaceFromText(text: str, replacement: Dict[str, str]) -> str:
    keys = list(replacement.keys())
    keys.sort(key=lambda x: len(x), reverse=True)
    for repKey in keys:
        text = text.replace(repKey, replacement[repKey])
    return text


def normalize_xml_string(xmlStr: str, needFixST: bool = True, deleteHeader: bool = True) -> str:
    if needFixST:
        deleteHeader = True

#    poor detect, at least it should look like xml
    if "</" in xmlStr:
        while len(xmlStr) > 0 and not xmlStr.startswith("<"):
            xmlStr = xmlStr[1:]
    replaced = re.sub(r'&[\s]+amp;', '&amp;', xmlStr)
    replaced = re.sub(r'&[\s]+lt;', '&lt;', replaced)
    replaced = re.sub(
        '&(?!ensp;|emsp;|nbsp;|lt;|gt;|amp;|quot;|copy;|reg;|trade;|times;|divide;)', '&amp;', replaced)
    replaced = re.sub(r'<!--[\s\S]*?-->', '', replaced)

    if deleteHeader:
        replaced = re.sub(r'<\?[^>]+\?>', '', replaced)

    # convert < in xml, but not tag
    replaced = re.sub('<(?![A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD/])', '&lt;', replaced).strip()
    if replaced.startswith("&lt;?xml"):
        replaced = "<"+replaced[4:]

    if needFixST:
        if not replaced.strip().startswith("<string_table>"):
            replaced = "<string_table>" + replaced + "</string_table>"

        # I cant believe in some case , there are half a string tag after the end of </string_table>
        replaced = re.sub(
            r"</string_table>[\s\S]+", "</string_table>", replaced)
    return replaced


def getEncodingDeclaration(xmlStr: str) -> str:
    dec = re.compile("<\?xml[^>]+encoding=([^>]+)\?>")
    resDec = dec.findall(xmlStr)
    if len(resDec) > 0:
        return re.sub(r'[\'"\s]', '', resDec[0])
    else:
        return None


def doesTextLookLikeId(text: str) -> bool:
    if len(rusLetCpl.findall(text)) > 0:
        return False
    if "_" in text:
        return True
    return " " not in text


def doesTextLookLikeScript(text: str) -> bool:
    if len(rusLetCpl.findall(text)) > 0:
        return False
    if '=' in text or '@' in text:
        return True
    strangePtn = re.compile(":\d")
    if len(strangePtn.findall(text)) > 0:
        return True


def cutTextWithSeparator(text: str) -> List[Dict[str, str]]:
    seps = allSeparateTextCpl.findall(text)
    pieces = allSeparateTextCpl.split(text)
    assert len(pieces) == len(seps) + \
        1, "separator and pieces count won't match"

    res = []
    for i in range(len(pieces)):
        if shouldPieceBeTranslated(pieces[i]):
            res.append({
                "needTrans": True,
                "content": pieces[i]
            })
        else:
            res.append({
                "needTrans": False,
                "content": pieces[i]
            })
        if i < len(seps):
            # cleaning for $$ACTION_XX$$
            washed = re.sub(r"(?<=\$\$)[\s]*(?=[_a-zA-Z0-9])", "", seps[i])
            washed = re.sub(r"(?<=[_a-zA-Z0-9])[\s]*(?=\$\$)", "", washed)
            res.append({
                "needTrans": False,
                "content": washed
            })

    return res
