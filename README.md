# STALKER_AutoTransTool_Remake

I'm that lazy to just put -h info here ;)

require python 3.9 and poetry, you can pack it into .exe with pyinstaller like me.

————————————————————————————————————————————

S.T.A.L.K.E.R. Game(X-Ray Engine) Text Auto-Translator, using with language pack generator is recommended.

Version 2.0.1, Updated at Jul 1st 2022     

by wzyddgFB from baidu S.T.A.L.K.E.R. tieba

usage:
    python .\app.py -e <use what translate engine, eg: baidu qq> -i <(Optional)appId of engine> -k <(Optional)appKey of engine> -f <(Optional)from 
what language if string uses text tag, eg: eng rus ukr> -t <to what language, eg: eng chs> -p <path of text xml folder> -r <(Optional)path of existing translated xml folder for translation reuse> -a <(Optional)more than how many characters does the sentence need qq analyze, default 0, means don't analyze(qq engine only)>

or: python .\app.py --engine=<use what translate engine> --appId=<appId of engine> --appKey=<appKey of engine> --fromLang=<(Optional)from what language> --toLang <to what language> --path=<path of text xml folder> --reusePath <(Optional)path of existing translated xml folder> --analyzeCharCount=<(Optional)how many characters need qq analyze>
