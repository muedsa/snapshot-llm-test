# fix-suite-artifacts.ps1 -- reformat the suite_artifacts member.
#
# The member was written on a single line because $nl was never bound in that scope (the
# earlier run only defined it inside Add-RootMember). It is valid JSON but unreadable, and
# it also carries a bytes value for suite-state.json itself, which is self-referential: the
# number is stale the moment the file is written. Both are corrected here by replacing the
# single member line with a properly indented block that has no bytes field.
$ErrorActionPreference = 'Stop'

$scriptRoot = $PSScriptRoot
$suiteRoot = (Get-Item (Join-Path $scriptRoot '..\..\..')).FullName
$runId = 'run-20261002-220723-mimo'
$ssPath = Join-Path $suiteRoot "outputs\$runId\_suite\suite-state.json"

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$utf8Bom = [System.Text.UTF8Encoding]::new($true)

$bytes = [IO.File]::ReadAllBytes($ssPath)
$hadBom = ($bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191)
$off = if ($hadBom) { 3 } else { 0 }
$text = [System.Text.UTF8Encoding]::new($false, $true).GetString($bytes, $off, $bytes.Length - $off)

$ss = $text | ConvertFrom-Json
$entries = @($ss.suite_artifacts)
if ($entries.Count -eq 0) { throw 'suite_artifacts is empty; nothing to reformat' }

$nl = if ($text.Contains("`r`n")) { "`r`n" } else { "`n" }
$blocks = New-Object System.Collections.Generic.List[string]
foreach ($e in $entries) {
  $lines = New-Object System.Collections.Generic.List[string]
  $lines.Add('      {')
  $lines.Add(('        "path": "{0}",' -f $e.path))
  $lines.Add(('        "path_base": "{0}",' -f $e.path_base))
  $lines.Add(('        "role": "{0}",' -f ($e.role -replace '\\', '/' -replace '"', '\"')))
  $lines.Add(('        "required_by_suite_config": {0},' -f ([bool]$e.required_by_suite_config).ToString().ToLower()))
  $lines.Add(('        "exists": {0}' -f ([bool]$e.exists).ToString().ToLower()))
  $lines.Add('      }')
  $blocks.Add(($lines -join $nl))
}

$member = ('    "suite_artifacts": [' + $nl + ($blocks -join (',' + $nl)) + $nl + '    ]')

# locate the existing member: it starts at an "    " prefix and ends at the matching ']'
$start = $text.IndexOf('"suite_artifacts": [')
if ($start -lt 0) { throw 'suite_artifacts member not found' }
$lineStart = $text.LastIndexOf("`n", $start)
$lineStart = if ($lineStart -lt 0) { 0 } else { $lineStart + 1 }

$depth = 0; $inStr = $false; $esc = $false; $end = -1
for ($i = $start; $i -lt $text.Length; $i++) {
  $c = $text[$i]
  if ($inStr) {
    if ($esc) { $esc = $false }
    elseif ($c -eq '\') { $esc = $true }
    elseif ($c -eq '"') { $inStr = $false }
    continue
  }
  if ($c -eq '"') { $inStr = $true }
  elseif ($c -eq '[') { $depth++ }
  elseif ($c -eq ']') { $depth--; if ($depth -eq 0) { $end = $i; break } }
}
if ($end -lt 0) { throw 'closing bracket of suite_artifacts not found' }

# swallow trailing spaces/tabs after the closing bracket, keep the rest of the line
$e2 = $end + 1
while ($e2 -lt $text.Length -and ($text[$e2] -eq ' ' -or $text[$e2] -eq "`t")) { $e2++ }

$new = $text.Substring(0, $lineStart) + $member + $text.Substring($e2)
if ($hadBom) { [IO.File]::WriteAllText($ssPath, $new, $utf8Bom) }
else { [IO.File]::WriteAllText($ssPath, $new, $utf8NoBom) }

$check = [IO.File]::ReadAllText($ssPath, [Text.Encoding]::UTF8) | ConvertFrom-Json
$physical = [IO.File]::ReadAllLines($ssPath, [Text.Encoding]::UTF8).Count
$nEntries = @($check.suite_artifacts).Count
$nBytes = ([regex]::Matches([IO.File]::ReadAllText($ssPath, [Text.Encoding]::UTF8), '"bytes":\s*\d+')).Count
"reformatted: suite_artifacts=$nEntries  bytes_field_left=$nBytes  lines=$physical  parse=OK"
foreach ($a in $check.suite_artifacts) {
  "   {0,-56} req={1,-5} exists={2}" -f $a.path, $a.required_by_suite_config, $a.exists
}
