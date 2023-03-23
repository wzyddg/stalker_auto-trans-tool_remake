from time import time
import xRayXmlParser
import webTranslator
import os
import sys
import getopt
import zhconv
import json


class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


# disable buffer
sys.stdout = Unbuffered(sys.stdout)


def main(argv):

    # parameters
    engine = None
    sourceLangForTextTag = "rus"
    textDir = None
    reuseDir = None
    blackListJson = None
    targetLang = None
    appId = None
    appKey = None
    analyzeCharCount = 0
    runnableCheck = False
    forceTrans = []
    transFunction = 'text'
    outputWhenEmpty = False
    convertToCHS = False
    scriptsTranslateFunctionName = 'game.translate_string'
    ua = ""

    opts, args = getopt.getopt(argv[1:], "choe:i:k:f:t:p:a:b:r:", [
                               "runnableCheck", "convertToCHS", "help", "outputWhenEmpty", "engine=", "appId=", "appKey=", "fromLang=", "toLang=", "path=", "forceTransFiles=", "reusePath=", "blackListIdJson=", "analyzeCharCount=", "function=", "ua="])
    print(opts)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            helpText = """
S.T.A.L.K.E.R. Game(X-Ray Engine or like) Text Auto-Translator, using with language pack generator is recommended.
Version 2.1.2, Updated at March 23th 2023
by wzyddgFB from baidu S.T.A.L.K.E.R. tieba

Options:
  -e <value>|--engine=<value>               use what translate engine.
                                                eg: baidu qq 
  -p <value>|--path=<value>                 path of the folder containing what you want to translate.
                                                always quote with ""
  -t <value>|--toLang=<value>               translate to what language.
                                                eg: eng chs
  -i <value>|--appId=<value>                (Optional)appId of engine.
                                                required for baidu
  -k <value>|--appKey=<value>               (Optional)appKey of engine.
                                                required for baidu
  -f <value>|--fromLang=<value>             (Optional)from what language.
                                                default rus. eg: eng rus ukr
  -a <value>|--analyzeCharCount=<value>     (Optional)more than how many chars does the sentence need qq analyze.
                                                default 0, means don't analyze(qq engine only)
  -r <value>|--reusePath=<value>            (Optional)path of existing translated xml folder.
                                                for cfgxml/script?/ltx translating text id protecting or text translating accelerating, always quote with ""
  -b <value>|--blackListIdJson=<value>      (Optional)path of force translate id json array file, even if it's in translated xml.
                                                work with -r parameter. file content eg: ["dialog_sah_11","dialog_wolf_22"]
  --forceTransFiles=<value>                 (Optional)files that ignore reuse.
                                                concat with ','. eg: a.xml,b.xml
  -c        |--runnableCheck                (Optional)just analyze and extract files.
                                                won't do translation.
  -o        |--outputAnyWay                 (Optional)generate output file even this file has nothing translated.
                                                for cfgxml/script?/ltx, for solving #include encoding problem.
  --convertToCHS                            (Optional)convert Traditional Chinese
                                                to Simplified Chinese.
  --function=<value>                        (Optional)translating function. default text. eg: text cfgxml ltx scriptL scriptE .
                                                scriptL(same as legacy script) is translate and replace in original files.
                                                scriptE is translate and extract to a special text xml like other fuctions.
                                                program will recursively translate all files for cfgxml/script?/ltx.
  --ua=<value>                              (Optional)user agent from browser, use with qq engine to generate apikey, always quote with "".
        """
            print(helpText)
            sys.exit()
        elif opt in ("-e", "--engine"):
            engine = arg
        elif opt in ("-c", "--runnableCheck"):
            runnableCheck = True
        elif opt in ("-i", "--appId"):
            appId = arg
        elif opt in ("-k", "--appKey"):
            appKey = arg
        elif opt in ("-p", "--path"):
            textDir = arg
        elif opt in ("-f", "--fromLang"):
            sourceLangForTextTag = arg
        elif opt in ("-t", "--toLang"):
            targetLang = arg
        elif opt in ("-o", "--outputWhenEmpty"):
            outputWhenEmpty = True
        elif opt in ("-a", "--analyzeCharCount"):
            analyzeCharCount = int(arg)
        elif opt in ("-r", "--reusePath"):
            reuseDir = arg
        elif opt in ("-b", "--blackListIdJson"):
            blackListJson = arg
        elif opt in ("--forceTransFiles"):
            forceTrans = arg.split(",")
        elif opt in ("--convertToCHS"):
            convertToCHS = True
            zhconv.loaddict(os.path.join(os.path.dirname(
                __file__), "resources", "zhcdict.json"))
        elif opt in ("--function"):
            transFunction = arg
            # support legacy cmd/shell
            if transFunction == 'gameplay':
                transFunction = 'cfgxml'
            if transFunction == 'script':
                transFunction = 'scriptL'
        elif opt in ("--ua"):
            ua = arg

    # validation
    assert engine is not None, "engine must be provided."
    assert textDir is not None, "text folder path must be provided."
    assert targetLang is not None, "target language must be provided."
    if engine == 'baidu':
        assert appId is not None and appKey is not None, "when using baidu, AppId and AppKey must be provided, see https://fanyi-api.baidu.com/api/trans/product/desktop"

    # preparation

    def getTranslator(e) -> webTranslator.WebTranslator:
        if e == 'qq':
            return webTranslator.TransmartQQTranslator(analyzeCharCount, ua)
        elif e == 'deepl':
            return webTranslator.DeepLTranslator()
        elif e == 'baidu':
            return webTranslator.BaiduTranslator(appId, appKey)

    def getBenchPlayerTrans(e) -> webTranslator.WebTranslator:
        if e == 'qq':
            return webTranslator.BaiduTranslator(appId, appKey)
        else:
            return webTranslator.TransmartQQTranslator(1)

    # actual logic
    lst = os.listdir(textDir)
    doneDir = os.path.join(textDir, "translated_"+engine)
    if not os.path.exists(doneDir):
        os.mkdir(doneDir)

    # reuse translated texts
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
                    reFullPath, ['utf-8', 'cp1252', 'cp1251'])
                for ent in exEnts:
                    thisRe = xRayXmlParser.getRecommendLangText(ent, targetLang)[1]
                    if convertToCHS:
                        thisRe = zhconv.convert(thisRe, 'zh-cn')
                    reuseT[ent.id] = thisRe
        return reuseT

    reuseTexts = {}
    if reuseDir is not None:
        reuseTexts = readExistingText(reuseDir)

    if transFunction == 'text':
        tempDir = os.path.join(doneDir, "__temp__")
        if not os.path.exists(tempDir):
            os.mkdir(tempDir)
        tempTexts = readExistingText(tempDir)
        for key in tempTexts:
            reuseTexts[key] = tempTexts[key]

    blackListId = []
    if blackListJson is not None:
        blackListId = json.loads(xRayXmlParser.read_plain_text(blackListJson))
        for blc in blackListId:
            reuseTexts.pop(blc, "")

    globalReqCount = 0
    globalTransChars = 0
    globalTranslator = getTranslator(engine)
    benchPlayerTrans = getBenchPlayerTrans(engine)
    pastIds = []
    redundantIds = []

    def translateOneString(text: str, fl: str) -> str:
        pieces = xRayXmlParser.cutTextWithSeparator(text)
        nonlocal globalReqCount
        nonlocal globalTransChars
        for piece in pieces:
            if piece["needTrans"]:
                langCode = fl
                if langCode == 'text':
                    langCode = sourceLangForTextTag
                if langCode == targetLang:
                    piece["translated"] = piece["content"]
                else:
                    if not runnableCheck:
                        transedPie = globalTranslator.doTranslate(
                            piece["content"], langCode, targetLang)
                        if transedPie == piece["content"] and benchPlayerTrans is not None:
                            try:
                                benchPie = benchPlayerTrans.doTranslate(
                                    piece["content"], langCode, targetLang)
                                transedPie = benchPie
                            except:
                                pass
                        piece["translated"] = transedPie

                    else:
                        # runnable check
                        piece["translated"] = piece["content"]

                print('.', end='')
                globalReqCount = globalReqCount + 1
                globalTransChars = globalTransChars + len(piece["content"])
            else:
                piece["translated"] = piece["content"]
        transedWholeText = ""
        for piece in pieces:
            transedWholeText = transedWholeText + piece["translated"]
        return transedWholeText

    textIdPrefix = "sgtat_auto_generate_text_"+str(int(time()))+"_"
    totalGenerateCount = 0
    extract = {}

    # for xRFile in lst:
    i = 0
    while i < len(lst):
        xRFile = lst[i]
        fullPath = os.path.join(textDir, xRFile)
        if os.path.isfile(fullPath) and not os.path.exists(os.path.join(doneDir, xRFile)):
            print("\n\n"+xRFile+":")

            if transFunction == 'text':
                texts = xRayXmlParser.parse_xray_text_xml(
                    fullPath, ['cp1251', 'cp1252', 'utf-8'])
                print(" └──"+fullPath + " got " + str(len(texts)) + " texts!")
                doneHere = dict()
                tempClock = time()
                for entity in texts:
                    if entity.id in pastIds and entity.id not in redundantIds:
                        redundantIds.append(entity.id)
                    else:
                        pastIds.append(entity.id)
                    print(entity.id, end='')
                    if entity.id in reuseTexts and xRFile not in forceTrans:
                        doneHere[entity.id] = reuseTexts[entity.id]
                        print('.', end='')
                        continue

                    chosen = xRayXmlParser.getRecommendLangText(
                        entity, targetLang)
                    if targetLang == chosen[0]:
                        transedStr = chosen[1]
                    else:
                        transedStr = translateOneString(chosen[1], chosen[0])
                    doneHere[entity.id] = transedStr

                    # every 2 minutes generate a temp file
                    if time() - tempClock > 120:
                        xRayXmlParser.generateOutputXml(
                            os.path.join(tempDir, xRFile), doneHere)
                        tempClock = time()

                xRayXmlParser.generateOutputXml(
                    os.path.join(doneDir, xRFile), doneHere)
                print("")

            elif transFunction == 'cfgxml':
                pathSteps = xRFile.split(os.path.sep)
                if pathSteps[-1].lower().count(".xml") < 1 or "text" in pathSteps:
                    i = i+1
                    continue
                wholeText, candidates, successEncoding = xRayXmlParser.parse_xray_cfgxml_xml(
                    fullPath, ['cp1251', 'cp1252', 'utf-8', 'cp1251'])
                repDict = {}
                for cand in candidates:
                    if cand in reuseTexts:
                        print('!', end='')
                        continue
                    if cand.strip() == '' or xRayXmlParser.doesTextLookLikeId(cand):
                        continue
                    transedStr = translateOneString(
                        cand, globalTranslator.autoLangCode)
                    repDict[cand] = transedStr
                repdText = wholeText
                if len(repDict) > 0:
                    for key in repDict:
                        extKey = textIdPrefix+str(totalGenerateCount)
                        totalGenerateCount = totalGenerateCount+1
                        extract[extKey] = repDict[key]
                        repDict[key] = extKey

                    repdText = xRayXmlParser.replaceFromText(
                        wholeText, repDict)

                if len(repDict) > 0 or outputWhenEmpty:
                    xRayXmlParser.generateOutputFileFromString(
                        os.path.join(doneDir, xRFile), repdText, needXmlHeader=False, encoding=successEncoding)
                print("")

            elif transFunction == 'ltx':
                pathSteps = xRFile.split(os.path.sep)
                if pathSteps[-1].lower().count(".ltx") < 1:
                    i = i+1
                    continue
                wholeText, candidates, successEncoding = xRayXmlParser.parse_xray_ltx_file(
                    fullPath, ['cp1251', 'cp1252', 'utf-8', "cp1251"])
                repDict = {}
                for cand in candidates:
                    if cand in reuseTexts:
                        print('!', end='')
                        continue
                    if xRayXmlParser.doesTextLookLikeId(cand):
                        continue
                    candSend = cand
                    isQuoted = len(cand) > 1 and cand.startswith(
                        '"') and cand.endswith('"')
                    if isQuoted:
                        candSend = cand[1:-1]
                    transedStr = translateOneString(
                        candSend, globalTranslator.autoLangCode)
                    if isQuoted:
                        transedStr = '"'+transedStr+'"'
                    repDict[cand] = transedStr
                repdText = wholeText
                if len(repDict) > 0:
                    for key in repDict:
                        extKey = textIdPrefix+str(totalGenerateCount)
                        totalGenerateCount = totalGenerateCount+1
                        extract[extKey] = repDict[key]
                        repDict[key] = extKey

                    repdText = xRayXmlParser.replaceFromText(
                        wholeText, repDict)

                if len(repDict) > 0 or outputWhenEmpty:
                    xRayXmlParser.generateOutputFileFromString(
                        os.path.join(doneDir, xRFile), repdText, needXmlHeader=False, encoding=successEncoding)
                print("")

            elif transFunction.startswith('script'):
                pathSteps = xRFile.split(os.path.sep)
                if pathSteps[-1].lower().count(".script") < 1:
                    i = i+1
                    continue
                wholeText, candidates = xRayXmlParser.parse_xray_script_file(
                    fullPath, ['cp1251', 'cp1252', 'utf-8'])
                repDict = {}
                for candWithQuote in candidates:
                    thisQuoteChar = candWithQuote[0]
                    cand = candWithQuote[1:-1]
                    if cand in reuseTexts:
                        print('!', end='')
                        continue
                    if xRayXmlParser.doesTextLookLikeId(cand) or xRayXmlParser.doesTextLookLikeScript(cand):
                        continue
                    transedStr = translateOneString(
                        cand, globalTranslator.autoLangCode)

                    if "chars_all_in" not in extract:
                        extract["chars_all_in"] = set()

                    for char in transedStr:
                        extract["chars_all_in"].add(char)

                    # escape back
                    repDict[thisQuoteChar+xRayXmlParser.escapeLiteralText(
                        cand, quote=thisQuoteChar)+thisQuoteChar] = thisQuoteChar+xRayXmlParser.escapeLiteralText(transedStr, quote=thisQuoteChar)+thisQuoteChar
                repdText = wholeText
                if len(repDict) > 0:
                    repdText = xRayXmlParser.replaceFromText(
                        wholeText, repDict)

                if len(repDict) > 0 or outputWhenEmpty:
                    xRayXmlParser.generateOutputFileFromString(os.path.join(
                        doneDir, xRFile), repdText, needXmlHeader=False)
                print("")

        elif os.path.isdir(fullPath) and transFunction in ['ltx', 'scriptL', 'scriptE', 'cfgxml']:
            if not xRFile == "translated_"+engine and not xRFile.endswith(".git"):
                subs = os.listdir(fullPath)
                for sub in subs:
                    subPath = os.path.join(xRFile, sub)
                    lst.append(subPath)
                    nextDoneDir = os.path.join(doneDir, xRFile)
                    if not os.path.exists(nextDoneDir):
                        os.mkdir(nextDoneDir)

        else:
            print("\n"+fullPath+" is not a file or already existed.")

        # end one round
        i = i+1

    if transFunction in ['scriptL', 'ltx'] and "chars_all_in" in extract:
        pie = xRayXmlParser.splitTextToPiecesAtLength(
            "".join(extract["chars_all_in"]), 500)
        extract.clear()
        for i in range(len(pie)):
            extract["text_gen_for_font_"+str(i)] = pie[i]

    if transFunction in ['cfgxml', 'scriptL', 'ltx']:
        xRayXmlParser.generateOutputXml(os.path.join(
            doneDir, "___" + transFunction+"__put_this_to_text_folder.xml"), extract)

    print("\n\nAll done! Congratulations! Now generate localization pack and have fun!")
    print("translated files are located at " + doneDir)
    print("total request:"+str(globalReqCount))
    print("total char:"+str(globalTransChars))
    print("these ids are redundant, please check manually:")
    print("["+", ".join(redundantIds)+"]")


if __name__ == "__main__":
    main(sys.argv)
