S.T.A.L.K.E.R. Game(X-Ray Engine or like) Text Auto-Translator, using with language pack generator is recommended.  
Version 2.1.2, Updated at March 23th 2023  
by wzyddg(FB) from baidu S.T.A.L.K.E.R. tieba  
  
Options:  
  -e &lt;value&gt;|--engine=&lt;value&gt;               use what translate engine.  
                                                eg: baidu qq   
  -p &lt;value&gt;|--path=&lt;value&gt;                 path of the folder containing what you want to translate.  
                                                always quote with `""`  
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
                                                for cfgxml/script?/ltx translating text id protecting or text translating accelerating, always quote with `""`  
  -b &lt;value&gt;|--blackListIdJson=&lt;value&gt;      (Optional)path of force translate id json array file, even if it's in translated xml.  
                                                work with -r parameter. file content eg: `["dialog_sah_11","dialog_wolf_22"]`  
  --forceTransFiles=&lt;value&gt;                 (Optional)files that ignore reuse.  
                                                concat with `,`. eg: a.xml,b.xml  
  -c        |--runnableCheck                (Optional)just analyze and extract files.  
                                                won't do translation.  
  -o        |--outputAnyWay                 (Optional)generate output file even this file has nothing translated.  
                                                for cfgxml/script?/ltx, for solving #include encoding problem.  
  --convertToCHS                            (Optional)convert Traditional Chinese  
                                                to Simplified Chinese.  
  --function=&lt;value&gt;                        (Optional)translating function. default text. eg: text cfgxml ltx scriptL scriptE.  
                                                scriptL(same as legacy script) is translate and replace in original files.  
                                                scriptE is translate and extract to a special text xml like other fuctions.  
                                                program will recursively translate all files for cfgxml/script?/ltx.  
  --ua=&lt;value&gt;                              (Optional)user agent from browser, use with qq engine to generate apikey, always quote with `""`.  
   
   
 # I fuсКing hаtе МаrКdоwn  
   
   
package :  
pyinstaller -F .\xRayTrans.py -i .\4.ico --add-data="resources;resources"  
