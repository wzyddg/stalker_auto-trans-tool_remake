import re
from typing import Any, Dict, List, Tuple
from .entityDefinition import *

rusLettersString = "АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщъЫыьЭэЮюЯяЬ"
actionPattern = r"[()\"']?[\s]*\$\$[\s]*[Aa][Cc][Tt][_a-zA-Z0-9]*[\s]*\$\$[\s]*[()\"']?"

# add descriptor, actually not just placeholder, it's a placeholder detector, members' order matter in a group
placeholderPattern = r"%+(?:(?:[a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)+%+)|(?:[.0-9]*[A-Za-z](?:\[[a-z0-9,\s_]*?\])?))[\s]*"
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

# add guarantee safe here
scriptLinePermitPtn = re.compile(
    r"([Mm]essage|[Tt]ext(?!ure)|(?<![a-z])[Nn]ews(?![a-z]))")
scriptLineSensitivePtn = re.compile(
    r"(exec|write|parse_names|info_add|get_sequence_for_npc|load|call|set(?![Tt]ext)|open|sound|effect|abort|print|console|cmd|return)")
scriptMatchSensitivePtn = re.compile(r'("[\s]*return)')
scriptContentPatternStringBlackList = [":\d", "load\s+~+"]


def getRecommendLangText(entity: TextEntity, targetLang: str) -> Tuple[str]:
    blackList = []
    for lang in entity.texts:
        if lang == "text":
            return (lang, entity.texts[lang])
    recOrder = ["eng", "rus", "ukr"]
    for lang in recOrder:
        #
        if lang not in entity.texts:
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


def getConfigXmlPotentialTexts(text: str) -> set[str]:
    gpptn = re.compile(
        r"<(?:text|bio|title|name)(?:\s*|[^/>])*?\s*>([^<>]*?)</(?:text|bio|title|name)>")
    res = gpptn.findall(text)
    hintptn = re.compile(
        r'(?:hint|name|group)\s*=\s*((?:"[^"]*")|'+r"(?:'[^']*'))")
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

# COP style complicated task info:
# title = {+zat_b101_both_heli_info} "Сигнал", {+zat_b101_one_heli_info -jup_b8_heli_4_searching} "Сигнал", "Сигнал"
# descr = {+zat_b101_both_heli_info} "Пятиканальный сигнал от неизвестного сталкера", {+zat_b101_one_heli_info -jup_b8_heli_4_searching} "Пятиканальный сигнал от неизвестного сталкера", "Пятиканальный сигнал от неизвестного сталкера"

def getLtxPotentialTexts(text: str) -> set[str]:
    res = set()
    lines = text.split("\n")

    for line in lines:
        line = re.sub(';[\s\S]*', '', line).strip()
        pieces = line.split("=")
        if len(pieces) < 2:
            continue
        content = "=".join(pieces[1:]).strip()
        if "description" in pieces[0] or pieces[0].startswith("inv_name"):
            res.add(content)
        elif pieces[0].strip() in ["title","descr"]:
            # engine will just split by ',' , following examples will not display completely
            # title = {+zat_b101_both_heli_info} "this is what we call stupid,and this is wrong!" , {+zat_b101_one_heli_info -jup_b8_heli_4_searching}sgtat_auto_generate_text_1692190353_2sig , this is what we call stupid
            # descr = "all is well ,you see?"
            if '{' in content or ',' in content:
                sac = re.sub('\{[^}]*\}', '', content)
                contentPieces = sac.split(",")
                for cp in contentPieces:
                    if len(cp.strip())>0:
                        res.add(cp.strip())
            else:
                res.add(content)
            
    return res


def getScriptPotentialTexts(text: str) -> set[str]:
    res = set()

    lines = text.split("\n")
    wordPattern = re.compile("["+rusLettersString+"a-zA-Z]")

    for line in lines:
        # some pre filter
        line = re.sub(r'--[\s\S]*$', '', line).strip()

        isOpen = False
        onGoing = ''
        isEscape = False
        quoteChar = None

        lineMatchSet = set()

        for i in range(len(line)):
            # new start
            if line[i] == '"' or line[i] == "'":
                if line[i] == quoteChar or quoteChar is None:
                    if not isOpen:
                        onGoing = line[i]
                        quoteChar = line[i]
                        isOpen = True
                        continue

                    # now open
                    if isEscape:
                        onGoing = onGoing + line[i]
                        isEscape = False
                    else:
                        onGoing = onGoing + line[i]
                        isOpen = False
                        quoteChar = None
                        # res.add(onGoing)

                        # match check
                        # if len(scriptMatchSensitivePtn.findall(onGoing)) == 0 and len(onGoing[1:-1].strip()) > 0:
                        if len(scriptMatchSensitivePtn.findall(onGoing)) == 0 and len(wordPattern.findall(onGoing)) > 0:
                            lineMatchSet.add(onGoing)

                    continue
                else:
                    pass

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
        sortedLM = list(lineMatchSet)
        sortedLM.sort(key=lambda x: len(x), reverse=True)
        sacLine = line
        for lm in sortedLM:
            thisQuoteChar = lm[0]
            escLM = thisQuoteChar + \
                escapeLiteralText(lm[1:-1], quote=thisQuoteChar)+thisQuoteChar
            sacLine = sacLine.replace(escLM, "")
        normLine = sacLine.lower()
        if len(scriptLinePermitPtn.findall(normLine)) > 0:
            res = set(sortedLM+list(res))
        elif len(scriptLineSensitivePtn.findall(normLine)) > 0:
            continue
        else:
            res = set(sortedLM+list(res))

    return res


def escapeLiteralText(text: str, quote: str = '"') -> str:
    escaped = text.replace("\\", '\\\\').replace("\n", '\\n')
    if quote == '"':
        escaped = escaped.replace('"', '\\"')
    elif quote == "'":
        escaped = escaped.replace("'", "\\'")
    return escaped


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
        '&(?!ensp;|emsp;|nbsp;|lt;|gt;|amp;|quot;|apos;|copy;|reg;|trade;|times;|divide;)', '&amp;', replaced)
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

    # special blacklist
    blklst = scriptContentPatternStringBlackList
    for blk in blklst:
        strangePtn = re.compile(blk)
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
