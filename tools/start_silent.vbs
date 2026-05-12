Dim oShell
Set oShell = CreateObject("WScript.Shell")

' VOICEVOX 語音引擎（怡嘉說話用）
oShell.CurrentDirectory = "D:\Downloads\windows-nvidia"
oShell.Run "run.exe --host 127.0.0.1 --port 50021", 0, False

' 等 VOICEVOX 初始化
WScript.Sleep 3000

' Watchdog 統一管理所有服務（Python + Node.js）
' pythonw = 無視窗版 Python
oShell.CurrentDirectory = "C:\Users\Allen\Desktop\ClaudeWorkRoom\wuxia-rpg"
oShell.Run "pythonw tools\watchdog.py", 0, False

Set oShell = Nothing
