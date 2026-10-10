# A17 - fetch the documentation this task actually relies on, retain the bytes,
# and log every request to requests.jsonl with measurable status/bytes/duration.
$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$TMP = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A17'
$utf8 = New-Object System.Text.UTF8Encoding($false)
$LOG = Join-Path $TMP 'requests.jsonl'
if (!(Test-Path $TMP)) { New-Item -ItemType Directory -Force -Path $TMP | Out-Null }

$docs = @(
  [pscustomobject]@{ id = 'A17-doc-01-ai-guide';     url = 'https://open-snapshot.muedsa.com/ai-guide.md';             out = 'doc-ai-guide.md';       rely = 'P1: POST /snapshot contract, UTF-8 plain-text body (not JSON), Content-Type text/plain; charset=utf-8, PNG binary response, error JSON shape (code/message/requestId), GET /fonts, 429/Retry-After, do not invent tag/attribute names' },
  [pscustomobject]@{ id = 'A17-doc-02-rendering';     url = 'https://snapshot.muedsa.com/guides/rendering/';            out = 'doc-rendering.html';    rely = 'P1: render entry and output - how the widget tree becomes an encoded file and how output type follows the root type attribute' },
  [pscustomobject]@{ id = 'A17-doc-03-parser-errors'; url = 'https://snapshot.muedsa.com/reference/parser-errors/';     out = 'doc-parser-errors.html'; rely = 'P1/P3: error classes (ParseException / IllegalArgumentException / IllegalStateException), text and whitespace rules (Text trims, Raw keeps, & not decoded, CDATA for < >, comments, DOCTYPE unsupported), ParseException carries Pos[line:col]~offset' },
  [pscustomobject]@{ id = 'A17-doc-04-layout';        url = 'https://snapshot.muedsa.com/guides/layout/';               out = 'doc-layout.html';       rely = 'P2: BoxConstraints protocol, Container composition order, Expanded = Flexible(fit=TIGHT) must be a direct Flex child, Flex needs a finite main axis before Expanded works, Stack lays out non-Positioned then Positioned, at most two of left/right/width per axis' },
  [pscustomobject]@{ id = 'A17-doc-05-parser';        url = 'https://snapshot.muedsa.com/guides/parser/';               out = 'doc-parser.html';       rely = 'P3: parser overview, Text vs Raw whitespace, CDATA, comments, case sensitivity, Snapshot root, registered tag count' },
  [pscustomobject]@{ id = 'A17-doc-06-media-text';    url = 'https://snapshot.muedsa.com/guides/media-text/';           out = 'doc-media-text.html';   rely = 'P3: rich text (RichText / WidgetSpan / ImageEmojiSpan) and text constraints' },
  [pscustomobject]@{ id = 'A17-doc-07-painting';      url = 'https://snapshot.muedsa.com/guides/painting/';             out = 'doc-painting.html';     rely = 'P4: BackdropFilter = background filter (behind), ImageFiltered = subtree filter (result of subtree), ColorFiltered, clipping and when a filter shows no effect' },
  [pscustomobject]@{ id = 'A17-doc-08-testing';       url = 'https://snapshot.muedsa.com/guides/testing/';              out = 'doc-testing.html';      rely = 'P4: four-layer verification (layout -> pixel -> golden -> artifact), artifact is not an assertion, golden stability rules, common pitfalls' }
)

function Get-Url([string]$u) {
  $req = [Net.HttpWebRequest]::Create($u)
  $req.Method = 'GET'
  $req.Timeout = 30000
  $req.UserAgent = 'snapshot-suite-doc-fetch/1.0'
  $req.AutomaticDecompression = [Net.DecompressionMethods]::GZip -bor [Net.DecompressionMethods]::Deflate
  $resp = $req.GetResponse()
  $code = [int]$resp.StatusCode
  $ctype = $resp.Headers['Content-Type']
  $rid = $resp.Headers['X-Request-Id']
  $st = $resp.Headers['Server-Timing']
  $rl = $resp.Headers['X-RateLimit-Remaining']
  $sr = New-Object IO.StreamReader($resp.GetResponseStream(), [Text.Encoding]::UTF8)
  $body = $sr.ReadToEnd()
  $sr.Close(); $resp.Close()
  return [pscustomobject]@{ status = $code; ctype = $ctype; rid = $rid; st = $st; rl = $rl; body = $body }
}

foreach ($d in $docs) {
  $outPath = Join-Path $TMP $d.out
  $t0 = Get-Date
  $start = (Get-Date).ToUniversalTime()
  $entry = $null
  try {
    $r = Get-Url $d.url
    $end = (Get-Date).ToUniversalTime()
    $ms = [math]::Round(((Get-Date) - $t0).TotalMilliseconds, 1)
    [IO.File]::WriteAllText($outPath, $r.body, $utf8)
    $bytes = (Get-Item $outPath).Length
    $entry = [ordered]@{
      id = $d.id; task = 'A17'; type = 'document'
      started_utc = $start.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
      ended_utc = $end.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
      tz = 'UTC'; duration_ms = $ms
      method = 'GET'; path = $d.url
      http_status = $r.status; content_type = $r.ctype; bytes = $bytes
      request_file = $null; response_file = "tmp\run-20261002-220723-mimo\A17\$($d.out)"
      request_id = $r.rid; server_timing = $r.st; ratelimit_remaining = $r.rl
      error_summary = $null; attempt = 1
      note = "read for: $($d.rely) || this page was first read through the harness webfetch (that tool exposes no status/timing/bytes), then re-fetched here so the bytes are retained and the measured fields are real; one log row, disclosed here rather than double-counted"
    }
    Write-Output ("OK {0} {1} ms {2} bytes -> {3}" -f $r.status, $ms, $bytes, $d.out)
  } catch {
    $end = (Get-Date).ToUniversalTime()
    $ms = [math]::Round(((Get-Date) - $t0).TotalMilliseconds, 1)
    $emsg = $_.Exception.Message
    if ($_.Exception.Response) {
      try {
        $er = $_.Exception.Response.GetResponseStream()
        $esr = New-Object IO.StreamReader($er, [Text.Encoding]::UTF8)
        $ebody = $esr.ReadToEnd(); $esr.Close()
        [IO.File]::WriteAllText(($outPath + '.error'), $ebody, $utf8)
        $emsg = "$($emsg) || body: $($ebody.Substring(0, [Math]::Min(300, $ebody.Length)))"
      } catch { }
    }
    $entry = [ordered]@{
      id = $d.id; task = 'A17'; type = 'document'
      started_utc = $start.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
      ended_utc = $end.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
      tz = 'UTC'; duration_ms = $ms
      method = 'GET'; path = $d.url
      http_status = $null; content_type = $null; bytes = $null
      request_file = $null; response_file = $null
      request_id = $null; server_timing = $null; ratelimit_remaining = $null
      error_summary = $emsg; attempt = 1
      note = "document fetch failed; nothing was claimed as read from this URL"
    }
    Write-Output ("FAIL {0} {1}" -f $d.out, $emsg)
  }
  [IO.File]::AppendAllText($LOG, (($entry | ConvertTo-Json -Compress -Depth 6) + "`n"), $utf8)
}
Write-Output ("requests.jsonl rows now: " + (@(Get-Content $LOG | Where-Object { $_ -and $_.Trim() }).Count))
