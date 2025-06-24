# PowerShell script to run Mihomo as administrator (especially for TUN mode)
Write-Host "Launching Mihomo as administrator..."
$command = "cd `"$PSScriptRoot`"; python start_visible.py"
Start-Process powershell -Verb RunAs -ArgumentList @('-NoExit', '-Command', $command)
