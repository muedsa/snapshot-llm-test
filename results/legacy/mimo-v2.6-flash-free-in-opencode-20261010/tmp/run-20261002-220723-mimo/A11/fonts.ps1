$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root
$TMP  = "$root\tmp\$RUN\A11"
$utf8 = New-Object System.Text.UTF8Encoding($false)

$hdr = Join-Path $env:TEMP ("a11fonts-" + [Guid]::NewGuid().ToString('N') + '.txt')
$out = "$TMP\fonts-0001.txt"
$url = 'https://open-snapshot.muedsa.com/fonts'
$t0 = Get-Date
$utc0 = (Get-Date).ToUniversalTime()
$code = curl.exe -sS -D $hdr -o $out -w '%{http_code}' $url
$ms = [math]::Round(((Get-Date) - $t0).TotalMilliseconds, 1)
$utc1 = (Get-Date).ToUniversalTime()

$h = @{}
Get-Content $hdr | ForEach-Object { if ($_ -match '^([^:]+):\s*(.*)$') { $h[$matches[1].ToLower()] = $matches[2] } }
Remove-Item $hdr -ErrorAction SilentlyContinue

$fams = @(Get-Content $out -Encoding UTF8 | Where-Object { $_.Trim() -ne '' })
$entry = [ordered]@{
  id = 'A11-fonts-0001'; task = 'A11'; type = 'fonts'
  started_utc = $utc0.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
  ended_utc   = $utc1.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
  tz = 'UTC'; duration_ms = $ms
  method = 'GET'; path = '/fonts'
  http_status = [int]$code
  content_type = $(if ($h.ContainsKey('content-type')) { $h['content-type'] } else { $null })
  bytes = (Get-Item $out).Length
  request_file = $null; response_file = $out
  request_id = $(if ($h.ContainsKey('x-request-id')) { $h['x-request-id'] } else { $null })
  server_timing = $(if ($h.ContainsKey('server-timing')) { $h['server-timing'] } else { $null })
  ratelimit_remaining = $(if ($h.ContainsKey('x-ratelimit-remaining')) { $h['x-ratelimit-remaining'] } else { $null })
  error_summary = $null; attempt = 1
}
[IO.File]::AppendAllText("$TMP\requests.jsonl", (($entry | ConvertTo-Json -Compress -Depth 6) + "`n"), $utf8)
"status=$code bytes=" + (Get-Item $out).Length + " duration=$ms ms families=$($fams.Count)"
$fams -join ', '
