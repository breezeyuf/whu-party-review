param(
    [Parameter(Mandatory=$true)][string]$Exe,
    [Parameter(Mandatory=$true)][string]$DataDirectory,
    [Parameter(Mandatory=$true)][string]$Output
)
$ErrorActionPreference = 'Stop'
$exePath = (Resolve-Path -LiteralPath $Exe).Path
$qaPath = [IO.Path]::GetFullPath($DataDirectory)
if (Test-Path -LiteralPath $qaPath) { throw '验收目录必须全新，拒绝使用已有数据目录。' }
if ($exePath -match '[^\x00-\x7F]' -or $qaPath -match '[^\x00-\x7F]') { throw 'EXE 和验收数据目录须使用英文路径。' }
$checks = [Collections.Generic.List[object]]::new()
$qaProcess = $null
$failure = $null
function Check([string]$Name, [bool]$Passed) {
    $checks.Add([pscustomobject]@{name=$Name;passed=$Passed})
    if (-not $Passed) { throw $Name }
}
function Request-Api([string]$Method, [string]$Path, $Body=$null, $ExtraHeaders=@{}) {
    $headers = @{'X-Requested-With'='party-review';Origin=$script:qaUrl}
    foreach ($key in $ExtraHeaders.Keys) { $headers[$key]=$ExtraHeaders[$key] }
    $options = @{Uri=($script:qaUrl+'/api'+$Path);Method=$Method;WebSession=$script:qaSession;
        Headers=$headers;UseBasicParsing=$true;TimeoutSec=90}
    if ($null -ne $Body) { $options.ContentType='application/json'; $options.Body=($Body | ConvertTo-Json -Depth 8) }
    Invoke-WebRequest @options
}
try {
    $qaProcess = Start-Process -FilePath $exePath -ArgumentList @('--headless','--data-dir',('"'+$qaPath+'"')) -WindowStyle Hidden -PassThru
    $deadline = (Get-Date).AddSeconds(120)
    while ((Get-Date) -lt $deadline) {
        if ($qaProcess.HasExited) { throw '验收程序提前退出，请检查独立验收目录的 desktop.log。' }
        $configPath = Join-Path $qaPath 'config.json'
        if (Test-Path -LiteralPath $configPath) {
            $qaConfig = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
            $script:qaUrl = 'http://127.0.0.1:'+$qaConfig.http_port
            try {
                $health = Invoke-WebRequest -Uri ($script:qaUrl+'/api/health') -UseBasicParsing -TimeoutSec 2
                if (($health.Content | ConvertFrom-Json).data.db -eq 'ok') { break }
            } catch { }
        }
        Start-Sleep -Milliseconds 500
    }
    Check '全新目录启动并连接内置数据库' (($null -ne $health) -and (($health.Content | ConvertFrom-Json).data.db -eq 'ok'))
    $script:qaSession = New-Object Microsoft.PowerShell.Commands.WebRequestSession
    $login = Request-Api 'POST' '/auth/login' @{username='admin';password=$qaConfig.admin_password}
    $data = ($login.Content | ConvertFrom-Json).data
    Check '登录设置 HttpOnly Cookie' (($login.Headers['Set-Cookie'] -join ';') -match 'HttpOnly')
    Check '响应不返回访问或刷新令牌' (($null -eq $data.access_token) -and ($null -eq $data.refresh_token))
    $qaPassword = 'Qa9'+[guid]::NewGuid().ToString('N')+'!'
    $null = Request-Api 'PUT' '/auth/password' @{old_password=$qaConfig.admin_password;new_password=$qaPassword}
    try { $null = Request-Api 'GET' '/auth/me'; Check '改密后旧会话失效' $false }
    catch { Check '改密后旧会话失效' ([int]$_.Exception.Response.StatusCode -eq 401) }
    $null = Request-Api 'POST' '/auth/login' @{username='admin';password=$qaPassword}
    $me = (Request-Api 'GET' '/auth/me').Content | ConvertFrom-Json
    Check 'Cookie 会话可访问受保护接口' ($me.data.username -eq 'admin')
    try { $null = Request-Api 'POST' '/auth/logout' @{} @{Origin='https://untrusted.invalid'}; Check '拒绝跨站退出' $false }
    catch { Check '拒绝跨站退出' ([int]$_.Exception.Response.StatusCode -eq 403) }
    $ocr = (Request-Api 'POST' '/settings/ai/test' @{target='ocr';override=@{engine='rapidocr'}}).Content | ConvertFrom-Json
    Check '打包后的真实 RapidOCR 中文日期自检' ([bool]$ocr.data.ok)
    try { $null = Request-Api 'PUT' '/settings' @{ai=@{base_url='https://8.8.8.8/v1';api_key='synthetic'}}; Check '拒绝公网模型设置' $false }
    catch { Check '拒绝公网模型设置' ([int]$_.Exception.Response.StatusCode -eq 422) }
    $null = Request-Api 'POST' '/auth/logout' @{}
    try { $null = Request-Api 'GET' '/auth/me'; Check '退出后会话失效' $false }
    catch { Check '退出后会话失效' ([int]$_.Exception.Response.StatusCode -eq 401) }
} catch { $failure='验收未通过，请核对 checks 和独立验收目录中的日志。' }
finally {
    if ($null -ne $qaProcess -and -not $qaProcess.HasExited) {
        if (Test-Path -LiteralPath $qaPath) { New-Item -ItemType File -Path (Join-Path $qaPath 'stop.request') -Force | Out-Null }
        if (-not $qaProcess.WaitForExit(30000)) { Stop-Process -Id $qaProcess.Id -Force }
    }
    $result = [pscustomobject]@{checks=$checks;passed=@($checks | Where-Object passed).Count;
        failed=@($checks | Where-Object {-not $_.passed}).Count;error=$failure;
        exe_sha256=(Get-FileHash -LiteralPath $exePath -Algorithm SHA256).Hash}
    $result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $Output -Encoding UTF8
    $result | Select-Object passed,failed,error | ConvertTo-Json
}
if ($failure) { exit 1 }
