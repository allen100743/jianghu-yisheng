Dim oShell
Set oShell = CreateObject("WScript.Shell")
oShell.CurrentDirectory = "C:\Users\Allen\Desktop\ClaudeWorkRoom\AgentVRM"
oShell.Run "powershell.exe -NonInteractive -WindowStyle Hidden -Command ""Start-Process '" & Chr(34) & "C:\Program Files\nodejs\npm.cmd" & Chr(34) & "' -ArgumentList 'run dev' -WorkingDirectory '" & Chr(34) & "C:\Users\Allen\Desktop\ClaudeWorkRoom\AgentVRM" & Chr(34) & "' -NoNewWindow""", 0, False
Set oShell = Nothing
