from typing import Any, Dict, List
from lxml import etree
import os
import re
from .xRayTextAnalyzer import *
from .entityDefinition import *

# I will separate those included xml as standalone xml with full structure


def extract_entity_from_root(root: etree._Element) -> List[TextEntity]:
    children = None
    if root.tag == 'string':
        children = [root]
    else:
        children = root.getchildren()

    res = []
    for ent in children:
        entChildren = ent.getchildren()
        langDict = dict()
        for lang in entChildren:
            if lang.text is not None and len(lang.text) > 0:
                curText = re.sub(r'[\n]', '', lang.text)
                langDict[lang.tag] = curText
        if ent.attrib.get("id") is not None:
            res.append(TextEntity(ent.attrib.get("id"), langDict))

    return res


def parse_xray_text_xml(filePath: str, candidateEncodings: List[str] = ["cp1251"]) -> List[TextEntity]:
    tree = None
    f = None
    root = None

    try:
        tree = etree.parse(filePath)
        return extract_entity_from_root(tree.getroot())

    except:
        for encoding in candidateEncodings:
            try:

                f = open(filePath, "r", encoding=encoding)
                wholeText = f.read()
            except UnicodeDecodeError:
                f.close()
                print(" ├──" + filePath + " is not encoded with "+encoding)
                continue
            else:
                f.close()
                print(" ├──" + filePath + " successfully decoded with "+encoding)
                break

        try:
            wholeText = normalize_xml_string(wholeText)
            root = etree.fromstring(wholeText)
        except (etree.XMLSyntaxError, ValueError) as err:
            print(filePath + " is not a parsable xml")
            print(err)

    return extract_entity_from_root(root)


def parse_xray_cfgxml_xml(filePath: str, candidateEncodings: List[str] = ["cp1251"]) -> Tuple[str, set[str]]:
    successEncoding = ""
    for encodingIndex in range(len(candidateEncodings)):
        encoding = candidateEncodings[encodingIndex]
        try:
            # if last candidate, read any way
            f = 1
            if encodingIndex == len(candidateEncodings) - 1:
                f = open(filePath, "r", encoding=encoding, errors="ignore")
                print(" ├──" + filePath + " is forced decoded with "+encoding)
            else:
                f = open(filePath, "r", encoding=encoding)
            wholeText = f.read()
            successEncoding = encoding
        except UnicodeDecodeError:
            f.close()
            print(" ├──" + filePath + " is not encoded with "+encoding)
            continue
        else:
            f.close()
            print(" ├──" + filePath + " is successfully decoded with "+encoding)
            break

    wholeText = normalize_xml_string(
        wholeText, needFixST=False, deleteHeader=False)

    guys = getConfigXmlPotentialTexts(wholeText)

    return (wholeText, guys, successEncoding)


def parse_xray_script_file(filePath: str, candidateEncodings: List[str] = ["cp1251"]) -> Tuple[str, set[str]]:
    for encoding in candidateEncodings:
        try:
            f = open(filePath, "r", encoding=encoding)
            wholeText = f.read()
        except UnicodeDecodeError:
            f.close()
            print(" ├──" + filePath + " is not encoded with "+encoding)
            continue
        else:
            f.close()
            print(" ├──" + filePath + " successfully decoded with "+encoding)
            break

    guys = getScriptPotentialTexts(wholeText)

    return (wholeText, guys)


def parse_xray_ltx_file(filePath: str, candidateEncodings: List[str] = ["cp1251"]) -> Tuple[str, set[str]]:
    successEncoding = ""
    for encodingIndex in range(len(candidateEncodings)):
        encoding = candidateEncodings[encodingIndex]
        try:
            # if last candidate, read any way
            f = 1
            if encodingIndex == len(candidateEncodings) - 1:
                f = open(filePath, "r", encoding=encoding, errors="ignore")
                print(" ├──" + filePath + " is forced decoded with "+encoding)
            else:
                f = open(filePath, "r", encoding=encoding)
            wholeText = f.read()
            successEncoding = encoding
        except UnicodeDecodeError:
            f.close()
            print(" ├──" + filePath + " is not encoded with "+encoding)
            continue
        else:
            f.close()
            print(" ├──" + filePath + " successfully decoded with "+encoding)
            break

    guys = getLtxPotentialTexts(wholeText)

    return (wholeText, guys, successEncoding)


def read_plain_text(filePath: str, candidateEncodings: List[str] = ["cp1251", 'cp1252', 'utf-8']):
    for encoding in candidateEncodings:
        try:
            f = open(filePath, "r", encoding=encoding)
            wholeText = f.read()
        except UnicodeDecodeError:
            f.close()
            print(" ├──" + filePath + " is not encoded with "+encoding)
            continue
        else:
            f.close()
            print(" ├──" + filePath + " successfully decoded with "+encoding)
            break

    return wholeText