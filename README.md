# STALKER_AutoTransTool_Remake

I'm that lazy to just put -h info here ;)

require python 3.9 and poetry, you can pack it into .exe with pyinstaller like me.

————————————————————————————————————————————

S.T.A.L.K.E.R. Game(X-Ray Engine) Text Auto-Translator, using with language pack generator is recommended.
Version 2.0.2, Updated at Jul 10th 2022
by wzyddgFB from baidu S.T.A.L.K.E.R. tieba

Options:
  -e <value>|--engine=<value>                   use what translate engine. eg: baidu qq deepl
  -p <value>|--path=<value>                     path of target folder, always quote with ""
  -t <value>|--toLang=<value>                   translate to what language. eg: eng chs
  -i <value>|--appId=<value>                    (Optional)appId of engine, required for baidu
  -k <value>|--appKey=<value>                   (Optional)appKey of engine, required for baidu
  -f <value>|--fromLang=<value>                 (Optional)from what language if string uses text tag, default rus. eg: eng rus ukr
  -a <value>|--analyzeCharCount=<value>         (Optional)more than how many chars does the sentence need qq analyze,
                                                    default 0, means don't analyze(qq engine only)
  -r <value>|--reusePath=<value>                (Optional)path of existing translated xml folder.
                                                    for gameplay translating text id protecting or text translating accelerating
  -c        |--runnableCheck                    (Optional)just analyze files, won't do translation
  --forceTransFiles=<value>                     (Optional)for listed files, ignore existing translated xml files.
                                                    concat with ','. eg: a.xml,b.xml
  --function=<value>                            (Optional)translating function, default text. eg: text gameplay
 
