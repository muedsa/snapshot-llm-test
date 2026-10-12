# Shared Snapshot render helper for run 20261003-114508-flashmax
# Usage:
#   . render.ps1
#   Invoke-Snapshot -Task A01 -DslPath <path> -OutPath <path> -Label "operations-v1" [-Round round-01] [-Case case-01]
# Appends one JSON line per HTTP request to tmp/<run>[_suite or task]/requests.jsonl via -LogPath.
param()

$script:RunId = '20261003-114508-flashmax'
$script:BaseUrl = 'https://open-snapshot.muedsa.com'
$script:SharedDir = Join-Path (Split-Path -Parent $PSScriptRoot) '_suite\shared'
if (-not (Test-Path -LiteralPath $script:SharedDir)) { $script:SharedDir = $PSScriptRoot }
$script:ReqSeq = [System.Collections.Generic.Dictionary[string,int]]::new()

function _SeedFromLog([string]$LogPath, [string]$prefix) {
  # request ids must never repeat inside one requests.jsonl, even when the helper
  # is dot-sourced into a fresh pwsh process for every call. A per-prefix sequence
  # file is authoritative; the log is also scanned so a lost sequence file cannot
  # silently restart numbering at 1.
  if ($script:ReqSeq.ContainsKey($prefix)) { return }
  $max = 0
  $seqFile = Join-Path $script:SharedDir "reqseq-$prefix.txt"
  if (Test-Path -LiteralPath $seqFile) {
    $txt = (Get-Content -LiteralPath $seqFile -Raw).Trim()
    if ($txt -match '^\d+$') { $max = [int]$txt }
  }
  if (Test-Path -LiteralPath $LogPath) {
    foreach ($line in [System.IO.File]::ReadAllLines($LogPath)) {
      foreach ($m in [regex]::Matches($line, '"request_id":"([A-Za-z0-9_\-]+?)-(\d+)"')) {
        if ($m.Groups[1].Value -eq $prefix) {
          $n = [int]$m.Groups[2].Value
          if ($n -gt $max) { $max = $n }
        }
      }
    }
  }
  $script:ReqSeq[$prefix] = $max
}

function _NextReqId([string]$prefix) {
  if (-not $script:ReqSeq.ContainsKey($prefix)) { $script:ReqSeq[$prefix] = 0 }
  $script:ReqSeq[$prefix]++
  $n = $script:ReqSeq[$prefix]
  $seqFile = Join-Path $script:SharedDir "reqseq-$prefix.txt"
  if (-not (Test-Path -LiteralPath $script:SharedDir)) { New-Item -ItemType Directory -Force -Path $script:SharedDir | Out-Null }
  [System.IO.File]::WriteAllText($seqFile, "$n")
  return ("{0}-{1:d4}" -f $prefix, $n)
}

function Invoke-Snapshot {
  param(
    [Parameter(Mandatory)][string]$DslPath,
    [Parameter(Mandatory)][string]$OutPath,
    [Parameter(Mandatory)][string]$LogPath,
    [string]$ReqPrefix = 'REQ',
    [string]$Task = '',
    [string]$Round = '',
    [string]$Case = '',
    [string]$Phase = 'render',
    [int]$TimeoutSec = 180,
    [string]$Query = ''
  )
  $dslFull = (Resolve-Path -LiteralPath $DslPath).Path
  $bytes = [System.IO.File]::ReadAllBytes($dslFull)
  _SeedFromLog $LogPath $ReqPrefix
  $url = "$script:BaseUrl/snapshot"
  if ($Query) { $url = "$url?$Query" }
  $reqId = _NextReqId $ReqPrefix
  $t0 = [DateTimeOffset]::Now
  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  $status = $null; $ctype = $null; $respReqId = $null; $serverTiming = $null; $err = $null; $ok = $false
  $respBytes = $null
  # curl.exe is used because Invoke-WebRequest discards the JSON error body that the
  # guide asks us to read; headers are dumped so X-Request-Id / Server-Timing survive.
  $dir2 = Split-Path -Parent $OutPath
  if ($dir2 -and -not (Test-Path $dir2)) { New-Item -ItemType Directory -Force -Path $dir2 | Out-Null }
  $bodyPath = "$OutPath.rawbody"
  $hdrPath = "$OutPath.rawheaders"
  $metaPath = "$OutPath.rawmeta"
  & curl.exe -sS -X POST $url -H 'Content-Type: text/plain; charset=utf-8' `
      --data-binary "@$dslFull" -D $hdrPath `
      -w '%{http_code}|%{content_type}|%{size_download}|%{time_total}' -o $bodyPath > $metaPath 2>"$metaPath.err"
  if (Test-Path -LiteralPath $bodyPath) { $respBytes = [System.IO.File]::ReadAllBytes($bodyPath) }
  if (Test-Path -LiteralPath $metaPath) {
    $meta = (Get-Content -LiteralPath $metaPath -Raw).Trim()
    $parts = $meta -split '\|'
    if ($parts.Count -ge 4) {
      if ($parts[0] -match '^\d+$') { $status = [int]$parts[0] }
      $ctype = $parts[1]
    }
  }
  if (Test-Path -LiteralPath $hdrPath) {
    foreach ($h in [System.IO.File]::ReadAllLines($hdrPath)) {
      if ($h -match '^(?i)x-request-id:\s*(.+)$') { $respReqId = $Matches[1].Trim() }
      if ($h -match '^(?i)server-timing:\s*(.+)$') { $serverTiming = $Matches[1].Trim() }
    }
  }
  $ok = ($status -eq 200) -and ($respBytes -and $respBytes.Length -gt 0) -and ($ctype -match 'image/')
  if (-not $ok) {
    if ($respBytes -and $respBytes.Length -gt 0) { $err = [System.Text.Encoding]::UTF8.GetString($respBytes) }
    elseif (Test-Path -LiteralPath "$metaPath.err") { $err = (Get-Content -LiteralPath "$metaPath.err" -Raw).Trim() }
    else { $err = "no response body" }
  }
  $sw.Stop()
  $t1 = [DateTimeOffset]::Now
  $outFull = $null
  if ($ok) {
    [System.IO.File]::WriteAllBytes($OutPath, $respBytes)
    $outFull = (Resolve-Path -LiteralPath $OutPath).Path
  } else {
    # keep the raw failure body beside the attempt, never as the final image
    Copy-Item -LiteralPath $bodyPath -Destination "$OutPath.failed.txt" -Force -ErrorAction SilentlyContinue
  }  $rec = [ordered]@{
    request_id      = $reqId
    run_id          = $script:RunId
    task_id         = $Task
    round           = if ($Round) { $Round } else { $null }
    case_id         = if ($Case) { $Case } else { $null }
    phase           = $Phase
    request_kind    = 'render'
    method          = 'POST'
    url             = '/snapshot'
    query           = if ($Query) { $Query } else { $null }
    started_at      = $t0.ToString('o')
    ended_at        = $t1.ToString('o')
    tz              = $t0.ToString('zzz')
    duration_ms     = [int]$sw.ElapsedMilliseconds
    http_status     = $status
    content_type    = $ctype
    request_file    = $dslFull
    request_bytes   = $bytes.Length
    response_file   = $outFull
    response_bytes  = if ($respBytes) { $respBytes.Length } else { 0 }
    service_request_id = $respReqId
    server_timing   = $serverTiming
    success         = $ok
    error           = $err
  }
  $json = ($rec | ConvertTo-Json -Compress -Depth 5)
  $logDir = Split-Path -Parent $LogPath
  if ($logDir -and -not (Test-Path $logDir)) { New-Item -ItemType Directory -Force -Path $logDir | Out-Null }
  Add-Content -LiteralPath $LogPath -Value $json -Encoding utf8
  if (-not $ok) { Write-Warning "[$reqId] render failed status=$status err=$err" }
  return [pscustomobject]@{ Success = $ok; Status = $status; Out = $outFull; RequestId = $reqId; ServiceRequestId = $respReqId; DurationMs = [int]$sw.ElapsedMilliseconds; Error = $err; Bytes = if ($respBytes) { $respBytes.Length } else { 0 } }
}

function Invoke-SnapshotRetry {
  <#
    Render with bounded retry for TRANSIENT failures only.

    Seven workstreams can hit the service at the same time, so a 429 (rate limit) or a
    5xx is a real possibility. This wrapper honours Retry-After when the service sends it
    and otherwise backs off exponentially with a fixed per-attempt jitter derived from the
    task prefix, so parallel callers do not retry in lockstep.

    A 400 is NOT retried: the DSL itself is wrong, and retrying would just burn requests.
    Every attempt is still logged separately by Invoke-Snapshot (the standard requires that
    a retry of the same DSL counts as a new request), and the returned object is the LAST
    attempt so callers can report the final state.
  #>
  param(
    [Parameter(Mandatory)][string]$DslPath,
    [Parameter(Mandatory)][string]$OutPath,
    [Parameter(Mandatory)][string]$LogPath,
    [string]$ReqPrefix = 'REQ',
    [string]$Task = '', [string]$Round = '', [string]$Case = '',
    [string]$Phase = 'render', [int]$TimeoutSec = 180, [string]$Query = '',
    [int]$MaxAttempts = 4
  )
  $jitter = 0
  foreach ($ch in $ReqPrefix.ToCharArray()) { $jitter = ($jitter * 31 + [int]$ch) % 400 }
  $result = $null
  for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
    $result = Invoke-Snapshot -DslPath $DslPath -OutPath $OutPath -LogPath $LogPath `
      -ReqPrefix $ReqPrefix -Task $Task -Round $Round -Case $Case -Phase $Phase `
      -TimeoutSec $TimeoutSec -Query $Query
    if ($result.Success) { return $result }
    $transient = ($result.Status -eq 429) -or ($result.Status -ge 500) -or ($null -eq $result.Status)
    if (-not $transient -or $attempt -eq $MaxAttempts) { return $result }
    $waitMs = [int]([Math]::Pow(2, $attempt) * 700) + $jitter
    $retryAfter = $null
    if (Test-Path -LiteralPath "$OutPath.rawheaders") {
      foreach ($h in [System.IO.File]::ReadAllLines("$OutPath.rawheaders")) {
        if ($h -match '^(?i)retry-after:\s*(\d+)\s*$') { $retryAfter = [int]$Matches[1] }
      }
    }
    if ($retryAfter) { $waitMs = [Math]::Max($waitMs, $retryAfter * 1000) }
    Write-Warning "[$($result.RequestId)] transient status=$($result.Status); retry $attempt/$MaxAttempts in ${waitMs}ms"
    Start-Sleep -Milliseconds $waitMs
  }
  return $result
}

function Invoke-SnapshotText {
  param(
    [Parameter(Mandatory)][string]$Text,
    [Parameter(Mandatory)][string]$OutPath,
    [Parameter(Mandatory)][string]$LogPath,
    [string]$ReqPrefix = 'REQ',
    [string]$Task = '', [string]$Round = '', [string]$Case = '', [string]$Phase = 'render',
    [int]$TimeoutSec = 180, [string]$Query = ''
  )
  $tmpDsl = "$OutPath.dsl"
  $dir = Split-Path -Parent $tmpDsl
  if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  [System.IO.File]::WriteAllText($tmpDsl, $Text, (New-Object System.Text.UTF8Encoding($false)))
  return Invoke-Snapshot -DslPath $tmpDsl -OutPath $OutPath -LogPath $LogPath -ReqPrefix $ReqPrefix -Task $Task -Round $Round -Case $Case -Phase $Phase -TimeoutSec $TimeoutSec -Query $Query
}

function Get-SnapshotFonts {
  param([Parameter(Mandatory)][string]$OutPath, [Parameter(Mandatory)][string]$LogPath, [string]$ReqPrefix='REQ', [string]$Task='_suite')
  $url = "$script:BaseUrl/fonts"
  $t0 = [DateTimeOffset]::Now
  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  $status=$null;$ctype=$null;$respReqId=$null;$err=$null;$ok=$false;$body=$null
  try {
    $resp = Invoke-WebRequest -Uri $url -Method Get -TimeoutSec 60 -UseBasicParsing -ErrorAction Stop
    $status=[int]$resp.StatusCode; $ctype=$resp.Headers['Content-Type']; $respReqId=$resp.Headers['X-Request-Id']
    $body = $resp.Content; $ok=$true
  } catch { $err=$_.Exception.Message; if ($_.Exception.Response) { $status=[int]$_.Exception.Response.StatusCode } }
  $sw.Stop(); $t1=[DateTimeOffset]::Now
  if ($ok) {
    $dir = Split-Path -Parent $OutPath; if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    [System.IO.File]::WriteAllText($OutPath, $body, (New-Object System.Text.UTF8Encoding($false)))
  }
  $rec = [ordered]@{ request_id=(_NextReqId $ReqPrefix); run_id=$script:RunId; task_id=$Task; round=$null; case_id=$null
    phase='fonts'; request_kind='fonts'; method='GET'; url='/fonts'; query=$null
    started_at=$t0.ToString('o'); ended_at=$t1.ToString('o'); tz=$t0.ToString('zzz'); duration_ms=[int]$sw.ElapsedMilliseconds
    http_status=$status; content_type=$ctype; request_file=$null; request_bytes=0
    response_file= if ($ok) { (Resolve-Path -LiteralPath $OutPath).Path } else { $null }
    response_bytes= if ($body) { $body.Length } else { 0 }
    service_request_id=$respReqId; server_timing=$null; success=$ok; error=$err }
  Add-Content -LiteralPath $LogPath -Value ($rec | ConvertTo-Json -Compress -Depth 5) -Encoding utf8
  return [pscustomobject]@{ Success=$ok; Status=$status; Body=$body; Out=$OutPath }
}
