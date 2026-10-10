# fetch-search-b06.ps1 -- short-query Bing RSS searches (multi-term CN queries get
# truncated to the first token, so queries are kept to 1-2 terms).  curl writes raw
# bytes -> no encoding corruption.  Every request is logged to requests.jsonl.
$ErrorActionPreference = 'Continue'
$dir = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\B06')
$log = Join-Path $dir 'requests.jsonl'
$outDir = Join-Path $dir 'research'
$utf8 = New-Object System.Text.UTF8Encoding($false)
$ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

$queries = @(
  ,@('B06-res-26-pricetag',  '明码标价')
  ,@('B06-res-27-label',     '药品说明书')
  ,@('B06-res-28-checkup',   '体检报告')
  ,@('B06-res-29-apr',       '分期手续费')
  ,@('B06-res-30-deposit',   '押金退还')
  ,@('B06-res-31-precip',    '降水概率')
  ,@('B06-res-32-parcel',    '快递时限')
  ,@('B06-res-33-parking',   '停车计费')
  ,@('B06-res-34-metro',     '地铁末班车')
  ,@('B06-res-35-unitprice', '比价网站')
  ,@('B06-res-36-receipt',   '账单看不懂')
  ,@('B06-res-37-report',    '体检箭头')
)

foreach ($q in $queries) {
  $id = $q[0]; $term = $q[1]
  $enc = [uri]::EscapeDataString($term)
  $url = "https://www.bing.com/search?format=rss&q=$enc&setmkt=zh-CN"
  $out = Join-Path $outDir ($id + '.xml')
  $hdr = Join-Path $env:TEMP ("hdr-" + [Guid]::NewGuid().ToString('N') + '.txt')
  $t0 = Get-Date
  $code = curl.exe -sS -A $ua -L -D $hdr --max-time 40 -o $out -w '%{http_code}' $url
  $ms = [math]::Round(((Get-Date) - $t0).TotalMilliseconds, 1)
  $b = if (Test-Path $out) { (Get-Item $out).Length } else { 0 }
  $stHdr = $null
  if (Test-Path $hdr) { $stHdr = ((Get-Content $hdr) | Where-Object { $_ -match '^server-timing:' } | Select-Object -First 1) }
  Remove-Item $hdr -ErrorAction SilentlyContinue

  $entry = [ordered]@{
    id = $id; task = 'B06'; case_id = $null; type = 'research'
    started_utc = $null; started_at = $t0.ToString('yyyy-MM-ddTHH:mm:ss.fffzzz')
    ended_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss.fffzzz'); ended_utc = $null
    timezone = 'UTC+08:00'; tz_id = [TimeZoneInfo]::Local.Id
    duration_ms = $ms; method = 'GET'; url = $url
    http_status = $(if ($code) { [int]$code } else { $null })
    content_type = 'application/rss+xml'; bytes = $b
    request_file = $null; response_file = $out; request_id = $null
    server_timing = $stHdr; ratelimit_remaining = $null; error_summary = $null
    ua = 'Mozilla/5.0 Chrome/124.0'; query_term = $term
  }
  [IO.File]::AppendAllText($log, (($entry | ConvertTo-Json -Compress -Depth 4) + "`n"), $utf8)
  "{0}  '{1}' -> {2}  {3} ms  {4} B" -f $id, $term, $code, $ms, $b
}

# ---- summary of what was actually obtained ----
$files = Get-ChildItem $outDir -Filter 'B06-res-2*.xml' | Sort-Object Name
"---- parsed titles ----"
foreach ($f in (Get-ChildItem $outDir -Filter '*.xml' | Sort-Object Name)) {
  $raw = [IO.File]::ReadAllText($f.FullName, [Text.Encoding]::UTF8)
  $t = $raw
  if ($raw -match '[\u0080-\u009F]') { $t = [Text.Encoding]::UTF8.GetString([Text.Encoding]::GetEncoding(28591).GetBytes($raw)) }
  $its = [regex]::Matches($t, '<item>(.*?)</item>', 'Singleline')
  "=== $($f.BaseName)  items=$($its.Count)"
  $i = 0
  foreach ($m in $its) { $i++; if ($i -gt 4) { break }
    $ti = [regex]::Match($m.Value, '<title>(.*?)</title>', 'Singleline').Groups[1].Value
    $de = [regex]::Match($m.Value, '<description>(.*?)</description>', 'Singleline').Groups[1].Value -replace '<[^>]+>', ''
    "   * $ti"
    "     $de" }
}
