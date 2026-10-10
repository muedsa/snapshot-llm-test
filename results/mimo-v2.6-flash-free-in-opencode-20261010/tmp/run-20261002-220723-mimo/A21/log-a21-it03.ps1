# log-a21-it03.ps1 - two real defects hit while archiving round-01, both fixed before the round
# could be closed. Appends one syntax-fix iteration row (strictly append-only).
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root
$tmp = "tmp\$RUN\A21"
$utf8 = New-Object System.Text.UTF8Encoding($false)

$now = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
$it = [ordered]@{
  id = 'A21r1-it03'; task = 'A21'; round = 1
  parent = 'A21r1-it02'
  type = 'syntax-fix'
  created_utc = $now; tz = 'UTC'
  image_paths = @()
  rendered_after = @()
  viewed_at_basis = '无看图（本行是归档/进度脚本的语法缺陷，不产生图也不改 DSL）'
  viewed_with = $null
  observed = @(
    '缺陷 1：close-a21-round01.ps1 第一次运行解析失败，报 Unexpected token。最小复现证明根因是 PowerShell 把 U+201C/U+201D（“ ”）也当作字符串定界符——`$a = "plain 中文 “curly” end"` 这样一个双引号字符串会在 处被切断，而单引号字符串里的同样字符不受影响（gen-a21.ps1 / promote-a21-r01.ps1 里的 “ ” 都在单引号内，所以它们一直正常）。本执行环境没有可用的 PowerShell 7，powershell.exe 即 Windows PowerShell 5.1。',
    '缺陷 2：改完引号后仍报 Missing closing ''}''（函数 IhdrOf 的开括号 29:29）。用 [System.Management.Automation.Language.Parser]::ParseFile 一次取回全部错误，再数原始大括号得 28 开 / 27 闭——IhdrOf 函数体末尾少写了一个 }，$p = IhdrOf ... 被吞进了函数体。'
  )
  changes = @(
    '缺陷 1：把双引号字符串里的“”换成「」，并把该行改用单引号 + -f 格式化传 $base，保证不再出现任何会被 PowerShell 当定界符的字符',
    '缺陷 2：在闭合哈希表 } 之后补上函数自己的 }，大括号回到 28/28'
  )
  rechecked = '重新用 ParseFile 校验：parse errors = 0；随后脚本一次跑通，归档 8 个产物、写入 events seq 41 与 checkpoint state-000022.json（291309 字节）。两个缺陷都发生在任何 DSL 生成与渲染之前，未影响 round-01 的交付内容'
  result = '已修复'
  ordering_note = '本行按时间顺序发生在 A21r1-it01（baseline）之后、round-01 归档完成之前，是在归档动作本身被阻塞后补记的；为保持 iterations.jsonl 严格追加，不插入、不改写既有行。'
  stats = [pscustomobject]@{ renders = 0; images = 0; problems_fixed = 2; parse_errors = 0 }
}
[IO.File]::AppendAllText("$tmp\iterations.jsonl", (([pscustomobject]$it | ConvertTo-Json -Depth 8 -Compress) + "`n"), $utf8)

$i = 0; $bad = 0
Get-Content "$tmp\iterations.jsonl" -Encoding UTF8 | ForEach-Object { $i++; try { $null = $_ | ConvertFrom-Json } catch { $bad++ } }
"iterations.jsonl -> $i rows, $bad bad"
Get-Content "$tmp\iterations.jsonl" -Encoding UTF8 | ForEach-Object { $o = $_ | ConvertFrom-Json; "  {0}  type={1,-14} renders={2}" -f $o.id, $o.type, $o.stats.renders }
