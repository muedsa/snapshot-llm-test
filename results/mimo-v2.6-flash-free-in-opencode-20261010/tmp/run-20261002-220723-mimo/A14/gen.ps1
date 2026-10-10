param([int]$Ver = 1)

# ---------------------------------------------------------------- A14 gen ----
# inputs/cards.json  -> 8 complete 1200x630 DSLs (card-K01 .. card-K08) plus a
# badge probe. One parametric rule set; nothing is hard-coded per card.
#
#   * shared on all 8: palette, brand mark, brand string, date, title zone,
#     status system, divider, footer grid
#   * length drives the title font size (ladder) and the line breaks
#   * title >= 36px and <= 3 lines; speaker >= 22px and <= 2 lines
#   * every box stays inside the 40px safe margin; title never meets the badge
#   * no Image, no transform/scale: the whole card is emitted from data

$ErrorActionPreference = 'Stop'
[System.Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[System.Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root

$TMP = "$root\tmp\$RUN\A14"
New-Item -ItemType Directory -Force -Path $TMP | Out-Null

# ------------------------------------------------------------------ input ----
$SRC = "$root\tasks\A14-content-stress-batch\inputs\cards.json"
$CARDS_JSON = [IO.File]::ReadAllText($SRC, [Text.UTF8Encoding]::new($false))
# ConvertFrom-Json emits a JSON array as ONE pipeline object in PS 5.1, so a
# wrapping @(...) would give Count = 1; assign first, then normalise.
$CARD_RAW = ConvertFrom-Json -InputObject $CARDS_JSON
if ($CARD_RAW -is [array]) { $CARD_LIST = $CARD_RAW } else { $CARD_LIST = @($CARD_RAW) }
if ($CARD_LIST.Count -ne 8) { throw ('expected 8 cards, got ' + $CARD_LIST.Count) }

# ----------------------------------------------------------------- palette ----
$BG      = '#0B1220'
$LINE    = '#23324C'
$INK     = '#F8FAFC'
$MUTED   = '#9FB0CB'
$PRIMARY = '#38BDF8'
$AMBER   = '#F6B94A'
$PILLINK = '#0B1220'
$CANCELINK = '#F87171'
$FAM  = 'Noto Sans CJK SC,Noto Sans CJK JP'
$MONO = 'Noto Sans Mono CJK SC'

$BRAND = 'Structure / Vision'
$DATEL = '2026.11.07'
$CANCELNOTE = '本场取消'

$STATUS = [ordered]@{
  ([string]'开放') = [pscustomobject]@{ sym = [string]'○'; code = 'U+25CB'; color = '#34D399' }
  ([string]'满额') = [pscustomobject]@{ sym = [string]'◆'; code = 'U+25C6'; color = '#F6B94A' }
  ([string]'候补') = [pscustomobject]@{ sym = [string]'△'; code = 'U+25B3'; color = '#A78BFA' }
  ([string]'取消') = [pscustomobject]@{ sym = [string]'×'; code = 'U+00D7'; color = '#F87171' }
}

# ----------------------------------------------------------------- geometry ---
$W = 1200; $H = 630; $M = 40
$CW        = $W - (2 * $M)      # 1120 content width
$MARK_Y    = 50
$BRAND_Y   = 48
$BADGE_Y   = 40
$BADGE_H   = 40
$BADGE_FS  = 26
$BADGE_PAD = 22
$TITLE_TOP = 104
$ZONE_BOT  = 396            # 8px of air above the rule
$ZONE_H    = $ZONE_BOT - $TITLE_TOP
$TITLE_W   = $CW
$DIV_Y     = 404
$DIV1_W    = 240
# ---- footer geometry (bottom-anchored, see the emission block below) --------
# The speaker block is placed so its last line ends exactly on the safe line
# (H - M = 590), which keeps the card's top and bottom margins both at 40px.
# The time row sits $FOOT_GAP above the speaker block. A 2-line speaker is
# 37 + 32 = 69px tall and still lands on 590, so it can never overflow.
$TIME_FS   = 56
$TIME_W    = 520
$FOOT_GAP  = 18
$DATE_W    = 500
$NOTE_W    = 500
$SPK_W     = 560
$LEAD      = 1.16

$TITLE_LADDER = @(112, 104, 96, 88, 80, 72, 64, 56, 48, 40, 36)
$SPK_LADDER   = @(32, 30, 28, 26, 24, 22)

# chars that may not start a line (Chinese line-breaking rule) / that make a
# good natural break point after them. Built from code points because
# PowerShell parses U+2018/U+2019/U+201C/U+201D as quote delimiters.
$NOSTART = -join @(
  [char]0xFF0C, [char]0x3002, [char]0x3001, [char]0xFF1B, [char]0xFF1A,
  [char]0xFF1F, [char]0xFF01, [char]0xFF09, [char]0x3011, [char]0x300B,
  [char]0x3009, [char]0x300D, [char]0x300F, [char]0x201D, [char]0x2019,
  [char]0x2026, [char]0xFF0F, [char]0x0029, [char]0x003E, [char]0x005D,
  [char]0x007D, [char]0x0026, [char]0x002F
)
$PREFBREAK = -join @(
  [char]0xFF0C, [char]0x3002, [char]0x3001, [char]0xFF1B, [char]0xFF1A,
  [char]0xFF1F, [char]0xFF01, [char]0xFF09, [char]0x3011, [char]0x300B,
  [char]0x3009, [char]0x300D, [char]0x300F, [char]0x201D, [char]0x2019,
  [char]0x2026, [char]0xFF0F, [char]0x2014, [char]0x002F
)

# ---------------------------------------------------------------- measuring ---
function Test-FW([char]$ch) {
  $cp = [int][char]$ch
  if ($cp -ge 0x2E80) { return $true }
  if ($cp -ge 0x25A0 -and $cp -le 0x25FF) { return $true }
  if ($cp -ge 0x2600 -and $cp -le 0x26FF) { return $true }
  if ($cp -in @(0x2013, 0x2014, 0x2015, 0x2018, 0x2019, 0x201C, 0x201D, 0x2026, 0x2030)) { return $true }
  return $false
}

# conservative advance width in em (CJK = 1.0em; latin by class; mono = 0.62)
function Get-Em([string]$s, [string]$mode) {
  $em = 0.0
  foreach ($ch in $s.ToCharArray()) {
    if (Test-FW $ch) { $em += 1.0; continue }
    if ($mode -eq 'mono') { $em += 0.62; continue }
    $cp = [int][char]$ch
    if ($cp -gt 127) { $em += 0.55; continue }
    if ($ch -ge 'A' -and $ch -le 'Z') { $em += 0.74; continue }
    if ($ch -ge 'a' -and $ch -le 'z') { $em += 0.58; continue }
    if ($ch -ge '0' -and $ch -le '9') { $em += 0.58; continue }
    if ($ch -eq ' ') { $em += 0.30; continue }
    $em += 0.40
  }
  return $em
}

# px width of one atom. CJK/fullwidth glyphs have an exact 1em advance in
# Noto Sans CJK, so they only need a 5% pad; latin metrics are genuinely
# estimated, so they get 10%.
function Get-AtomPx([string]$s, [int]$size, [string]$mode) {
  $f = 1.10
  if ($s.Length -gt 0) { if (Test-FW $s[0]) { $f = 1.05 } }
  $em = Get-Em $s $mode
  return ($em * $size * $f)
}

# px width of a whole string (used for single-line fits and pill widths)
function Get-W([string]$s, [int]$size, [string]$mode) {
  $px = 0.0
  foreach ($ch in $s.ToCharArray()) { $px += Get-AtomPx ([string]$ch) $size $mode }
  return [int][math]::Ceiling($px)
}

# ---------------------------------------------------------------- tokenizer ---
# latin words stay whole (spaces end an atom), every CJK/fullwidth char is its
# own atom, and a CJK em-dash pair is kept together so —— is never split.
function Get-Atoms([string]$s) {
  $atoms = New-Object System.Collections.Generic.List[string]
  $chars = $s.ToCharArray()
  $buf = ''
  for ($i = 0; $i -lt $chars.Length; $i++) {
    $ch = $chars[$i]
    if (Test-FW $ch) {
      if ($buf -ne '') { $atoms.Add($buf); $buf = '' }
      $isDash = (([int][char]$ch) -eq 0x2014)
      if ($isDash -and (($i + 1) -lt $chars.Length) -and (([int][char]$chars[$i + 1]) -eq 0x2014)) {
        $atoms.Add([string]$ch + [string]$chars[$i + 1])
        $i++
      } else {
        $atoms.Add([string]$ch)
      }
    } elseif ($ch -eq ' ') {
      $buf += ' '
      $atoms.Add($buf)
      $buf = ''
    } else {
      $buf += $ch
    }
  }
  if ($buf -ne '') { $atoms.Add($buf) }
  return ,$atoms.ToArray()
}

function Test-NoStart([string]$atom) {
  $t = $atom.TrimEnd(' ')
  if ($t -eq '') { return $false }
  return $NOSTART.Contains([string]$t[$t.Length - 1])
}

function Test-PrefEnd([string]$atom) {
  if ($atom.EndsWith(' ')) { return $true }
  $t = $atom.TrimEnd(' ')
  if ($t -eq '') { return $false }
  return $PREFBREAK.Contains([string]$t[$t.Length - 1])
}

# ---------------------------------------------------------------- wrapping ----
# try every cut of the atom list into exactly n lines; keep the candidates
# whose lines all fit and whose continuation lines do not begin with forbidden
# punctuation; rank: natural break > even balance > smaller first line.
function Find-Split([string[]]$atoms, [double[]]$w, [int]$avail, [int]$n) {
  $cnt = $atoms.Length
  if ($n -eq 1) {
    $tot = 0.0
    for ($i = 0; $i -lt $cnt; $i++) { $tot += $w[$i] }
    # a single row has no break to judge: pref = 0 so a size that merely
    # fits on one row never outranks a larger size broken at punctuation
    if ($tot -le $avail) { return @{ cuts = @(); pref = 0 } }
    return $null
  }

  $pref = New-Object 'double[]' ($cnt + 1)
  for ($i = 0; $i -lt $cnt; $i++) { $pref[$i + 1] = $pref[$i] + $w[$i] }
  $total = $pref[$cnt]
  $thr = 0.70 * $avail

  $cands = New-Object System.Collections.Generic.List[object]

  if ($n -eq 2) {
    for ($k = 1; $k -lt $cnt; $k++) {
      $seg1 = $pref[$k]
      $seg2 = $total - $pref[$k]
      $lw = @($seg1, $seg2)
      if (($lw | Measure-Object -Maximum).Maximum -gt $avail) { continue }
      if (Test-NoStart $atoms[$k]) { continue }
      $isPref = 0
      if ((Test-PrefEnd $atoms[$k - 1]) -and ($lw[0] -ge $thr)) { $isPref = 1 }
      $imb = [math]::Abs($lw[0] - $lw[1])
      $cands.Add([pscustomobject]@{ cuts = @($k); pref = $isPref; imb = $imb; k1 = $k })
    }
  } else {
    for ($k1 = 1; $k1 -lt ($cnt - 1); $k1++) {
      for ($k2 = ($k1 + 1); $k2 -lt $cnt; $k2++) {
        $seg1 = $pref[$k1]
        $seg2 = $pref[$k2] - $pref[$k1]
        $seg3 = $total - $pref[$k2]
        $lw = @($seg1, $seg2, $seg3)
        if (($lw | Measure-Object -Maximum).Maximum -gt $avail) { continue }
        if (Test-NoStart $atoms[$k1]) { continue }
        if (Test-NoStart $atoms[$k2]) { continue }
        $isPref = 0
        if ((Test-PrefEnd $atoms[$k1 - 1]) -and ($lw[0] -ge $thr)) { $isPref = 1 }
        $imb = ($lw | Measure-Object -Maximum).Maximum - ($lw | Measure-Object -Minimum).Minimum
        $cands.Add([pscustomobject]@{ cuts = @($k1, $k2); pref = $isPref; imb = $imb; k1 = $k1 })
      }
    }
  }

  if ($cands.Count -eq 0) { return $null }
  $best = $null
  foreach ($c in $cands) {
    if ($null -eq $best) { $best = $c; continue }
    if ($c.pref -gt $best.pref) { $best = $c; continue }
    if ($c.pref -lt $best.pref) { continue }
    if ($c.imb -lt ($best.imb - 0.001)) { $best = $c; continue }
    if (([math]::Abs($c.imb - $best.imb) -le 0.001) -and ($c.k1 -lt $best.k1)) { $best = $c; continue }
  }
  return @{ cuts = @($best.cuts); pref = [int]$best.pref }
}

function Build-Lines([string[]]$atoms, [int[]]$cuts) {
  $lines = New-Object System.Collections.Generic.List[string]
  $prev = 0
  $bounds = @($cuts) + @($atoms.Length)
  foreach ($b in $bounds) {
    $part = ''
    for ($i = $prev; $i -lt $b; $i++) { $part += $atoms[$i] }
    $lines.Add($part.TrimEnd(' '))
    $prev = $b
  }
  return ,$lines.ToArray()
}

# Largest size from the ladder that sets the text in <= 2 rows AND breaks on a
# natural boundary (punctuation / space). A single row counts as natural.
# If no size in the ladder offers a natural break, the largest size that still
# fits in <= 2 rows is used with the most even break instead; a 3-row result is
# only ever kept when nothing in the ladder reaches 2 rows.
function Resolve-Text([string]$text, [int]$avail, [int[]]$ladder, [int]$maxLines, [string]$mode) {
  $atoms = Get-Atoms $text
  $fbRows = $null
  $fbAny = $null
  foreach ($size in $ladder) {
    $w = New-Object 'double[]' $atoms.Length
    for ($i = 0; $i -lt $atoms.Length; $i++) { $w[$i] = Get-AtomPx $atoms[$i] $size $mode }
    $hit = $null
    for ($n = 1; $n -le $maxLines; $n++) {
      $split = Find-Split $atoms $w $avail $n
      if ($null -eq $split) { continue }
      $lines = Build-Lines $atoms @($split.cuts)
      $hit = [pscustomobject]@{
        size = $size; count = $lines.Count; lines = @($lines)
        atom_count = $atoms.Length; cuts = @($split.cuts); natural = [int]$split.pref
      }
      break
    }
    if ($null -eq $hit) { continue }
    if (($hit.count -le 2) -and ($hit.natural -eq 1)) { return $hit }
    if (($hit.count -le 2) -and ($null -eq $fbRows)) { $fbRows = $hit }
    if ($null -eq $fbAny) { $fbAny = $hit }
  }
  if ($null -ne $fbRows) { return $fbRows }
  return $fbAny
}

# ------------------------------------------------------------------- emit -----
$script:NODES = New-Object System.Collections.Generic.List[string]

function Put-Box([string]$id, [int]$x, [int]$y, [int]$w, [int]$h, [string]$col, [int]$radius) {
  $r = ''
  if ($radius -gt 0) { $r = ' borderRadius="' + $radius + '"' }
  $node = '<Positioned left="' + $x + '" top="' + $y + '" width="' + $w + '" height="' + $h + '"><Container width="' + $w + '" height="' + $h + '" color="' + $col + '"' + $r + '/></Positioned>'
  [void]$script:NODES.Add($node)
}

function Put-Text([string]$id, [int]$x, [int]$y, [int]$w, [string]$txt, [int]$fs, [string]$fam, [string]$col, [string]$align, [string]$style) {
  if ($txt.Contains(']]>')) { throw ('CDATA terminator in: ' + $txt) }
  $st = ''
  if ($style -ne '') { $st = ' fontStyle="' + $style + '"' }
  $node = '<Positioned left="' + $x + '" top="' + $y + '" width="' + $w + '"><Text fontFamily="' + $fam + '" fontSize="' + $fs + '" color="' + $col + '"' + $st + ' textAlign="' + $align + '" height="1.0"><Raw><![CDATA[' + $txt + ']]></Raw></Text></Positioned>'
  [void]$script:NODES.Add($node)
}

# pairwise disjoint test over text boxes (title lines, speaker lines, footer)
function Test-Disjoint([object[]]$boxes) {
  for ($i = 0; $i -lt $boxes.Count; $i++) {
    for ($j = $i + 1; $j -lt $boxes.Count; $j++) {
      $a = $boxes[$i]; $b = $boxes[$j]
      $ox = [math]::Min($a.x + $a.width, $b.x + $b.width) - [math]::Max($a.x, $b.x)
      $oy = [math]::Min($a.y + $a.height, $b.y + $b.height) - [math]::Max($a.y, $b.y)
      if (($ox -gt 0) -and ($oy -gt 0)) { return $false }
    }
  }
  return $true
}

# ---------------------------------------------------------------- badge probe -
$script:NODES.Clear()
$probeW = 760
$pillW = 0
foreach ($k in $STATUS.Keys) {
  $s = $STATUS[$k]
  $t = $s.sym + ' ' + $k
  $ew = Get-W $t $BADGE_FS 'fam'
  if (($ew + (2 * $BADGE_PAD)) -gt $pillW) { $pillW = $ew + (2 * $BADGE_PAD) }
}
$px = 40
$probeRecs = @()
foreach ($k in $STATUS.Keys) {
  $s = $STATUS[$k]
  $t = $s.sym + ' ' + $k
  Put-Box ('probe/pill-' + $k) $px 60 $pillW $BADGE_H $s.color 20
  Put-Text ('probe/label-' + $k) ($px + $BADGE_PAD) 67 ($pillW - (2 * $BADGE_PAD)) $t $BADGE_FS $FAM $PILLINK 'CENTER' ''
  $probeRecs += [pscustomobject]@{ status = $k; symbol = $s.sym; code = $s.code; color = $s.color; text = $t; pill = [pscustomobject]@{ x = $px; y = 60; width = $pillW; height = $BADGE_H } }
  $px = $px + $pillW + 24
}
$probeW = $px + 16
$probeDoc = '<Snapshot type="png" background="' + $BG + '"><Container width="' + $probeW + '" height="160" color="' + $BG + '"><Stack>' + ([string]::Join('', $script:NODES.ToArray())) + '</Stack></Container></Snapshot>'
$probePath = "$TMP\probe-badges-v$Ver.snapshot"
[IO.File]::WriteAllText($probePath, $probeDoc, [Text.UTF8Encoding]::new($false))

# ------------------------------------------------------------------- cards ----
$layout = New-Object System.Collections.Generic.List[object]

foreach ($cd in $CARD_LIST) {
  $cid  = [string]$cd.id
  $tit  = [string]$cd.title
  $spk  = [string]$cd.speaker
  $stm  = [string]$cd.time
  $sts  = [string]$cd.status
  if (-not $STATUS.Contains($sts)) { throw ("unknown status on " + $cid + ": " + $sts) }
  $smeta = $STATUS[$sts]
  $badgeText = $smeta.sym + ' ' + $sts

  $script:NODES.Clear()
  $textBoxes = New-Object System.Collections.Generic.List[object]

  # ---- header: brand mark + brand string + status badge (shared) ---------
  Put-Box ($cid + '/mark-1') 40 $MARK_Y 20 20 $PRIMARY 4
  Put-Box ($cid + '/mark-2') 64 $MARK_Y 20 20 $AMBER 4
  $brandW = Get-W $BRAND 24 'fam'
  Put-Text ($cid + '/brand') 96 $BRAND_Y 520 $BRAND 24 $FAM $INK 'START' ''
  $textBoxes.Add([pscustomobject]@{ id = 'brand'; x = 96; y = $BRAND_Y; width = 520; height = 24; text = $BRAND })

  $pillX = $W - $M - $pillW
  Put-Box ($cid + '/badge') $pillX $BADGE_Y $pillW $BADGE_H $smeta.color 20
  Put-Text ($cid + '/badge-t') ($pillX + $BADGE_PAD) 47 ($pillW - (2 * $BADGE_PAD)) $badgeText $BADGE_FS $FAM $PILLINK 'CENTER' ''
  $badgeBox = [pscustomobject]@{ id = 'badge'; x = $pillX; y = $BADGE_Y; width = $pillW; height = $BADGE_H; text = $badgeText }

  # ---- title zone: one shared box (104..396); the block is centred in it so
  #      a one-row title does not leave a hole under it --------------------
  $tr = Resolve-Text $tit $TITLE_W $TITLE_LADDER 3 'fam'
  if ($null -eq $tr) { throw ($cid + ': title cannot be set within 3 lines') }
  if ($tr.size -lt 36) { throw ($cid + ': title size ' + $tr.size + ' < 36') }
  if ($tr.count -gt 3) { throw ($cid + ': title lines ' + $tr.count + ' > 3') }
  $lh = [int][math]::Round($tr.size * $LEAD)
  $titleBlock = (($tr.count - 1) * $lh) + $tr.size
  $titleTop = $TITLE_TOP + [int][math]::Floor(($ZONE_H - $titleBlock) / 2)
  if (($titleTop -lt $TITLE_TOP) -or (($titleTop + $titleBlock) -gt $ZONE_BOT)) {
    throw ($cid + ': title block ' + $titleBlock + ' does not fit the shared zone')
  }
  $titleBoxes = @()
  for ($i = 0; $i -lt $tr.count; $i++) {
    $ty = $titleTop + ($i * $lh)
    $tline = [string]$tr.lines[$i]
    Put-Text ($cid + '/title-' + ($i + 1)) 40 $ty $TITLE_W $tline $tr.size $FAM $INK 'START' 'BOLD'
    $b = [pscustomobject]@{ id = ('title-' + ($i + 1)); x = 40; y = $ty; width = $TITLE_W; height = $tr.size; text = $tline }
    $titleBoxes += $b
    $textBoxes.Add($b)
  }
  $titleBottom = $titleTop + $titleBlock
  if ($titleBottom -gt ($DIV_Y - 8)) { throw ($cid + ': title bottom ' + $titleBottom + ' too close to divider') }

  # ---- divider: status-coloured head + neutral tail (shared geometry) ----
  Put-Box ($cid + '/div-1') 40 $DIV_Y $DIV1_W 1 $smeta.color 0
  Put-Box ($cid + '/div-2') (40 + $DIV1_W) $DIV_Y ($CW - $DIV1_W) 1 $LINE 0

  # ---- footer: bottom-anchored so the card keeps an even 40px top and bottom
  #      margin; the speaker row sits on the safe line and the time row is
  #      $FOOT_GAP above it. The speaker block height drives both rows, so a
  #      2-line speaker simply lifts the time row instead of overflowing.
  $sr = Resolve-Text $spk $SPK_W $SPK_LADDER 2 'fam'
  if ($null -eq $sr) { throw ($cid + ': speaker cannot be set within 2 lines') }
  if ($sr.size -lt 22) { throw ($cid + ': speaker size ' + $sr.size + ' < 22') }
  $slh = [int][math]::Round($sr.size * $LEAD)
  $spkBlock = (($sr.count - 1) * $slh) + $sr.size
  $spkTop = ($H - $M) - $spkBlock
  $footY  = $spkTop - $FOOT_GAP - $TIME_FS
  if ($footY -lt ($DIV_Y + 8)) { throw ($cid + ': footer row collides with the divider') }

  $timeW = Get-W $stm $TIME_FS 'mono'
  if ($timeW -gt $TIME_W) { throw ($cid + ': time does not fit') }
  Put-Text ($cid + '/time') 40 $footY $TIME_W $stm $TIME_FS $MONO $PRIMARY 'START' ''
  $textBoxes.Add([pscustomobject]@{ id = 'time'; x = 40; y = $footY; width = $TIME_W; height = $TIME_FS; text = $stm })

  $speakerBoxes = @()
  for ($i = 0; $i -lt $sr.count; $i++) {
    $sy = $spkTop + ($i * $slh)
    $sline = [string]$sr.lines[$i]
    Put-Text ($cid + '/speaker-' + ($i + 1)) 40 $sy $SPK_W $sline $sr.size $FAM $INK 'START' ''
    $b = [pscustomobject]@{ id = ('speaker-' + ($i + 1)); x = 40; y = $sy; width = $SPK_W; height = $sr.size; text = $sline }
    $speakerBoxes += $b
    $textBoxes.Add($b)
  }
  $spkBottom = $spkTop + $spkBlock
  if ($spkBottom -gt ($H - $M)) { throw ($cid + ': speaker overflows the safe area') }

  # date rides on the speaker row (bottom right of every card is populated)
  $dateW = Get-W $DATEL 30 'mono'
  if ($dateW -gt $DATE_W) { throw ($cid + ': date does not fit') }
  Put-Text ($cid + '/date') (660) $spkTop $DATE_W $DATEL 30 $MONO $MUTED 'END' ''
  $textBoxes.Add([pscustomobject]@{ id = 'date'; x = 660; y = $spkTop; width = $DATE_W; height = 30; text = $DATEL })

  $noteRec = $null
  if ($sts -eq '取消') {
    Put-Text ($cid + '/cancel-note') 660 $footY $NOTE_W $CANCELNOTE 30 $FAM $CANCELINK 'END' ''
    $nb = [pscustomobject]@{ id = 'cancel-note'; x = 660; y = $footY; width = $NOTE_W; height = 30; text = $CANCELNOTE }
    $textBoxes.Add($nb)
    $noteRec = $nb
  }

  # ---- guards ----------------------------------------------------------
  foreach ($b in $textBoxes) {
    if ($b.x -lt $M -or $b.y -lt $M) { throw ($cid + '/' + $b.id + ' starts outside the safe margin') }
    if (($b.x + $b.width) -gt ($W - $M)) { throw ($cid + '/' + $b.id + ' crosses the right safe margin') }
    if (($b.y + $b.height) -gt ($H - $M)) { throw ($cid + '/' + $b.id + ' crosses the bottom safe margin') }
  }
  $all = @($textBoxes.ToArray())
  if (-not (Test-Disjoint $all)) { throw ($cid + ': two text boxes overlap') }
  foreach ($tb in $titleBoxes) {
    $ox = [math]::Min($tb.x + $tb.width, $badgeBox.x + $badgeBox.width) - [math]::Max($tb.x, $badgeBox.x)
    $oy = [math]::Min($tb.y + $tb.height, $badgeBox.y + $badgeBox.height) - [math]::Max($tb.y, $badgeBox.y)
    if (($ox -gt 0) -and ($oy -gt 0)) { throw ($cid + ': title collides with the status badge') }
  }

  # ---- write the DSL ----------------------------------------------------
  $doc = '<Snapshot type="png" background="' + $BG + '"><Container width="' + $W + '" height="' + $H + '" color="' + $BG + '"><Stack>' + ([string]::Join('', $script:NODES.ToArray())) + '</Stack></Container></Snapshot>'
  $outPath = "$TMP\card-$cid-v$Ver.snapshot"
  [IO.File]::WriteAllText($outPath, $doc, [Text.UTF8Encoding]::new($false))

  $layout.Add([pscustomobject][ordered]@{
    id = $cid
    dsl = ("tmp/$RUN/A14/card-$cid-v$Ver.snapshot")
    dsl_bytes = (Get-Item $outPath).Length
    content = [pscustomobject][ordered]@{ title = $tit; speaker = $spk; time = $stm; status = $sts }
    title = [pscustomobject][ordered]@{
      font_size = $tr.size; min_required = 36
      lines = $tr.count; max_allowed = 3
      line_height = $lh
      line_texts = @($tr.lines)
      natural_break = $(if ($tr.count -gt 1) { [bool]$tr.natural } else { $null })
      break_rule = 'largest ladder size that fits in <=2 rows and breaks on punctuation/space; a balanced break is used only when no size in the ladder offers a natural break; a single row has no break to judge'
      zone_top = $TITLE_TOP; zone_height = $ZONE_H; zone_bottom = $ZONE_BOT; zone_width = $TITLE_W
      alignment = 'block centred vertically inside the shared zone'
      block_top = $titleTop; block_height = $titleBlock
      top = $titleTop; bottom = $titleBottom
      boxes = @($titleBoxes)
    }
    speaker = [pscustomobject][ordered]@{
      font_size = $sr.size; min_required = 22
      lines = $sr.count; max_allowed = 2
      line_height = $slh
      line_texts = @($sr.lines)
      natural_break = $(if ($sr.count -gt 1) { [bool]$sr.natural } else { $null })
      top = $spkTop; bottom = $spkBottom; anchor = 'block bottom rests exactly on the safe line'
      boxes = @($speakerBoxes)
    }
    status_encoding = [pscustomobject][ordered]@{
      text = $sts; symbol = $smeta.sym; symbol_codepoint = $smeta.code
      color = $smeta.color; label = $badgeText
      pill = [pscustomobject]@{ x = $pillX; y = $BADGE_Y; width = $pillW; height = $BADGE_H }
      label_box = [pscustomobject]@{ x = ($pillX + $BADGE_PAD); y = 47; width = ($pillW - (2 * $BADGE_PAD)); height = $BADGE_FS }
      divider_head = [pscustomobject]@{ x = 40; y = $DIV_Y; width = $DIV1_W; height = 1; color = $smeta.color }
      encoding = 'color + symbol + text (all three, on every card)'
    }
    time_box = [pscustomobject]@{ x = 40; y = $footY; width = $TIME_W; height = $TIME_FS }
    date_box = [pscustomobject]@{ x = 660; y = $spkTop; width = $DATE_W; height = 30 }
    brand_box = [pscustomobject]@{ x = 96; y = $BRAND_Y; width = 520; height = 24 }
    badge_box = $badgeBox
    cancel_note = $noteRec
    text_boxes = @($textBoxes.ToArray())
    all_within_safe_margin = $true
    title_clear_of_badge = $true
    boxes_disjoint = $true
  })

  Write-Output ("  {0}  title {1}px/{2} line(s)   speaker {3}px/{4} line(s)   {5} {6}   dsl={7} B" -f `
    $cid, $tr.size, $tr.count, $sr.size, $sr.count, $sts, $smeta.sym, (Get-Item $outPath).Length)
}

# ------------------------------------------------------------- shared tokens --
$shared = [pscustomobject][ordered]@{
  canvas = [pscustomobject]@{ width = $W; height = $H; safe_margin = $M }
  palette = [pscustomobject]@{
    background = $BG; hairline = $LINE; text_primary = $INK; text_secondary = $MUTED
    primary = $PRIMARY; accent = $AMBER; pill_text = $PILLINK; cancel_note = $CANCELINK
    note = 'Identical on all eight cards - only the status colour changes, and only through the status system.'
  }
  brand = [pscustomobject]@{ string = $BRAND; box = [pscustomobject]@{ x = 96; y = $BRAND_Y; width = 520; height = 24 }; mark = [pscustomobject]@{ x1 = 40; x2 = 64; y = $MARK_Y; size = 20 } }
  date = [pscustomobject]@{ string = $DATEL; align = 'END'; right_edge = ($W - $M); row = 'top-aligned with the per-card speaker row'; per_card_box = 'see each card record.date_box' }
  title_zone = [pscustomobject]@{ top = $TITLE_TOP; bottom = $ZONE_BOT; height = $ZONE_H; left = 40; width = $TITLE_W; align = 'START'; vertical_align = 'centred'; size_ladder = @($TITLE_LADDER); line_height_ratio = $LEAD; min_size = 36; max_lines = 3 }
  footer = [pscustomobject]@{ anchor = 'bottom'; speaker_row_bottom = ($H - $M); time_row_gap = $FOOT_GAP; time_font_size = $TIME_FS; cancel_note_row = 'time row, right column, K06 only'; top_margin = $M; bottom_margin = $M }
  speaker_zone = [pscustomobject]@{ anchor = 'block bottom on the safe line'; left = 40; width = $SPK_W; size_ladder = @($SPK_LADDER); min_size = 22; max_lines = 2 }
  badge = [pscustomobject]@{ y = $BADGE_Y; height = $BADGE_H; font_size = $BADGE_FS; padding = $BADGE_PAD; width = $pillW; right_edge = ($W - $M) }
  divider = [pscustomobject]@{ y = $DIV_Y; head_width = $DIV1_W; x = 40 }
  fonts = [pscustomobject]@{ prose = $FAM; numeric = $MONO; source = 'GET /fonts (shared suite response, tmp/run-20261002-220723-mimo/A11/fonts-0001.txt)' }
  measurement = [pscustomobject]@{
    method = 'per-class advance estimate in em, converted to px'
    cjk_fullwidth_em = 1.0; cjk_pad = 1.05
    latin_note = 'upper .74 lower/digit .58 space .30 other ascii .40 latin1 .55 mono .62 em'
    latin_pad = 1.10
    purpose = 'keeps every emitted line inside its box without scaling the card'
  }
}

$statusSystem = @()
foreach ($k in $STATUS.Keys) {
  $s = $STATUS[$k]
  $statusSystem += [pscustomobject][ordered]@{
    status = $k; symbol = $s.sym; symbol_codepoint = $s.code; color = $s.color
    label = ($s.sym + ' ' + $k)
    encoded_by = @('color', 'symbol', 'text')
  }
}

$layoutDoc = [pscustomobject][ordered]@{
  schema_version = 1
  task_id = 'A14'
  run_id = $RUN
  generator = ("tmp/$RUN/A14/gen.ps1 -Ver " + $Ver)
  generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  timezone = 'Asia/Shanghai (UTC+08:00)'
  source = 'tasks/A14-content-stress-batch/inputs/cards.json'
  shared = $shared
  status_system = $statusSystem
  badge_probe = [pscustomobject]@{ dsl = ("tmp/$RUN/A14/probe-badges-v$Ver.snapshot"); pills = @($probeRecs); width = $probeW; height = 160 }
  cards = @($layout.ToArray())
}
$layoutPath = "$TMP\layout-v$Ver.json"
[IO.File]::WriteAllText($layoutPath, ($layoutDoc | ConvertTo-Json -Depth 14), [Text.UTF8Encoding]::new($false))

Write-Output "written:"
Write-Output ("  " + $probePath + "  bytes=" + (Get-Item $probePath).Length)
Write-Output ("  " + $layoutPath + "  bytes=" + (Get-Item $layoutPath).Length)
Write-Output ("cards={0}  pill_width={1}  probe_width={2}" -f $layout.Count, $pillW, $probeW)
