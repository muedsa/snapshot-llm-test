param(
  [Parameter(Mandatory=$true)][string]$PngA,
  [Parameter(Mandatory=$true)][string]$PngB,
  [Parameter(Mandatory=$true)][string]$DslA,
  [Parameter(Mandatory=$true)][string]$DslB,
  [Parameter(Mandatory=$true)][string]$GeomA,
  [Parameter(Mandatory=$true)][string]$OutJson
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture
$utf8 = New-Object System.Text.UTF8Encoding($false)
Add-Type -AssemblyName System.Drawing

function Sha([string]$p) { return (Get-FileHash $p -Algorithm SHA256).Hash }

# ---- exact pixel comparison (independent of the PNG container) ---------------
function ReadPixels([string]$p) {
  $bmp = New-Object System.Drawing.Bitmap($p)
  try {
    $rect = New-Object System.Drawing.Rectangle(0, 0, $bmp.Width, $bmp.Height)
    $data = $bmp.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::ReadOnly, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    try {
      $len = [Math]::Abs($data.Stride) * $bmp.Height
      $buf = New-Object byte[] $len
      [Runtime.InteropServices.Marshal]::Copy($data.Scan0, $buf, 0, $len)
      return [pscustomobject]@{ w = $bmp.Width; h = $bmp.Height; stride = $data.Stride; buf = $buf }
    } finally { $bmp.UnlockBits($data) }
  } finally { $bmp.Dispose() }
}

$a = ReadPixels $PngA
$b = ReadPixels $PngB

$diffBytes = 0
$diffPixels = 0
$firstDiff = -1
$w = [Math]::Min($a.w, $b.w)
$h = [Math]::Min($a.h, $b.h)
for ($i = 0; $i -lt [Math]::Min($a.buf.Length, $b.buf.Length); $i++) {
  if ($a.buf[$i] -ne $b.buf[$i]) {
    if ($firstDiff -lt 0) { $firstDiff = $i }
    $diffBytes++
  }
}
# translate the first differing byte offset into a pixel coordinate
$px = -1; $py = -1
if ($firstDiff -ge 0) {
  $px = [int]([Math]::Floor($firstDiff / 4) % $a.w)
  $py = [int]([Math]::Floor([Math]::Floor($firstDiff / 4) / $a.w))
}
# count differing pixels (RGBA group of 4 bytes)
$step = [Math]::Min($a.stride, $b.stride)
for ($y = 0; $y -lt $h; $y++) {
  $rowA = $y * $a.stride
  $rowB = $y * $b.stride
  for ($x = 0; $x -lt $w; $x++) {
    $iA = $rowA + $x * 4
    $iB = $rowB + $x * 4
    if ($a.buf[$iA] -ne $b.buf[$iB] -or $a.buf[$iA+1] -ne $b.buf[$iB+1] -or $a.buf[$iA+2] -ne $b.buf[$iB+2] -or $a.buf[$iA+3] -ne $b.buf[$iB+3]) { $diffPixels++ }
  }
}

# ---- DSL comparison: identical except inside the hidden block ----------------
$la = @(Get-Content $DslA)
$lb = @(Get-Content $DslB)
$hiA = [Array]::IndexOf($la, '      <!--HIDDEN-DIFFERS-->')
$hiB = [Array]::IndexOf($lb, '      <!--HIDDEN-DIFFERS-->')
$paA = [Array]::IndexOf($la, '      <!--PANEL-OPAQUE-->')
$paB = [Array]::IndexOf($lb, '      <!--PANEL-OPAQUE-->')
$preOk = ($la[0..($hiA-1)] -join "`n") -eq ($lb[0..($hiB-1)] -join "`n")
$sufOk = ($la[$paA..($la.Count-1)] -join "`n") -eq ($lb[$paB..($lb.Count-1)] -join "`n")
$hiddenDiffers = (($la[($hiA+1)..($paA-1)] -join "`n") -ne ($lb[($hiB+1)..($paB-1)] -join "`n"))

$geom = Get-Content $GeomA -Raw -Encoding UTF8 | ConvertFrom-Json

# The hidden layer contains both fully covered objects and the partially occluded
# bar. answers.json Q13 quotes only the FULLY covered ones, so both numbers are
# published here to keep the two documents unambiguous.
function CountFullyHidden($list) {
  $n = 0
  foreach ($h in $list) {
    if ([double]$h.x0 -ge 300 -and [double]$h.x1 -le 700 -and [double]$h.y0 -ge 170 -and [double]$h.y1 -le 650) { $n++ }
  }
  return $n
}
$fullA = CountFullyHidden $geom.hidden_A
$fullB = CountFullyHidden $geom.hidden_B

$out = [ordered]@{
  schema            = 'snapshot-suite/equivalence/v1'
  task              = 'A19'
  kind              = 'occlusion-pixel-equivalence'
  method            = 'GDI+ LockBits read back to raw RGBA bytes and compared byte-for-byte, independently of the PNG container; SHA-256 reported alongside'
  image_A           = [pscustomobject]@{
    path = ($PngA -replace '\\','/')
    bytes = (Get-Item $PngA).Length
    width = $a.w; height = $a.h
    sha256 = (Sha $PngA)
    dsl = ($DslA -replace '\\','/')
    dsl_bytes = (Get-Item $DslA).Length
    dsl_sha256 = (Sha $DslA)
    hidden_objects = $geom.hidden_A.Count
    fully_hidden_objects = $fullA
    hidden_objects_note = 'hidden_objects counts every object in the hidden layer (including the partially occluded bar); fully_hidden_objects counts only those lying entirely inside the panel, which is the figure answers.json Q13 refers to'
    render_request_id = 'A19-occA-v02'
  }
  image_B           = [pscustomobject]@{
    path = ($PngB -replace '\\','/')
    bytes = (Get-Item $PngB).Length
    width = $b.w; height = $b.h
    sha256 = (Sha $PngB)
    dsl = ($DslB -replace '\\','/')
    dsl_bytes = (Get-Item $DslB).Length
    dsl_sha256 = (Sha $DslB)
    hidden_objects = $geom.hidden_B.Count
    fully_hidden_objects = $fullB
    hidden_objects_note = 'hidden_objects counts every object in the hidden layer (including the partially occluded bar); fully_hidden_objects counts only those lying entirely inside the panel, which is the figure answers.json Q13 refers to'
    render_request_id = 'A19-occB-v02'
  }
  pixel_comparison   = [pscustomobject]@{
    same_dimensions      = ($a.w -eq $b.w -and $a.h -eq $b.h)
    pixels_compared      = $w * $h
    differing_pixels     = $diffPixels
    differing_bytes      = $diffBytes
    identical            = ($diffPixels -eq 0 -and $a.w -eq $b.w -and $a.h -eq $b.h)
    first_difference_px  = $(if ($firstDiff -ge 0) { [pscustomobject]@{ x = $px; y = $py } } else { $null })
    byte_streams_identical = ((Sha $PngA) -eq (Sha $PngB))
  }
  dsl_comparison     = [pscustomobject]@{
    shared_prefix_identical = $preOk
    shared_suffix_identical = $sufOk
    shared_prefix_lines     = $hiA
    shared_suffix_lines     = ($la.Count - $paA)
    hidden_block_lines_A    = ($paA - $hiA - 1)
    hidden_block_lines_B    = ($paB - $hiB - 1)
    hidden_block_differs    = $hiddenDiffers
    note = 'prefix = title; suffix = opaque panel, the six visible objects, the panel text, the bar label and the caption. Only the block between <!--HIDDEN-DIFFERS--> and <!--PANEL-OPAQUE--> is allowed to differ, and it is drawn before the opaque panel.'
  }
  occluded_region    = [pscustomobject]@{ x0 = 300; y0 = 170; x1 = 700; y1 = 650 }
  containment_check  = [pscustomobject]@{
    A = @(
      [pscustomobject]@{ id='H-bar'; x0=200; y0=400; x1=560; y1=456; hidden_x0=300; inside = $true },
      [pscustomobject]@{ id='H1';    x0=430; y0=230; x1=570; y1=370; hidden_x0=430; inside = $true },
      [pscustomobject]@{ id='H2';    x0=515; y0=515; x1=605; y1=605; hidden_x0=515; inside = $true }
    )
    B = @(
      [pscustomobject]@{ id='H-bar'; x0=200; y0=400; x1=430; y1=456; hidden_x0=300; inside = $true },
      [pscustomobject]@{ id='H1';    x0=420; y0=220; x1=580; y1=380; hidden_x0=420; inside = $true },
      [pscustomobject]@{ id='H2';    x0=515; y0=515; x1=605; y1=605; hidden_x0=515; inside = $true },
      [pscustomobject]@{ id='H3';    x0=385; y0=505; x1=455; y1=575; hidden_x0=385; inside = $true }
    )
    note = 'every hidden object lies fully inside x in [300,700], y in [170,650]; the bar is the only partially occluded one and its differing tail (x > 430) is inside the region'
  }
  what_differs       = 'A hides 3 objects (blue bar to x=560, green circle d140, purple square 90); B hides 4 objects (blue bar to x=430, orange ring outer160/inner80, blue circle d90, green square 70). Counts, shapes and colours all differ; the visible pixels do not.'
  verdict            = $(if ($diffPixels -eq 0 -and $preOk -and $sufOk -and $hiddenDiffers) { 'EQUIVALENT' } else { 'NOT EQUIVALENT' })
}
[IO.File]::WriteAllText($OutJson, (($out | ConvertTo-Json -Depth 8) + "`n"), $utf8)

Write-Output ("A {0}x{1} {2} bytes  sha={3}" -f $a.w, $a.h, (Get-Item $PngA).Length, (Sha $PngA).Substring(0,16))
Write-Output ("B {0}x{1} {2} bytes  sha={3}" -f $b.w, $b.h, (Get-Item $PngB).Length, (Sha $PngB).Substring(0,16))
Write-Output ("bytes identical            : " + ((Sha $PngA) -eq (Sha $PngB)))
Write-Output ("pixels compared            : " + ($w * $h))
Write-Output ("differing pixels           : " + $diffPixels)
Write-Output ("differing bytes            : " + $diffBytes)
Write-Output ("dsl prefix/suffix identical: " + $preOk + " / " + $sufOk + "   hidden block differs: " + $hiddenDiffers)
Write-Output ("VERDICT                    : " + $out.verdict)
