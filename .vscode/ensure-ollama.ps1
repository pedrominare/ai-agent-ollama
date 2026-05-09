# BEGIN: Garantir Ollama ativo para preLaunchTask do VS Code/Cursor
$uri = 'http://127.0.0.1:11434/'
function Test-OllamaUp {
    try {
        Invoke-WebRequest -Uri $uri -UseBasicParsing -TimeoutSec 2 | Out-Null
        return $true
    }
    catch {
        return $false
    }
}
if (Test-OllamaUp) {
    exit 0
}
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Error "Comando 'ollama' nao encontrado no PATH. Instale: https://ollama.com/download"
    exit 1
}
Start-Process -FilePath 'ollama' -ArgumentList 'serve' -WindowStyle Hidden
$deadline = (Get-Date).AddSeconds(60)
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Milliseconds 500
    if (Test-OllamaUp) {
        exit 0
    }
}
Write-Error "Ollama nao respondeu em $uri apos 60s."
exit 1
# END: Garantir Ollama ativo
