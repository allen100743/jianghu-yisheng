Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class PowerUtil {
    [DllImport("kernel32.dll")]
    public static extern uint SetThreadExecutionState(uint esFlags);
}
"@

# ES_SYSTEM_REQUIRED = 0x1 (prevent sleep once, resets idle timer)
[PowerUtil]::SetThreadExecutionState([uint32]1) | Out-Null

$timestamp = Get-Date -Format "HH:mm:ss"
$logPath = Join-Path $PSScriptRoot "qingxia_log.md"
Add-Content -Path $logPath -Value "[$timestamp] [keep-awake] ok" -Encoding UTF8
