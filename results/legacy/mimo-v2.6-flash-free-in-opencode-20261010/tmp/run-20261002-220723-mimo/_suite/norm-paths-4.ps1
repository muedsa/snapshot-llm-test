# norm-paths-4.ps1 -- take the machine root out of the process scripts.
#
# PATHS.md: "涉及文件或目录的配置、DSL、程序脚本、命令、报告和自建日志，都使用有明确基准的
# 相对路径，或读取直接指向目录的环境变量。不得写死当前机器的盘符、用户名称、用户目录、
# 仓库位置或 UNC 路径." and the row "程序脚本与复现命令 -> 明确声明的启动/脚本/配置所在目录，
# 或目录环境变量".
#
# Every historical script lives exactly three directories under the suite root
# (tmp/<run>/<task>/<script>.ps1, tmp/<run>/_suite/<script>.ps1, outputs/<run>/<task>/...),
# so the root can always be re-derived from the script's own location. The replacement keeps
# the same behaviour when the script is started from the suite root, and additionally works
# from any working directory:
#
#     $env:SNAPSHOT_TASK_ROOT  if it points at the suite root
#     else the directory three levels above this script
#
# The rewritten files are re-parsed with the PowerShell language parser before the result is
# accepted, so a syntactically broken script is never left behind.
$ErrorActionPreference = 'Stop'

$scriptRoot = $PSScriptRoot
$suiteRoot = (Get-Item (Join-Path $scriptRoot '..\..\..')).FullName
$runId = 'run-20261002-220723-mimo'

$LIT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$rxLit = [regex]'D:[\\/]{1,2}workspaces[\\/]{1,2}opencode-with-mimo-v2\.6-flash-free'

# statement form, valid on the right-hand side of an assignment:
#     $ROOT = if ($env:SNAPSHOT_TASK_ROOT) { ... } else { ... }
$ROOT_ASSIGN = "if (`$env:SNAPSHOT_TASK_ROOT) { `$env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path `$PSScriptRoot '..\..\..')).FullName }"
# subexpression form, valid where a value is expected (command arguments, call arguments):
#     (Join-Path $(if (...) { ... } else { ... }) 'suffix')
$ROOT_SUBEXPR = '$(' + $ROOT_ASSIGN + ')'
# form used inside a .NET regex replacement: '$' must be doubled or it is read as a group ref
$ROOT_ASSIGN_RE = $ROOT_ASSIGN.Replace('$', '$$')
$ROOT_SUBEXPR_RE = $ROOT_SUBEXPR.Replace('$', '$$')

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

function Test-Parses([string]$path) {
  $tokens = $null; $errors = $null
  $null = [System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$tokens, [ref]$errors)
  return ,@($errors)
}

$roots = @(
  (Join-Path $suiteRoot "tmp\$runId"),
  (Join-Path $suiteRoot "outputs\$runId")
)

$converted = 0; $skippedEncoding = 0; $leftover = @(); $broken = @(); $noChange = 0

foreach ($scope in $roots) {
  foreach ($f in @(Get-ChildItem $scope -Recurse -Filter '*.ps1' -File)) {
    $hadBom = $false
    $text = Read-Preserved $f.FullName ([ref]$hadBom)
    if ($null -eq $text) { $skippedEncoding++; continue }
    if (-not $rxLit.IsMatch($text)) { continue }

    $new = $text
    # 1. assignment form:  $ROOT = 'D:\...\opencode-with-mimo-v2.6-flash-free'
    $new = [regex]::Replace($new, ("(?m)(=\s*)'" + $rxLit + "'"), ('${1}' + $ROOT_ASSIGN_RE))
    # 2. bare single-quoted root used as a command/argument value:
    #        Set-Location 'D:\...\opencode-with-mimo-v2.6-flash-free'
    #    must become an expression, not a string, otherwise '$(...)' stays literal text
    $new = [regex]::Replace($new, ("'" + $rxLit + "'"), $ROOT_SUBEXPR_RE)
    # 3. bare double-quoted root used as a command/argument value
    $new = [regex]::Replace($new, ('"' + $rxLit + '"'), $ROOT_SUBEXPR_RE)
    # 4. single-quoted path with a suffix:  'D:\...\opencode-with-mimo-v2.6-flash-free\tmp\...'
    #    note: '$1' must stay a *PowerShell* single-quoted string, otherwise PowerShell
    #    interpolates $1 and the .NET group reference never reaches the regex engine
    $new = [regex]::Replace($new, ("'" + $rxLit + "[\\/]([^']*)'"), ("(Join-Path " + $ROOT_SUBEXPR_RE + " '" + '$1' + "')"))
    # 5. double-quoted path with a suffix:  "D:\...\opencode-with-mimo-v2.6-flash-free\tmp\..."
    $new = [regex]::Replace($new, ('"' + $rxLit + '[\\/]([^"]*)"'), ("(Join-Path " + $ROOT_SUBEXPR_RE + " '" + '$1' + "')"))
    # 6. anything else (bare literal) -> the value subexpression itself
    #    String.Replace is not a regex, so no '$$' escaping here
    $new = $rxLit.Replace($new, $ROOT_SUBEXPR)

    if ($rxLit.IsMatch($new)) { $leftover += $f.FullName.Substring($suiteRoot.Length + 1); continue }
    if ($new -eq $text) { $noChange++; continue }

    if ($hadBom) { [IO.File]::WriteAllText($f.FullName, $new, $utf8Bom) }
    else { [IO.File]::WriteAllText($f.FullName, $new, $utf8NoBom) }

    $errs = Test-Parses $f.FullName
    if ($errs.Count -gt 0) {
      $broken += ("{0} :: {1}" -f $f.FullName.Substring($suiteRoot.Length + 1), ($errs | ForEach-Object { $_.Message } | Select-Object -First 2) -join '; ')
      # restore the original text so a failure never leaves a broken script behind
      if ($hadBom) { [IO.File]::WriteAllText($f.FullName, $text, $utf8Bom) }
      else { [IO.File]::WriteAllText($f.FullName, $text, $utf8NoBom) }
      continue
    }
    $converted++
  }
}

"converted      : $converted"
"skipped (enc)  : $skippedEncoding"
"unchanged      : $noChange"
"leftover root  : $($leftover.Count)"
$leftover | Select-Object -First 10 | ForEach-Object { "   ! $_" }
"parse failures : $($broken.Count)  (restored to original)"
$broken | Select-Object -First 10 | ForEach-Object { "   ! $_" }

# ---------- final sweep: any remaining machine root anywhere in the run ----------
"--- residual machine roots by area ---"
foreach ($scope in $roots) {
  $hit = @()
  foreach ($f in @(Get-ChildItem $scope -Recurse -File)) {
    if ($f.Extension -in @('.png', '.snapshot', '.html')) { continue }   # raw bytes / raw fetches
    $bytes = [IO.File]::ReadAllBytes($f.FullName)
    $off = if ($bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191) { 3 } else { 0 }
    $enc = [System.Text.UTF8Encoding]::new($false, $true)
    try { $t = $enc.GetString($bytes, $off, $bytes.Length - $off) } catch { continue }
    $n = $rxLit.Matches($t).Count
    if ($n -gt 0) { $hit += ("{0} x{1}" -f $f.FullName.Substring($suiteRoot.Length + 1), $n) }
  }
  "  {0}: {1} file(s)" -f (Split-Path $scope -Leaf), $hit.Count
  $hit | ForEach-Object { "     ! $_" }
}
