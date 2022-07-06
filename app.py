import re
import xRayXmlParser
import webTranslator
import os
import sys
import getopt


def main(argv):

    # parameters
    engine = None
    sourceLangForTextTag = None
    textDir = None
    reuseDir = None
    targetLang = None
    appId = None
    appKey = None
    analyzeCharCount = 0
    runnableCheck = False

    opts, args = getopt.getopt(argv[1:], "che:i:k:f:t:p:a:r:", [
                               "runnableCheck", "help", "engine=", "appId=", "appKey=", "fromLang=", "toLang=", "path=", "reusePath=", "analyzeCharCount="])

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("\nS.T.A.L.K.E.R. Game(X-Ray Engine) Text Auto-Translator, using with language pack generator is recommended.\n")
            print("Version 2.0.1, Updated at Jul 1st 2022\n")
            print("by wzyddgFB from baidu S.T.A.L.K.E.R. tieba\n")
            print("usage:")
            print('    '+argv[0]+' -e <use what translate engine, eg: baidu qq> -i <(Optional)appId of engine> -k <(Optional)appKey of engine> -f <(Optional)from what language if string uses text tag, eg: eng rus ukr> -t <to what language, eg: eng chs> -p <path of text xml folder> -r <(Optional)path of existing translated xml folder for translation reuse> -a <(Optional)more than how many characters does the sentence need qq analyze, default 0, means don\'t analyze(qq engine only)>')
            print('\nor: '+argv[0]+' --engine=<use what translate engine> --appId=<appId of engine> --appKey=<appKey of engine> --fromLang=<(Optional)from what language> --toLang <to what language> --path=<path of text xml folder> --reusePath <(Optional)path of existing translated xml folder> --analyzeCharCount=<(Optional)how many characters need qq analyze>\n')
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
        elif e == 'baidu':
            return webTranslator.TransmartQQTranslator(1)

    # actual logic
    lst = os.listdir(textDir)
    doneDir = os.path.join(textDir, "translated")
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
                exEnts = xRayXmlParser.parse_xray_xml(
                    reFullPath, ['utf-8', 'cp1251'])
                for ent in exEnts:
                    reuseTexts[ent.id] = xRayXmlParser.getRecommendLangText(ent, "chs")[1]

    globalTranslator = getTranslator(engine)
    benchPlayerTrans = getBenchPlayerTrans(engine)

    globalReqCount = 0
    globalTransChars = 0

    pastIds = []
    redundantIds = []

    for xRFile in lst:
        fullPath = os.path.join(textDir, xRFile)
        if os.path.isfile(fullPath) and xRFile not in doneFileLst:
            print("\n\n"+xRFile+":")
            texts = xRayXmlParser.parse_xray_xml(fullPath, ['cp1251', 'utf-8'])
            print(" └──"+fullPath + " got " + str(len(texts)) + " texts!")
            doneHere = dict()
            for entity in texts:
                if entity.id in pastIds and entity.id not in redundantIds:
                    redundantIds.append(entity.id)
                else:
                    pastIds.append(entity.id)
                print(entity.id, end='')
                if entity.id in reuseTexts:
                    doneHere[entity.id] = reuseTexts[entity.id]
                    print('.', end='')
                    continue

                chosen = xRayXmlParser.getRecommendLangText(entity, "chs")
                pieces = xRayXmlParser.cutText(chosen[1])
                for piece in pieces:
                    if(piece["needTrans"]):
                        langCode = chosen[0]
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

                doneHere[entity.id] = transedWholeText

            xRayXmlParser.generateOutputXml(
                os.path.join(textDir, "translated", xRFile), doneHere)
            print("")

        else:
            print("\n\n"+fullPath+" is not a file or already existed.")

    print("\n\nAll done! Congratulations! Now generate localization pack and have fun!")
    print(r"translated files are located at {path}\translated")
    print("total request:"+str(globalReqCount))
    print("total char:"+str(globalTransChars))
    print("these ids are redundant, please check manually:")
    print("["+", ".join(redundantIds)+"]")


if __name__ == "__main__":
    main(sys.argv)
