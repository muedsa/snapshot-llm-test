# norm-paths-2.ps1 -- declare the path base next to every local path record.
#
# PATHS.md row "指标、状态、检查点、请求/迭代/工具日志中的本地路径 -> 默认总任务根，
# 记录 path_base: suite_root" and row "portfolio.json 的 PNG、DSL、素材和自检证据文件 ->
# 本题输出根，记录 path_base: output_dir".
#
# norm-paths-1.ps1 already removed the machine root so every local path is now relative;
# this pass attaches the declaration that says what those relative paths are relative to.
#
# Insertion is done on the raw text at the opening brace of each top-level JSON object, so
# no value is re-serialised: floats keep their exact digits, key order is untouched and the
# pretty-printed multi-record A05/A06 iteration streams keep their exact line structure.
$ErrorActionPreference = 'Stop'

$scriptRoot = $PSScriptRoot
$suiteRoot = (Get-Item (Join-Path $scriptRoot '..\..\..')).FullName
$runId = 'run-20261002-220723-mimo'
$outRoot = Join-Path $suiteRoot "outputs\$runId"
$tmpRoot = Join-Path $suiteRoot "tmp\$runId"

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$utf8Bom = [System.Text.UTF8Encoding]::new($true)

function Read-Preserved([string]$path, [ref]$hadBom) {
  $bytes = [IO.File]::ReadAllBytes($path)
  $hadBom.Value = $false
  $offset = 0
  if ($bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191) {
    $hadBom.Value = $true
    $offset = 3
  }
  $enc = [System.Text.UTF8Encoding]::new($false, $true)
  try { return $enc.GetString($bytes, $offset, $bytes.Length - $offset) } catch { return $null }
}

# offsets of the opening brace of every top-level JSON object in a text stream
function Get-TopLevelStarts([string]$text) {
  $starts = New-Object System.Collections.Generic.List[int]
  $depth = 0; $inStr = $false; $esc = $false
  for ($i = 0; $i -lt $text.Length; $i++) {
    $c = $text[$i]
    if ($inStr) {
      if ($esc) { $esc = $false }
      elseif ($c -eq '\') { $esc = $true }
      elseif ($c -eq '"') { $inStr = $false }
      continue
    }
    switch ($c) {
      '"' { $inStr = $true }
      '{' { if ($depth -eq 0) { $starts.Add($i) }; $depth++ }
      '}' { $depth-- }
    }
  }
  return $starts
}

$stats = @{ json = 0; jsonlFiles = 0; jsonlRecords = 0; skippedNoPath = 0; skippedExisting = 0; failed = @() }

function Insert-Field([string]$text, [string]$field) {
  $starts = Get-TopLevelStarts $text
  if ($starts.Count -eq 0) { return $null }
  $sb = New-Object System.Text.StringBuilder
  $prev = 0
  foreach ($s in $starts) {
    [void]$sb.Append($text.Substring($prev, ($s + 1) - $prev))
    [void]$sb.Append($field)
    $prev = $s + 1
  }
  [void]$sb.Append($text.Substring($prev))
  return $sb.ToString()
}

function Write-Preserved([string]$path, [string]$text, [bool]$hadBom) {
  if ($hadBom) { [IO.File]::WriteAllText($path, $text, $utf8Bom) }
  else { [IO.File]::WriteAllText($path, $text, $utf8NoBom) }
}

# ---- JSONL logs: requests.jsonl / iterations.jsonl / tool-usage.jsonl ----
foreach ($scope in @($outRoot, $tmpRoot)) {
  foreach ($f in @(Get-ChildItem $scope -Recurse -Filter '*.jsonl' -File)) {
    $hadBom = $false
    $text = Read-Preserved $f.FullName ([ref]$hadBom)
    if ($null -eq $text) { $stats.failed += ($f.FullName.Substring($suiteRoot.Length + 1) + ' (encoding)'); continue }
    if ($text.Contains('"path_base"')) { $stats.skippedExisting++; continue }
    # only logs that actually hold local paths need the declaration
    if ($text -notmatch '(?<=")(outputs|tmp)[\\/]') { $stats.skippedNoPath++; continue }

    $new = Insert-Field $text '"path_base":"suite_root",'
    if ($null -eq $new) { $stats.failed += ($f.FullName.Substring($suiteRoot.Length + 1) + ' (no object)'); continue }
    Write-Preserved $f.FullName $new $hadBom
    $stats.jsonlFiles++
    $stats.jsonlRecords += (Get-TopLevelStarts $text).Count
  }
}

# ---- JSON records: metrics / state / checkpoints / audits ----
foreach ($scope in @($outRoot, $tmpRoot)) {
  foreach ($f in @(Get-ChildItem $scope -Recurse -Filter '*.json' -File)) {
    if ($f.Name -eq 'portfolio.json') { continue }        # different base: output_dir
    $hadBom = $false
    $text = Read-Preserved $f.FullName ([ref]$hadBom)
    if ($null -eq $text) { continue }                      # raw cache with foreign encoding
    if ($text.Contains('"path_base"')) { $stats.skippedExisting++; continue }
    if ($text -notmatch '(?<=")(outputs|tmp)[\\/]') { $stats.skippedNoPath++; continue }
    if (-not ($text.TrimStart().StartsWith('{'))) { continue }

    # pretty-printed document -> add a new member line using the file's own indentation;
    # compact document (or a one-line object with a trailing newline) -> inline field
    $m = [regex]::Match($text, '\{\r?\n(\s+)"')
    if ($m.Success) {
      $nl = if ($text.Contains("`r`n")) { "`r`n" } else { "`n" }
      # insert BEFORE the original leading whitespace of the first member, so the file
      # keeps exactly its original line count and indentation
      $field = ($nl + $m.Groups[1].Value + '"path_base": "suite_root",')
    } else {
      $field = '"path_base":"suite_root",'
    }
    $new = Insert-Field $text $field
    if ($null -eq $new) { $stats.failed += ($f.FullName.Substring($suiteRoot.Length + 1) + ' (no object)'); continue }
    Write-Preserved $f.FullName $new $hadBom
    $stats.json++
  }
}

"json records annotated : $($stats.json)"
"jsonl files annotated   : $($stats.jsonlFiles)  (records: $($stats.jsonlRecords))"
"skipped (already set)   : $($stats.skippedExisting)"
"skipped (no local path) : $($stats.skippedNoPath)"
"failed                  : $($stats.failed.Count)"
$stats.failed | ForEach-Object { "  - $_" }
