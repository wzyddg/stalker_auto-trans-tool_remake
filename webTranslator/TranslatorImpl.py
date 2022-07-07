from hashlib import md5
import re
from time import sleep, time
import timeit
from typing import Any, Dict, Tuple
from .entityDefinition import WebTranslator
import urllib
import requests
import json
import base64
import random


class TransmartQQTranslator(WebTranslator):
    __langCodeMap = {
        "chs": "zh",
        "eng": "en",
        "rus": "ru"
    }

    def __init__(self, needAnalyzeCharCount: int = 0):
        super().__init__()
        print("\nTransmartQQTranslator only support chs/eng as output!")
        self.clientKey = ""
        self.needAnalyzeCharCount = needAnalyzeCharCount
        self.analyzeApi = "https://transmart.qq.com/api/imt"
        self.mainTransApi = "https://transmart.qq.com/api/imt"
        self.eachRequestGap = 0

    def getApiLangCode(self, textLang: str) -> str:
        return TransmartQQTranslator.__langCodeMap[textLang]

    def getClientKey(self):
        ua = b'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
        self.clientKey = base64.b64encode(ua).decode("utf-8")[0:100]

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

        if(timeit.default_timer()-self.lastRequest < self.eachRequestGap):
            sleep(self.eachRequestGap)
        body = {"header": {"fn": "auto_translation", "client_key": self.clientKey},
                "type": "plain", "model_category": "normal", "source": {"lang": self.getApiLangCode(fromLang), "text_list": textList}, "target": {"lang": self.getApiLangCode(toLang)}}
        response = None
        try:
            response = requests.post(self.mainTransApi, json=body)
        except requests.exceptions.ConnectionError:
            print("(aborted, wait " + str(self.timedOutGap) + "s and try again)")
            sleep(self.timedOutGap)
            # maybe set self.clientKey = "" here
            return self.doTranslate(text, fromLang, toLang)
        resJson = json.loads(response.text)
        self.lastRequest = timeit.default_timer()
        res = ""
        if resJson["header"]["ret_code"] == 'succ':
            # res = resJson["auto_translation"][0]
            for txt in resJson["auto_translation"]:
                res = res + txt
        else:
            if resJson["header"]["ret_code"] == 'error' and "timed out" in resJson['message']:
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
                raise KeyError
        return res


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
        if(timeit.default_timer()-self.lastRequest < self.eachRequestGap):
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
            if resJson["error_code"] == '52001':
                print("(timed out, wait " + str(self.timedOutGap) + "s and try again)")
                sleep(self.timedOutGap)
                return self.doTranslate(text, fromLang, toLang)
            else:
                raise err
        return res

    def getApiLangCode(self, textLang: str) -> str:
        return BaiduTranslator.__langCodeMap[textLang]

    def generateSign(self, query: str) -> str:
        chunk = self.appid+query+BaiduTranslator.fixedSalt+self.appkey
        sign = md5(chunk.encode("utf-8"))
        return sign.hexdigest()


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
        self.eachRequestGap = 0.5

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

        entities = []
        for i in range(len(texts)):
            entities.append(1)

        return []

    def doTranslate(self, text: str, fromLang: str, toLang: str, isRetry: bool = False) -> str:
        textPairs = self.analyzeTextByEngine(text, fromLang)
        body = {
            "jsonrpc": "2.0",
            "method": "LMT_handle_jobs",
            "params": {
                "jobs": self.generateJobs(textPairs),
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
        pass
