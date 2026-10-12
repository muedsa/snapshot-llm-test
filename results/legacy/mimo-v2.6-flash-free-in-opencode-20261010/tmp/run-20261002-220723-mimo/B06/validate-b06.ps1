# validate-b06.ps1 -- static attribute/structure validation for B06 .snapshot files.
# Prints one line per file and a summary; non-zero exit when any problem is found.
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$b6   = Join-Path $root 'tmp\run-20261002-220723-mimo\B06'
$out  = Join-Path $root 'outputs\run-20261002-220723-mimo\B06'

$files = @()
if (Test-Path $b6)   { $files += Get-ChildItem $b6 -Recurse -Filter '*.snapshot' -File }
if (Test-Path $out)  { $files += Get-ChildItem $out -Recurse -Filter '*.snapshot' -File }
$files = $files | Sort-Object FullName -Unique
if ($files.Count -eq 0) { Write-Output 'no .snapshot files found'; exit 1 }

$total = 0
foreach ($f in $files) {
    $s = [IO.File]::ReadAllText($f.FullName, [Text.Encoding]::UTF8)
    $problems = @()

    if ($s -notmatch '^<Snapshot ') { $problems += 'root is not <Snapshot>' }
    if ($s -notmatch '</Snapshot>\s*$') { $problems += 'root is not closed' }
    if (([regex]::Matches($s, '<Positioned')).Count -ne ([regex]::Matches($s, '</Positioned>')).Count) {
        $problems += 'unbalanced <Positioned>'
    }
    if (([regex]::Matches($s, '<Transform')).Count -ne ([regex]::Matches($s, '</Transform>')).Count) {
        $problems += 'unbalanced <Transform>'
    }

    # every attribute in the document, all values
    $attrs = [regex]::Matches($s, '([A-Za-z][A-Za-z0-9_]*)="([^"]*)"')
    foreach ($m in $attrs) {
        $k = $m.Groups[1].Value
        $v = $m.Groups[2].Value

        if ($k -eq 'fontStyle') {
            $problems += "forbidden attribute fontStyle=$v"
        }
        elseif ($k -eq 'border') {
            if ($v -ne '' -and $v -notmatch '^\d+(\.\d+)? SOLID #[0-9A-Fa-f]{6,8}$') {
                $problems += "bad border '$v'"
            }
        }
        elseif ($k -eq 'color') {
            if ($v -eq 'none') { $problems += "unproven color='none'" }
            elseif ($v -ne '' -and $v -notmatch '^#[0-9A-Fa-f]{6,8}$') { $problems += "bad color '$v'" }
        }
        elseif ($k -eq 'textAlign') {
            if ($v -ne 'LEFT' -and $v -ne 'RIGHT' -and $v -ne 'CENTER') { $problems += "bad textAlign '$v'" }
        }
        elseif ($k -eq 'boxShadow') {
            if ($v -notmatch '^ELEVATION_\d+$' -and $v -notmatch '^-?\d+(\.\d+)? -?\d+(\.\d+)? -?\d+(\.\d+)? #[0-9A-Fa-f]{6,8}$') {
                $problems += "bad boxShadow '$v'"
            }
        }
        elseif ($k -eq 'matrix') {
            $n = ($v -replace '[(),]', ' ') -split '\s+' | Where-Object { $_ -ne '' }
            if ($n.Count -ne 16) { $problems += "matrix has $($n.Count) numbers (want 16)" }
        }
        elseif ($k -eq 'fontSize' -or $k -eq 'width' -or $k -eq 'height' -or $k -eq 'left' -or $k -eq 'top') {
            if ($v -ne '' -and $v -notmatch '^-?\d+(\.\d+)?$') { $problems += "bad numeric $k='$v'" }
        }
    }

    # no raw text that would be interpreted as markup
    if ($s -match '(?<!&lt;)(?<!&amp;)<br') { $problems += 'raw <br in text' }

    $cnt = $problems.Count
    $total += $cnt
    if ($cnt -eq 0) {
        $g = [regex]::Match($s, '<Container width="(\d+)" height="(\d+)"')
        Write-Output ("OK   {0}  {1}x{2}  {3} bytes" -f ($f.Directory.Name + '\' + $f.Name), $g.Groups[1].Value, $g.Groups[2].Value, $s.Length)
    } else {
        Write-Output ("BAD  {0}  ({1})" -f ($f.Directory.Name + '\' + $f.Name), $cnt)
        $problems | ForEach-Object { Write-Output ("       - " + $_) }
    }
}

Write-Output ("files={0}  problems={1}" -f $files.Count, $total)
if ($total -gt 0) { exit 1 }
exit 0
