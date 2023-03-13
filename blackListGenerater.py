from time import time
import xRayXmlParser
import json
import os
import re


def readExistingText(exPath: str) -> dict[str, str]:
    # if reuseDir is not None:
    reLst = os.listdir(exPath)
    reuseT = {}
    print("")
    for reFile in reLst:
        reFullPath = os.path.join(exPath, reFile)
        if os.path.isfile(reFullPath):
            print("reading existing translated file:"+reFile)
            exEnts = xRayXmlParser.parse_xray_text_xml(
                reFullPath, ['cp1251', 'cp1252', 'utf-8'])
            for ent in exEnts:
                thisRe = xRayXmlParser.getRecommendLangText(ent, "chs")[1]
                reuseT[ent.id] = thisRe
    return reuseT

def norm(targ:str)->str:
    # return targ.lower()
    rem = re.sub(r'[\s,.!?\'":;]', '', targ)  
    return rem.lower()

ogse = readExistingText(r"C:\Users\wzy2\Desktop\stalker_auto-trans-tool_remake\OGSE0693TEXT\text\eng")
ogsr = readExistingText(r"C:\Users\wzy2\Desktop\stalker_auto-trans-tool_remake\OGSRTEXT")

bl=[]
for id in ogse:
    if id in ogsr:
        if norm(ogse[id]) != norm(ogsr[id]):
            bl.append(id)

print(len(bl))

xRayXmlParser.generateOutputFileFromString(r".\blackList.json",json.dumps(bl),needXmlHeader=False)
