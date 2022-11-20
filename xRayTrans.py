from time import time
import xRayXmlParser
import webTranslator
import os
import sys
import getopt


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
    targetLang = None
    appId = None
    appKey = None
    analyzeCharCount = 0
    runnableCheck = False
    forceTrans = []
    transFunction = 'text'
    outputWhenEmpty = False

    opts, args = getopt.getopt(argv[1:], "choe:i:k:f:t:p:a:r:", [
                               "runnableCheck", "help", "outputWhenEmpty", "engine=", "appId=", "appKey=", "fromLang=", "toLang=", "path=", "forceTransFiles=", "reusePath=", "analyzeCharCount=", "function="])
    print(opts)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            helpText = """
S.T.A.L.K.E.R. Game(X-Ray Engine) Text Auto-Translator, using with language pack generator is recommended.
Version 2.0.2, Updated at Aug 13th 2022
by wzyddgFB from baidu S.T.A.L.K.E.R. tieba

Options:
  -e <value>|--engine=<value>               use what translate engine.
                                                eg: baidu qq deepl
  -p <value>|--path=<value>                 path of target folder.
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
                                                for gameplay translating text id protecting or text translating accelerating, always quote with ""
  -c        |--runnableCheck                (Optional)just analyze files.
                                                won't do translation.
  -o        |--outputWhenEmpty              (Optional)generate output file even this file has nothing translated.
                                                for gameplay/script/ltx, for solving #include encoding problem.
  --forceTransFiles=<value>                 (Optional)files that ignore reuse.
                                                concat with ','. eg: a.xml,b.xml
  --function=<value>                        (Optional)translating function. default text. eg: text gameplay script ltx.
                                                when ltx, program will recursively translate all ltx files.
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
        elif opt in ("--forceTransFiles"):
            forceTrans = arg.split(",")
        elif opt in ("--function"):
            transFunction = arg

    # validation
    assert engine is not None, "engine must be provided."
    assert textDir is not None, "text folder path must be provided."
    assert targetLang is not None, "target language must be provided."
    if engine == 'baidu':
        assert appId is not None and appKey is not None, "when using baidu, AppId and AppKey must be provided, see https://fanyi-api.baidu.com/api/trans/product/desktop"

    # preparation

    def getTranslator(e) -> webTranslator.WebTranslator:
        if e == 'qq':
            return webTranslator.TransmartQQTranslator(analyzeCharCount)
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
    reuseTexts = {}
    if reuseDir is not None:
        reLst = os.listdir(reuseDir)
        print("")
        for reFile in reLst:
            reFullPath = os.path.join(reuseDir, reFile)
            if os.path.isfile(reFullPath):
                print("reading exiting translated file:"+reFile)
                exEnts = xRayXmlParser.parse_xray_text_xml(
                    reFullPath, ['utf-8', 'cp1252', 'cp1251'])
                for ent in exEnts:
                    reuseTexts[ent.id] = xRayXmlParser.getRecommendLangText(ent, "chs")[
                        1]

    globalReqCount = 0
    globalTransChars = 0
    globalTranslator = getTranslator(engine)
    benchPlayerTrans = getBenchPlayerTrans(engine)
    pastIds = []
    redundantIds = []

    def translateOneString(text: str, fl: str):
        pieces = xRayXmlParser.cutText(text)
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
                            transedPie = benchPlayerTrans.doTranslate(
                                piece["content"], langCode, targetLang)
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

                    chosen = xRayXmlParser.getRecommendLangText(entity, "chs")
                    transedStr = translateOneString(chosen[1], chosen[0])
                    doneHere[entity.id] = transedStr

                xRayXmlParser.generateOutputXml(
                    os.path.join(doneDir, xRFile), doneHere)
                print("")

            elif transFunction == 'gameplay':
                pathSteps = xRFile.split(os.path.sep)
                if pathSteps[-1].lower().count(".xml") < 1 or "text" in pathSteps:
                    i = i+1
                    continue
                wholeText, candidates, successEncoding = xRayXmlParser.parse_xray_gameplay_xml(
                    fullPath, ['cp1251', 'cp1252', 'utf-8', 'cp1251'])
                repDict = {}
                for cand in candidates:
                    if cand in reuseTexts:
                        print('!', end='')
                        continue
                    if xRayXmlParser.doesTextLookLikeId(cand):
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

            elif transFunction == 'script':
                pathSteps = xRFile.split(os.path.sep)
                if pathSteps[-1].lower().count(".script") < 1:
                    i = i+1
                    continue
                wholeText, candidates = xRayXmlParser.parse_xray_script_file(
                    fullPath, ['cp1251', 'cp1252', 'utf-8'])
                repDict = {}
                for candWithQuote in candidates:
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
                    repDict['"'+xRayXmlParser.escapeLiteralText(
                        cand)+'"'] = '"'+xRayXmlParser.escapeLiteralText(transedStr)+'"'
                repdText = wholeText
                if len(repDict) > 0:
                    repdText = xRayXmlParser.replaceFromText(
                        wholeText, repDict)

                if len(repDict) > 0 or outputWhenEmpty:
                    xRayXmlParser.generateOutputFileFromString(os.path.join(
                        doneDir, xRFile), repdText, needXmlHeader=False)
                print("")

        elif os.path.isdir(fullPath) and transFunction in ['ltx', 'script', 'gameplay']:
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

    if transFunction in ['script', 'ltx'] and "chars_all_in" in extract:
        pie = xRayXmlParser.splitTextToPiecesAtLength(
            "".join(extract["chars_all_in"]), 500)
        # dasd
        extract.clear()
        for i in range(len(pie)):
            extract["text_gen_for_font_"+str(i)] = pie[i]

    if transFunction in ['gameplay', 'script', 'ltx']:
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
