from hashlib import md5
import re
import math
from time import sleep, time
import timeit
from typing import Any, Dict, Tuple
from .entityDefinition import WebTranslator
import urllib
import requests
import json
import base64
import random


class BingTranslator(WebTranslator):
    '''
    request https://www.bing.com/translator
    find definition of params_AbusePreventionHelper and _G
    then find IG, IID, token, key
    '''

    abusePreventionHelper = None
    IG_param = None
    initTime = None
    curHost = None

    timedOutGap = 1
    captchaTimeOut = 10

    __langCodeMap = {
        "chs": "zh-Hans",
        "eng": "en",
        "auto": "auto-detect",
        "rus": "ru"
    }

    def __init__(self):
        super().__init__()
        self.initTime = timeit.default_timer()
        print("Init Bing Engine, get key and IG.")
        try:
            # for world wide
            # response = requests.get("https://www.bing.com/translator")

            # this works better in China
            response = requests.get("https://cn.bing.com/translator")
            lines = response.text.split("\n")
            for line in lines:
                normLine = re.sub(r'\s*=\s*', '=', line).strip()

                abusePtn = re.compile(
                    r"var params_AbusePreventionHelper=([^;]+);")
                pars = abusePtn.findall(normLine)
                if (len(pars) > 0):
                    self.abusePreventionHelper = json.loads(pars[0])
                    continue

                _GPtn = re.compile(r"_G=([^;]+);")
                _gs = _GPtn.findall(normLine)
                if (len(_gs) > 0):
                    IGPtn = re.compile(r'IG:"([^"]+)"')
                    try:
                        self.IG_param = IGPtn.findall(_gs[0])[0]
                    except KeyError:
                        pass

                # curUrl="https:\/\/cn.bing.com\/translator";
                # hostPtn= re.compile(r'curUrl="([^"]+)"')
                hostPtn = re.compile(r'curUrl="([^"]+)"')
                hosts = hostPtn.findall(normLine)
                if (len(hosts) > 0):
                    url = hosts[0]
                    url = re.sub(r'/translator/?|\\', '', url).strip()
                    self.curHost = url

        except KeyError:
            pass

    def getApiLangCode(self, textLang: str) -> str:
        return BingTranslator.__langCodeMap[textLang]

    def doTranslate(self, text: str, fromLang: str, toLang: str, isRetry: bool = False) -> str:
        if fromLang == self.autoLangCode:
            fromLang = self.detectLang(text)
        runFL = self.getApiLangCode(fromLang)
        runTL = self.getApiLangCode(toLang)

        gap = timeit.default_timer()-self.initTime
        if gap > self.abusePreventionHelper[2]/1000-1:
            self.__init__()
        transApi = self.curHost+"/ttranslatev3?isVertical=1&&IG=" + \
            self.IG_param+"&IID=translator.5027"

        # safe for http form, maybe useless, but why not
        if len(text) > 1000:
            sentences = self.cutSentenceWithLineEnds(text)
            mid = math.floor(len(sentences)/2)
            return self.doTranslate("".join(sentences[0:mid]), fromLang, toLang)+self.doTranslate("".join(sentences[mid:]), fromLang, toLang)

        form = {
            "fromLang": runFL,
            "to": runTL,
            "text": text,
            "token": self.abusePreventionHelper[1],
            "key": self.abusePreventionHelper[0],
            "tryFetchingGenderDebiasedTranslations": "true"
        }
        paramsStr = "&"+urllib.parse.urlencode(form)

        response = None
        try:
            response = requests.post(transApi, data=paramsStr, headers={
                                     'Content-Type': 'application/x-www-form-urlencoded',
                                     'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47"
                                     })
        except (requests.exceptions.ConnectionError, requests.exceptions.SSLError) as exc:
            print("(connection or retry problem, retry)")
            sleep(self.captchaTimeOut)
            return self.doTranslate(text, fromLang, toLang)

        if len(response.text) > 0:
            try:
                resJson = json.loads(response.text)
                res = resJson[0]["translations"][0]["text"]
                sleep(1)
                return self.resultFilter(text, res)
            except KeyError:
                print(response.text)
                if "Captcha" in response.text:
                    sleep(self.captchaTimeOut)
                    self.__init__()
                    return self.doTranslate(text, fromLang, toLang, isRetry=True)


class GoogleTranslator(WebTranslator):

    __langCodeMap = {
        "chs": "zh-CN",
        "eng": "en",
        "auto": "auto",
        "rus": "ru",
        "ukr": "uk"
    }

    def __init__(self):
        super().__init__()
        self.mainTransApi = 'https://translate.googleapis.com/translate_a/single'
        self.eachRequestGap = 1
        self.timedOutGap = 1
        self.lastRequest
        self.safeEncodedLength = 14678

    def getApiLangCode(self, textLang: str) -> str:
        return GoogleTranslator.__langCodeMap[textLang]

    def resultFilter(self, sourceText: str, resultText: str) -> str:
        return resultText

    def cutSentenceWithLineEnds(self, text: str, lineEnds: list[str] = ["?", ".", "!"]) -> list[str]:
        lineEndPtn = re.compile("["+"".join(lineEnds)+"]+")
        seps = lineEndPtn.findall(text)
        pieces = lineEndPtn.split(text)
        assert len(pieces) == len(seps) + \
            1, "separator and pieces count won't match"
        sentences = []
        for i in range(len(seps)):
            sentences.append(pieces[i]+seps[i])
        if len(sentences) > 0:
            sentences[-1] = sentences[-1]+pieces[-1]
        return sentences

    def doTranslate(self, text: str, fromLang: str, toLang: str, isRetry: bool = False) -> str:
        if fromLang == self.autoLangCode:
            fromLang = self.detectLang(text)
        runFL = self.getApiLangCode(fromLang)
        runTL = self.getApiLangCode(toLang)

        if timeit.default_timer()-self.lastRequest < self.eachRequestGap:
            sleep(self.eachRequestGap)
        params = {
            "client": "gtx",
            "q": text,
            "sl": runFL,
            "tl": runTL,
            "dt": "t",
            # # this is by json object
            # "dj": "1",
            "ie": "UTF-8",
            "oe": "UTF-8"
        }
        paramsStr = urllib.parse.urlencode(params)

        # add GET length limit for google, last known safe length: 14678, maybe max 16k
        if len(self.mainTransApi+"?"+paramsStr) > self.safeEncodedLength:
            sentences = self.cutSentenceWithLineEnds(text)
            mid = math.floor(len(sentences)/2)
            return self.doTranslate("".join(sentences[0:mid]), fromLang, toLang)+self.doTranslate("".join(sentences[mid:]), fromLang, toLang)

        response = None
        try:
            response = requests.get(self.mainTransApi+"?"+paramsStr)
        except requests.exceptions.ConnectionError as exc:
            if exc.args[0].reason.original_error.errno in [10054, 8]:
                print("(10054 or 8 socket problem, retry)")
                sleep(self.timedOutGap)
                return self.doTranslate(text, fromLang, toLang)
            else:
                pass

        resJson = json.loads(response.text)
        self.lastRequest = timeit.default_timer()
        res = ""

        # # this is by json object
        # if "sentences" in resJson:
        #     for sent in resJson["sentences"]:
        #         res = res + sent["trans"]
        # else:
        #     # to be found
        #     print("(can't translate, return original string)")
        #     print(str(resJson))
        #     return text
        try:
            gglPieces = resJson[0]
            for gp in gglPieces:
                res = res+gp[0]
        except KeyError:
            # to be found
            print("(can't translate, return original string)")
            print(str(resJson))
            return text

        return self.resultFilter(text, res)


class TransmartQQTranslator(WebTranslator):
    __langCodeMap = {
        "chs": "zh",
        "eng": "en",
        "rus": "ru"
    }

    def __init__(self, needAnalyzeCharCount: int = 0, userAgent: str = ""):
        super().__init__()
        print("\nTransmartQQTranslator only support chs/eng as output!")
        self.getClientKey(userAgent)
        self.needAnalyzeCharCount = needAnalyzeCharCount
        self.analyzeApi = "https://transmart.qq.com/api/imt"
        self.mainTransApi = "https://transmart.qq.com/api/imt"
        self.eachRequestGap = 0

    def getApiLangCode(self, textLang: str) -> str:
        return TransmartQQTranslator.__langCodeMap[textLang]

    def getClientKey(self, userAgent: str = ""):
        if len(userAgent.strip()) == 0:
            userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
        ua = bytes(userAgent, "utf-8")
        self.clientKey = base64.b64encode(ua).decode("utf-8")[0:100]

    def resultFilter(self, sourceText: str, resultText: str) -> str:
        # this is for tencent engine bug, somethimes double the result, and maybe a wide comma between.
        resFind = re.findall(r"^([\S\s]+)[\s：]*\1$", resultText.strip())
        if len(resFind) > 0:
            if len(re.findall(r"^([\S\s]+)[\s:：]*\1$", sourceText.strip())) == 0:
                return resFind[0]
        return resultText

    def analyzeTextByEngine(self, text: str) -> list[str]:
        anabody = {"header": {"fn": "text_analysis", "client_key": self.clientKey},
                   "type": "plain", "text": text}
        anaresponse = requests.post(self.analyzeApi, json=anabody)
        anaresJson = json.loads(anaresponse.text)
        texts = []
        for senten in anaresJson['sentence_list']:
            texts.append(senten["str"])
        return texts

    def doTranslate(self, text: str, fromLang: str, toLang: str, isRetry: bool = False) -> str:
        if fromLang == self.autoLangCode:
            fromLang = self.detectLang(text)

        if len(self.clientKey) == 0:
            self.getClientKey()
        textList = [text]

        if len(text) > self.needAnalyzeCharCount and self.needAnalyzeCharCount > 0:
            try:
                textList = self.analyzeTextByEngine(text)
            except ConnectionError:
                pass

        if timeit.default_timer()-self.lastRequest < self.eachRequestGap:
            sleep(self.eachRequestGap)
        body = {"header": {"fn": "auto_translation", "client_key": self.clientKey},
                "type": "plain", "model_category": "normal", "source": {"lang": self.getApiLangCode(fromLang), "text_list": textList}, "target": {"lang": self.getApiLangCode(toLang)}}
        response = None
        try:
            response = requests.post(self.mainTransApi, json=body)
        except requests.exceptions.ConnectionError as exc:
            print("(aborted: "+str(exc.args[0].reason.original_error.errno) +
                  ", wait " + str(self.timedOutGap) + "s and try again)")
            sleep(self.timedOutGap)
            # maybe set self.clientKey = "" here
            return self.doTranslate(text, fromLang, toLang)

        try:
            resJson = json.loads(response.text)
        except Exception:
            # incomplete request, fake a busy
            resJson = {"header": {"ret_code": "busy"}}

        self.lastRequest = timeit.default_timer()
        res = ""
        if resJson["header"]["ret_code"] == 'succ':
            # res = resJson["auto_translation"][0]
            for txt in resJson["auto_translation"]:
                res = res + txt
        else:
            if resJson["header"]["ret_code"] == 'error' and ("timed out" in resJson['message'] or "retry" in resJson['message']) or resJson["header"]["ret_code"] in ['busy']:
                print("(timed out, wait " + str(self.timedOutGap) + "s and try again)")
                sleep(self.timedOutGap)
                # maybe set self.clientKey = "" here
                return self.doTranslate(text, fromLang, toLang)
            elif resJson["header"]["ret_code"] in ['IndexOutOfBoundsException', 'ResourceAccessException']:
                print("(engine bug, normalize string)")
                if not isRetry:
                    return self.doTranslate(re.sub(r'\s+', ' ', text).strip(), fromLang, toLang, isRetry=True)
                else:
                    print("(can't translate, return original string)")
                    return text
            else:
                print("(can't translate, return original string)")
                print(str(resJson))
                return text
        return self.resultFilter(text, res)


class BaiduTranslator(WebTranslator):
    __langCodeMap = {
        "chs": "zh",
        "eng": "en",
        "rus": "ru",
        "ukr": "ukr"
    }

    fixedSalt = "letitburn"

    def __init__(self, appid: str, appkey: str):
        super().__init__()
        self.appid = appid
        self.appkey = appkey
        self.mainTransApi = "https://fanyi-api.baidu.com/api/trans/vip/translate"

    def doTranslate(self, text: str, fromLang: str, toLang: str, isRetry: bool = False) -> str:
        if fromLang == self.autoLangCode:
            fromLang = self.detectLang(text)

        # only sleep if really gonna call api
        if timeit.default_timer()-self.lastRequest < self.eachRequestGap:
            sleep(self.eachRequestGap)
        params = {
            "from": self.getApiLangCode(fromLang),
            "to": self.getApiLangCode(toLang),
            "q": text,
            "appid": self.appid,
            "salt": BaiduTranslator.fixedSalt,
            "sign": self.generateSign(text)
        }
        paramsStr = urllib.parse.urlencode(params)
        response = requests.get(self.mainTransApi+"?"+paramsStr)
        resJson = json.loads(response.text)
        self.lastRequest = timeit.default_timer()

        try:
            res = resJson["trans_result"][0]["dst"]
        except KeyError as err:
            if resJson["error_code"] == '52001' and not isRetry:
                print("(timed out, wait " + str(self.timedOutGap) + "s and try again)")
                sleep(self.timedOutGap)
                return self.doTranslate(text, fromLang, toLang, isRetry=True)
            else:
                print("(can't translate, return original string)")
                return text
        return res

    def getApiLangCode(self, textLang: str) -> str:
        return BaiduTranslator.__langCodeMap[textLang]

    def generateSign(self, query: str) -> str:
        chunk = self.appid+query+BaiduTranslator.fixedSalt+self.appkey
        sign = md5(chunk.encode("utf-8"))
        return sign.hexdigest()


# Deprecated, can't use DeepL for free
class DeepLTranslator(WebTranslator):
    __langCodeMap = {
        "chs": "ZH",
        "eng": "EN",
        "rus": "RU"
    }

    def __init__(self):
        super().__init__()
        self.analyzeApi = "https://www2.deepl.com/jsonrpc?method=LMT_split_text"
        self.mainTransApi = "https://www2.deepl.com/jsonrpc?method=LMT_handle_jobs"
        self.eachRequestGap = 3
        self.timedOutGap = 5
        self.jobsPerRequest = 12

    def getApiLangCode(self, textLang: str) -> str:
        return DeepLTranslator.__langCodeMap[textLang]

    # [(prefix,text)]
    def analyzeTextByEngine(self, text: str, lang: str) -> list[Tuple[str, str]]:
        anabody = {
            "jsonrpc": "2.0",
            "method": "LMT_split_text",
            "params": {
                "texts": [
                    text
                ],
                "lang": {
                    "lang_user_selected": self.getApiLangCode(lang),
                    "preference": {
                        "weight": {
                            self.getApiLangCode(lang): random.uniform(8, 10)
                        },
                        "default": "default"
                    }
                }
            },
            "id": random.randint(10000000, 100000000)
        }

        anaresponse = requests.post(self.analyzeApi, json=anabody)
        anaresJson = json.loads(anaresponse.text)
        digIntoRes = anaresJson["result"]["texts"][0]["chunks"]
        texts = []
        for chunk in digIntoRes:
            senten = chunk["sentences"][0]
            texts.append((senten["prefix"], senten["text"]))
        return texts

    def generateJobs(self, texts: list[Tuple[str, str]]) -> list[Dict[str, Any]]:
        # before 5 after 1
        # prefix strip
        # 12 entiy a request, context shared, id not reset in next request

        if len(texts) == 1:
            preferred_num_beams = 4
        else:
            preferred_num_beams = 1

        jobs = []
        for i in range(len(texts)):
            theEnt = texts[i]
            theJob = {
                "kind": "default",
                "sentences": [
                    {
                        "text": theEnt[1],
                        "id": i,
                        "prefix": theEnt[0].strip()
                    }
                ],
                "raw_en_context_before": [],
                "raw_en_context_after": [],
                "preferred_num_beams": preferred_num_beams
            }
            for j in range(max(0, i-5), max(0, i)):
                theJob["raw_en_context_before"].append(texts[j][1])

            if i+1 < len(texts):
                theJob["raw_en_context_after"].append(texts[i+1][1])

            jobs.append(theJob)

        return jobs

    def transWithRange(self, jobs: list[Dict[str, Any]], start: int, end: int, fromLang: str, toLang: str) -> str:
        body = {
            "jsonrpc": "2.0",
            "method": "LMT_handle_jobs",
            "params": {
                "jobs": jobs[start:end],
                "lang": {
                    "preference": {
                        "weight": {},
                        "default": "default"
                    },
                    "source_lang_computed": self.getApiLangCode(fromLang),
                    "target_lang": self.getApiLangCode(toLang)
                },
                "priority": 1,
                "commonJobParams": {
                    "browserType": 1,
                    "formality": None
                },
                "timestamp": int(time()*1000)
            },
            "id": random.randint(10000000, 100000000)
        }

        try:
            response = requests.post(self.mainTransApi, json=body)
        except requests.exceptions.ConnectionError:
            print("(aborted, wait " + str(self.timedOutGap) + "s and try again)")
            sleep(self.timedOutGap)
            # maybe set self.clientKey = "" here
            return self.transWithRange(jobs, start, end, fromLang, toLang)
        resJson = json.loads(response.text)
        self.lastRequest = timeit.default_timer()
        res = ""
        # if resJson["header"]["ret_code"] == 'succ':
        if 1 == 1:
            # res = resJson["auto_translation"][0]
            for txt in resJson["result"]["translations"]:
                res = res + txt["beams"][0]["sentences"][0]["text"]
        else:
            raise ValueError

        return res

    def doTranslate(self, text: str, fromLang: str, toLang: str) -> str:
        if fromLang == self.autoLangCode:
            fromLang = self.detectLang(text)

        # if this goes wrong means this engine wont do
        textPairs = self.analyzeTextByEngine(text, fromLang)

        if timeit.default_timer()-self.lastRequest < self.eachRequestGap:
            sleep(self.eachRequestGap)

        jobs = self.generateJobs(textPairs)

        res = ""
        for batchI in range(math.ceil(len(jobs)/self.jobsPerRequest)):
            # transWithRange(self, jobs: list[Dict[str, Any]], start: int, end: int, fromLang: str, toLang: str):
            res = res+self.transWithRange(jobs, batchI*self.jobsPerRequest, min(
                (batchI+1)*self.jobsPerRequest, len(jobs)), fromLang, toLang)

        return res
