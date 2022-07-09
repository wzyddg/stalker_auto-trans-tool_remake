import xRayXmlParser
import webTranslator
import os
import sys
import getopt
import re


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

    opts, args = getopt.getopt(argv[1:], "che:i:k:f:t:p:a:r:", [
                               "runnableCheck", "help", "engine=", "appId=", "appKey=", "fromLang=", "toLang=", "path=", "forceTransFiles=", "reusePath=", "analyzeCharCount=", "function="])

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            helpText = """
S.T.A.L.K.E.R. Game(X-Ray Engine) Text Auto-Translator, using with language pack generator is recommended.
Version 2.0.2, Updated at Jul 9th 2022
by wzyddgFB from baidu S.T.A.L.K.E.R. tieba

Options:
  -e <value>|--engine=<value>                   use what translate engine, eg: baidu qq deepl
  -p <value>|--path=<value>                     path of xml folder, always quote with ""
  -t <value>|--toLang=<value>                   to what language, eg: eng chs
  -c |--runnableCheck                           (Optional)just analyze files, won't do translation
  -i <value>|--appId=<value>                    (Optional)appId of engine, required for baidu
  -k <value>|--appKey=<value>                   (Optional)appKey of engine, required for baidu
  -f <value>|--fromLang=<value>                 (Optional)from what language if string uses text tag, default rus. eg: eng rus ukr
  -a <value>|--analyzeCharCount=<value>         (Optional)more than how many chars does the sentence need qq analyze,
                                                    default 0, means don't analyze(qq engine only)
  -r <value>|--reusePath=<value>                (Optional)path of existing translated xml folder.
                                                    for gameplay translating text id protecting or text translating accelerating
  --forceTransFiles=<value>                     (Optional)for listed files, ignore existing translated xml files.
                                                    concat with ','  eg: a.xml,b.xml
  --function=<value>                            (Optional)translating function, default text. eg: text gameplay
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
    doneFileLst = os.listdir(doneDir)

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
                    reFullPath, ['utf-8', 'cp1251'])
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
            if(piece["needTrans"]):
                langCode = fl
                if(langCode == 'text'):
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

    for xRFile in lst:
        fullPath = os.path.join(textDir, xRFile)
        if os.path.isfile(fullPath) and xRFile not in doneFileLst:
            print("\n\n"+xRFile+":")

            if transFunction == 'text':
                texts = xRayXmlParser.parse_xray_text_xml(
                    fullPath, ['cp1251', 'utf-8'])
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
                    transedWholeText = translateOneString(chosen[1], chosen[0])
                    doneHere[entity.id] = transedWholeText

                xRayXmlParser.generateOutputXml(
                    os.path.join(textDir, "translated_"+engine, xRFile), doneHere)
                print("")

            else:
                wholeText, candidates = xRayXmlParser.parse_xray_gameplay_xml(
                    fullPath, ['cp1251', 'utf-8'])
                for cand in candidates:
                    if(cand in reuseTexts):
                        continue
                    res = noLettersPattern.fullmatch(piece)
                    # todo
                    pass
        else:
            print("\n\n"+fullPath+" is not a file or already existed.")

    print("\n\nAll done! Congratulations! Now generate localization pack and have fun!")
    print("translated files are located at " +
          os.path.join(textDir, "translated_"+engine))
    print("total request:"+str(globalReqCount))
    print("total char:"+str(globalTransChars))
    print("these ids are redundant, please check manually:")
    print("["+", ".join(redundantIds)+"]")


if __name__ == "__main__":
    main(sys.argv)
