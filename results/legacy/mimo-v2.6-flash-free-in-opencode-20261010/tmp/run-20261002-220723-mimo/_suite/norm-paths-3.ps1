# norm-paths-3.ps1 -- attach the two declarations that the suite spec asks for.
#
#   1. suite-state.json must record `suite_artifacts`, the paths actually delivered.
#      AGENTS.md: "在 suite-state.json 的 suite_artifacts 记录实际总交付路径".
#   2. portfolio.json stores PNG / DSL / self-check evidence relative to the task output
#      root, so PATHS.md wants it to declare `path_base: "output_dir"`.
#
# Both edits are made by slicing raw text at the closing brace of the root object. The
# files are pretty-printed by PowerShell's ConvertTo-Json, which leaves a mix of raw CJK
# and \uXXXX escapes; re-serialising them would rewrite every escape, so it is never done
# here. Byte sizes are read from disk, never typed.
$ErrorActionPreference = 'Stop'

$scriptRoot = $PSScriptRoot
$suiteRoot = (Get-Item (Join-Path $scriptRoot '..\..\..')).FullName
$runId = 'run-20261002-220723-mimo'
$suiteDir = Join-Path $suiteRoot "outputs\$runId\_suite"

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$utf8Bom = [System.Text.UTF8Encoding]::new($true)

function Read-Preserved([string]$path, [ref]$hadBom) {
  $bytes = [IO.File]::ReadAllBytes($path)
  $hadBom.Value = $false
  $offset = 0
  if ($bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191) {
    $hadBom.Value = $true; $offset = 3
  }
  $enc = [System.Text.UTF8Encoding]::new($false, $true)
  try { return $enc.GetString($bytes, $offset, $bytes.Length - $offset) } catch { return $null }
}

function Write-Preserved([string]$path, [string]$text, [bool]$hadBom) {
  if ($hadBom) { [IO.File]::WriteAllText($path, $text, $utf8Bom) }
  else { [IO.File]::WriteAllText($path, $text, $utf8NoBom) }
}

# index of the brace that closes the root object
function Get-RootClose([string]$text) {
  $depth = 0; $inStr = $false; $esc = $false; $opened = $false
  for ($i = 0; $i -lt $text.Length; $i++) {
    $c = $text[$i]
    if ($inStr) {
      if ($esc) { $esc = $false }
      elseif ($c -eq '\') { $esc = $true }
      elseif ($c -eq '"') { $inStr = $false }
      continue
    }
    if ($c -eq '"') { $inStr = $true }
    elseif ($c -eq '{') { $depth++; $opened = $true }
    elseif ($c -eq '}') {
      $depth--
      if ($opened -and $depth -eq 0) { return $i }
    }
  }
  return -1
}

# append one member to a pretty-printed root object, keeping its own indentation
function Add-RootMember([string]$text, [string]$member, [int]$indent) {
  $end = Get-RootClose $text
  if ($end -lt 0) { return $null }
  $nl = if ($text.Contains("`r`n")) { "`r`n" } else { "`n" }
  $pad = ' ' * $indent
  $head = $text.Substring(0, $end).TrimEnd([char[]]"`r`n")
  $tail = $text.Substring($end)
  return ($head + ',' + $nl + $pad + $member + $nl + $tail)
}

# ---- 1. suite_artifacts in suite-state.json ----
$ssPath = Join-Path $suiteDir 'suite-state.json'
$hadBom = $false
$ssText = Read-Preserved $ssPath ([ref]$hadBom)
if ($null -eq $ssText) { throw 'suite-state.json is not valid UTF-8' }

if ($ssText.Contains('"suite_artifacts"')) {
  'suite-state.json : suite_artifacts already present, unchanged'
} else {
  $required = @('index.md', 'gallery.md', 'snapshot-usage.md', 'task-metrics.json', 'suite-state.json')
  $entries = New-Object System.Collections.Generic.List[string]
  foreach ($name in $required + @('gallery.html')) {
    $p = Join-Path $suiteDir $name
    $exists = Test-Path -LiteralPath $p
    $bytes = if ($exists) { (Get-Item -LiteralPath $p).Length } else { $null }
    $rel = ("outputs/{0}/_suite/{1}" -f $runId, $name)
    $isReq = $required -contains $name
    $role = switch ($name) {
      'index.md'          { '总索引：30 题状态、产物、单题入口与实际路径' }
      'gallery.md'        { '总画廊：124 张最终图片逐图标题 + Markdown 预览 + 原 PNG 链接 + .snapshot 链接，全部相对本目录' }
      'snapshot-usage.md' { '全套实际文档/DSL/工具应用、跨题经验与踩坑、总审查与剩余事项' }
      'task-metrics.json' { '全套起止与总耗时、shared + 每题请求/迭代/读图/作品数、汇总范围与计时/日志来源' }
      'suite-state.json'  { '当前进度指针：逐题状态、启止、产物、视觉复核证据、未解决事项与恢复笔记' }
      default             { '附加的 HTML 浏览版画廊；不在 suite_required_artifacts 内，仅供肉眼快速翻看' }
    }
    $entry = ('{' + $nl +
              ('        "path": "{0}",' -f $rel) + $nl +
              ('        "path_base": "suite_root",' ) + $nl +
              ('        "role": "{0}",' -f ($role -replace '\\', '/' -replace '"', '\"')) + $nl +
              ('        "required_by_suite_config": {0},' -f $isReq.ToString().ToLower()) + $nl +
              ('        "bytes": {0},' -f $(if ($exists) { $bytes } else { 'null' })) + $nl +
              ('        "exists": {0}' -f $exists.ToString().ToLower()) + $nl +
              '      }')
    $entries.Add($entry)
  }
  $member = ('"suite_artifacts": [' + $nl + '      ' + ($entries -join (',' + $nl + '      ')) + $nl + '    ]')
  $new = Add-RootMember $ssText $member 4
  if ($null -eq $new) { throw 'could not locate the root object of suite-state.json' }
  Write-Preserved $ssPath $new $hadBom
  "suite-state.json : suite_artifacts added ($($entries.Count) entries)"
}

# ---- 2. path_base in each portfolio.json ----
foreach ($i in 1..6) {
  $task = ('B{0:d2}' -f $i)
  $pf = Join-Path $suiteRoot ("outputs\{0}\{1}\portfolio.json" -f $runId, $task)
  if (-not (Test-Path -LiteralPath $pf)) { "portfolio $task : NOT FOUND"; continue }
  $had = $false
  $txt = Read-Preserved $pf ([ref]$had)
  if ($null -eq $txt) { "portfolio $task : not valid UTF-8, skipped"; continue }
  if ($txt.Contains('"path_base"')) { "portfolio $task : path_base already present"; continue }
  $new = Add-RootMember $txt '"path_base": "output_dir"' 4
  if ($null -eq $new) { "portfolio $task : root object not found, SKIPPED"; continue }
  Write-Preserved $pf $new $had
  "portfolio $task : path_base = output_dir"
}
