# log-a21-doc.ps1 - materialise the ai-guide that A21 actually read into this task's temp dir,
# with a real timed GET, and record the generator summary-printer defect fixed before any render.
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root
$tmp = "tmp\$RUN\A21"
$utf8 = New-Object System.Text.UTF8Encoding($false)
New-Item -ItemType Directory -Force -Path $tmp | Out-Null

$url = 'https://open-snapshot.muedsa.com/ai-guide.md'
$dst = "$tmp\doc-ai-guide.md"
$status = $null; $ctype = $null; $bytes = $null; $err = $null
$t0 = (Get-Date).ToUniversalTime()
try {
  $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 60
  $status = [int]$r.StatusCode
  $ctype  = [string]$r.Headers['Content-Type']
  $raw    = [Text.Encoding]::UTF8.GetBytes([string]$r.Content)
  $bytes  = $raw.Length
  [IO.File]::WriteAllBytes((Join-Path (Resolve-Path $tmp).Path 'doc-ai-guide.md'), $raw)
} catch {
  $err = $_.Exception.Message
}
$t1 = (Get-Date).ToUniversalTime()
$dur = [Math]::Round(($t1 - $t0).TotalMilliseconds, 1)

$doc = [ordered]@{
  id = 'A21-doc-001'; task = 'A21'; type = 'doc'
  started_utc = $t0.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
  ended_utc   = $t1.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
  tz = 'UTC'; duration_ms = $dur
  method = 'GET'; path = '/ai-guide.md'
  http_status = $status; content_type = $ctype; bytes = $bytes
  request_file = $null; response_file = $dst
  request_id = $null; server_timing = $null; ratelimit_remaining = $null
  error_summary = $err; attempt = 1
  note = 'A21 按本题 AGENTS「先实际阅读 ai-guide.md」在开工时通过取文工具读过一次该文档全文；因执行环境未暴露工具调用的起止时刻，本行记录的是随后为把该文档落到本任务临时目录而发起的同 URL 带计时 GET。所以 A21 的文档请求为 2 次（1 次带完整计时、1 次时刻不可得记 null），同一 URL，未重复计为新的不同文档。随后按总约定复用既有落盘结果：DSL 逐标签属性表（A17 tag-attrs.md）、DSL 指南摘录（A17 doc-excerpts.md）、字体清单（A11 fonts-0001.txt，27 个族含 Noto Sans CJK SC 与 Inter），这三项未再发新请求。'
}
[IO.File]::AppendAllText("$tmp\requests.jsonl", (([pscustomobject]$doc | ConvertTo-Json -Depth 6 -Compress) + "`n"), $utf8)

$now = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
$it = [ordered]@{
  id = 'A21r1-it02'; task = 'A21'; round = 1
  parent = 'A21r1-it01'
  type = 'syntax-fix'
  created_utc = $now; tz = 'UTC'
  image_paths = @()
  rendered_after = @()
  viewed_at_basis = '无看图（本行不是视觉迭代，是生成器的汇总打印缺陷）'
  viewed_with = $null
  observed = @(
    'gen-a21.ps1 第一次运行在全部产物写盘之后、汇总打印阶段抛出：Method invocation failed because [System.IO.File] does not contain a method named ''GetLength''。PowerShell 调静态成员应写 [IO.File]::GetLength(...)，而 .Length 是实例属性，方法名写错导致运行中断'
  )
  changes = @(
    '把汇总行的 [IO.File]::GetLength((Join-Path ...)) 换成 (Get-Item (Join-Path ...)).Length，只改打印语句，不触碰任何 DSL 生成逻辑'
  )
  rechecked = '第二次运行 0 problems，产出的 .snapshot 与第一次运行逐字节相同（生成器确定性、DSL 不含时间戳），对交付与渲染没有影响'
  result = '已修复'
  ordering_note = '本行按时间顺序发生在 A21r1-it01 之前，但为保持 iterations.jsonl 严格追加，只在末尾补记，不插入、不改写既有行；该缺陷发生在任何渲染之前，未影响交付的 DSL 或 PNG。'
  stats = [pscustomobject]@{ renders = 0; images = 0; problems_fixed = 1 }
}
[IO.File]::AppendAllText("$tmp\iterations.jsonl", (([pscustomobject]$it | ConvertTo-Json -Depth 8 -Compress) + "`n"), $utf8)

"GET $url  ->  $status  $bytes bytes  $dur ms  saved=$dst"
if ($err) { "  ERROR: $err" }
"requests.jsonl   + A21-doc-001"
"iterations.jsonl + A21r1-it02 (syntax-fix)"
