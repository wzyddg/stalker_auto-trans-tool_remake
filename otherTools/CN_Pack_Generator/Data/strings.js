var args = WScript.Arguments;
if (args.Count()!=2)
{
    WScript.Echo("Missing parameters!");
    WScript.Quit(0);
}
var nLine = parseInt(args(1));
var fso = new ActiveXObject("Scripting.FileSystemObject");
var f = fso.OpenTextFile(args(0), 1);
var str;
while (!f.AtEndOfStream)
{
    str = f.ReadLine();
    if (--nLine == 0)
        break;
}
f.Close();
fso = null;
if (nLine == 0)
{
    WScript.Echo(unescape(str));
}
else
{
    WScript.Echo("Missing string!");
}