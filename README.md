S.T.A.L.K.E.R. Game(X-Ray Engine) Text Auto-Translator, using with language pack generator is recommended.  
Version 2.0.2, Updated at Jul 11th 2022  
by wzyddgFB from baidu S.T.A.L.K.E.R. tieba  
  
Options:  
  -e &lt;value&gt;|--engine=&lt;value&gt;               use what translate engine.  
                                                eg: baidu qq deepl  
  -p &lt;value&gt;|--path=&lt;value&gt;                 path of target folder.  
                                                always quote with ""  
  -t &lt;value&gt;|--toLang=&lt;value&gt;               translate to what language.  
                                                eg: eng chs  
  -i &lt;value&gt;|--appId=&lt;value&gt;                (Optional)appId of engine.  
                                                required for baidu  
  -k &lt;value&gt;|--appKey=&lt;value&gt;               (Optional)appKey of engine.  
                                                required for baidu  
  -f &lt;value&gt;|--fromLang=&lt;value&gt;             (Optional)from what language.  
                                                default rus. eg: eng rus ukr  
  -a &lt;value&gt;|--analyzeCharCount=&lt;value&gt;     (Optional)more than how many chars does the sentence need qq analyze.  
                                                default 0, means don't analyze(qq engine only)  
  -r &lt;value&gt;|--reusePath=&lt;value&gt;            (Optional)path of existing translated xml folder.  
                                                for gameplay translating text id protecting or text translating accelerating, always quote with ""  
  -c        |--runnableCheck                (Optional)just analyze files.  
                                                won't do translation.  
  --forceTransFiles=&lt;value&gt;                 (Optional)files that ignore reuse.  
                                                concat with ','. eg: a.xml,b.xml  
  --function=&lt;value&gt;                        (Optional)translating function. default text. eg: text gameplay script.  
                                                when ltx, program will recursively translate all ltx files.  
