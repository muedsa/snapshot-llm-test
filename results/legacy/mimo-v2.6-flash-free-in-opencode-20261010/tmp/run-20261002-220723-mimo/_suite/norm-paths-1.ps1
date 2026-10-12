# norm-paths-1.ps1 -- strip machine-specific roots out of self-authored records.
#
# Why: PATHS.md forbids hardcoding the machine drive letter / user name / repo location
# in configs, DSL, scripts, commands, reports and self-built logs. It requires the local
# paths inside 指标 / 状态 / 检查点 / 请求 / 迭代 / 工具日志 to be suite-root relative and
# to declare path_base = "suite_root".
#
# Scope discipline:
#   * only files that currently contain a machine root are touched (discovered by scan,
#     never by assumption)
#   * raw fetched bytes (downloaded *.html docs, service *.png / *.snapshot bodies) are
#     never rewritten -- PATHS.md keeps service/tool raw responses byte-identical
#   * the transform only removes the suite-root prefix, so every remaining byte is kept
#
# Encoding: BOM presence and strict UTF-8 validity are both honoured. A file that is not
# valid UTF-8 is skipped and reported instead of being silently re-encoded.
$ErrorActionPreference = 'Stop'

$scriptRoot = $PSScriptRoot
$suiteRoot = (Get-Item (Join-Path $scriptRoot '..\..\..')).FullName
$runId = 'run-20261002-220723-mimo'
$outRoot = Join-Path $suiteRoot "outputs\$runId"
$tmpRoot = Join-Path $suiteRoot "tmp\$runId"

# suite root in all separator / JSON-escape spellings, always followed by a separator
$rxSuite = [regex]'D:[\\/]{1,2}workspaces[\\/]{1,2}opencode-with-mimo-v2\.6-flash-free[\\/]{1,2}'
# user profile in all spellings; the following separator is left in place so the
# replacement stays an unexpanded $env:USERPROFILE expression in either escaping
$rxUser = [regex]'C:[\\/]{1,2}Users[\\/]{1,2}mueds'

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
  # strict UTF-8 decoder: throws on invalid bytes so a legacy-encoded file is left alone
  $enc = [System.Text.UTF8Encoding]::new($false, $true)
  try {
    return $enc.GetString($bytes, $offset, $bytes.Length - $offset)
  } catch {
    return $null            # not valid UTF-8: raw/legacy encoding, do not touch
  }
}

$report = New-Object System.Text.StringBuilder
[void]$report.AppendLine('{')
[void]$report.AppendLine('  "path_base": "suite_root",')
[void]$report.AppendLine(('  "run_id": "{0}",' -f $runId))
[void]$report.AppendLine('  "transform": [')
[void]$report.AppendLine('    "D:<sep>workspaces<sep>opencode-with-mimo-v2.6-flash-free<sep>  ->  (removed)",')
[void]$report.AppendLine('    "C:<sep>Users<sep>mueds                              ->  $env:USERPROFILE"')
[void]$report.AppendLine('  ],')
[void]$report.AppendLine('  "files": [')

$first = $true
$scanned = 0
$changed = 0
$skipped = @()
$hitTotal = 0

foreach ($scope in @($outRoot, $tmpRoot)) {
  foreach ($f in @(Get-ChildItem $scope -Recurse -File -Include '*.json', '*.jsonl', '*.md' -ErrorAction SilentlyContinue)) {
    $scanned++
    $hadBom = $false
    $text = Read-Preserved $f.FullName ([ref]$hadBom)
    if ($null -eq $text) { $skipped += ($f.FullName.Substring($suiteRoot.Length + 1) + ' (not valid UTF-8)'); continue }

    $nSuite = $rxSuite.Matches($text).Count
    $nUser = $rxUser.Matches($text).Count
    if ($nSuite -eq 0 -and $nUser -eq 0) { continue }

    $new = $rxSuite.Replace($text, '')
    $new = $rxUser.Replace($new, '$env:USERPROFILE')

    $rel = $f.FullName.Substring($suiteRoot.Length + 1)
    if (-not $first) { [void]$report.AppendLine(',') }
    $first = $false
    [void]$report.AppendLine(('    {{"path": "{0}", "suite_prefix_removed": {1}, "user_prefix_rewritten": {2}, "bom_kept": {3}}}' -f ($rel -replace '\\', '/'), $nSuite, $nUser, ($hadBom.ToString().ToLower())))

    if ($hadBom) { [IO.File]::WriteAllText($f.FullName, $new, $utf8Bom) }
    else { [IO.File]::WriteAllText($f.FullName, $new, $utf8NoBom) }
    $changed++
    $hitTotal += ($nSuite + $nUser)
  }
}

[void]$report.AppendLine('')
[void]$report.AppendLine('  ],')
[void]$report.AppendLine(('  "scanned_files": {0},' -f $scanned))
[void]$report.AppendLine(('  "changed_files": {0},' -f $changed))
[void]$report.AppendLine(('  "prefixes_removed": {0},' -f $hitTotal))
[void]$report.AppendLine(('  "skipped_files": {0},' -f $skipped.Count))
[void]$report.AppendLine('  "skipped_detail": [')
$s2 = $true
foreach ($s in $skipped) { if (-not $s2) { [void]$report.AppendLine(',') } ; $s2 = $false; [void]$report.AppendLine(('    "{0}"' -f $s)) }
[void]$report.AppendLine('')
[void]$report.AppendLine('  ]')
[void]$report.AppendLine('}')

$reportPath = Join-Path $scriptRoot 'path-normalization.json'
[IO.File]::WriteAllText($reportPath, $report.ToString(), $utf8NoBom)

"scanned      : $scanned"
"changed      : $changed"
"prefixes out : $hitTotal"
"skipped      : $($skipped.Count)"
$skipped | ForEach-Object { "  - $_" }
"report       : tmp/$runId/_suite/path-normalization.json"
