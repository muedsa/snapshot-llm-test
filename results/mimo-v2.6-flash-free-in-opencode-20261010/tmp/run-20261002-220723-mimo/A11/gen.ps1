param([int]$Ver = 1)

# ---------------------------------------------------------------- A11 gen ----
# Builds both 1200x1600 invoice pages from inputs/invoice.json.
# - every string is emitted as <Raw><![CDATA[...]]></Raw>
#   * Raw   -> text is NOT trimmed, so leading/double spaces survive
#   * CDATA -> the parser does NOT decode HTML entities (documented), so < > & must be CDATA
# - all money is integer cents, rounded half up to the cent
# - every amount is a monospace END-aligned box with right edge x=1136;
#   all of them carry exactly 2 decimals -> one single decimal-point column

$ErrorActionPreference = 'Stop'
[System.Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[System.Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root

$TMP = "$root\tmp\$RUN\A11"
New-Item -ItemType Directory -Force -Path $TMP | Out-Null

# ------------------------------------------------------------- input / math --
$inv = Get-Content "$root\tasks\A11-bilingual-invoice\inputs\invoice.json" -Raw -Encoding UTF8 | ConvertFrom-Json

function ToCents([string]$s) {
  $t = $s.Trim(); $neg = $false
  if ($t.StartsWith('-')) { $neg = $true; $t = $t.Substring(1) }
  $p = $t.Split('.')
  $i = [int64]$p[0]; $fr = [int64]0
  if ($p.Count -gt 1) {
    $f = $p[1]
    if ($f.Length -gt 2) { throw "more than 2 decimals in input: $s" }
    $fr = [int64]($f.PadRight(2, '0'))
  }
  $c = ($i * 100) + $fr
  if ($neg) { return -$c }
  return $c
}

function Fmt([int64]$c) {
  $neg = $c -lt 0
  $a = [math]::Abs($c)
  $s = '{0}.{1:D2}' -f [int64][math]::Floor($a / 100), [int64]($a % 100)
  if ($neg) { return '-' + $s }
  return $s
}

function RoundHalfUp([int64]$num, [int64]$den) {
  $neg = (($num -lt 0) -xor ($den -lt 0))
  $n = [math]::Abs([double]$num); $d = [math]::Abs([double]$den)
  $q = [int64][math]::Floor($n / $d)
  $r = $n - ($q * $d)
  if (($r * 2) -ge $d) { $q = $q + 1 }
  if ($neg) { return -$q }
  return $q
}

$discountC = ToCents $inv.discount
$shipC     = ToCents $inv.shipping
$ratePct   = [int64](ToCents $inv.tax_rate)   # 0.06 -> 6  => 6/100

$lines = @(); $subtotalC = [int64]0
foreach ($it in $inv.items) {
  $unitC = ToCents $it.unit_price
  $amtC  = [int64]($unitC * [int64]$it.quantity)
  $lines += [pscustomobject]@{
    sku = $it.sku; name = $it.name; quantity = [int]$it.quantity
    unit_price = $it.unit_price; unit_cents = $unitC
    line_cents = $amtC; line_amount = (Fmt $amtC)
  }
  $subtotalC = $subtotalC + $amtC
}
$taxBaseC    = $subtotalC - $discountC
$taxExactNum = $taxBaseC * $ratePct                    # cents * percent
$taxC        = RoundHalfUp $taxExactNum ([int64]100)   # -> cents
$payableC    = $taxBaseC + $taxC + $shipC

# taxExactNum = tax_base_cents * rate_percent  =>  /10000 = currency units
$taxExactText = [string]([decimal]::new($taxExactNum) / [decimal]10000)
$subtotalTxt = Fmt $subtotalC; $discountTxt = Fmt $discountC; $baseTxt = Fmt $taxBaseC
$taxTxt = Fmt $taxC; $shipTxt = Fmt $shipC; $payTxt = Fmt $payableC

# ------------------------------------------------------------------ palette --
$INK='#111827'; $SUB='#6B7280'; $MUTE='#9CA3AF'; $LINE='#E5E7EB'; $LINE2='#F1F5F9'
$CARD='#F8FAFC'; $WHITE='#FFFFFF'; $GRNBG='#ECFDF5'; $GRNBD='#10B981'
$GREEN='#16A34A'; $GRAY='#9CA3AF'; $DARK='#111827'
$FAM  = 'Noto Sans CJK SC,Noto Sans CJK JP'
$MONO = 'Noto Sans Mono CJK SC'
$RIGHT = 1136

# ------------------------------------------------------------ emit machinery --
$P1   = New-Object System.Collections.Generic.List[string]
$P2   = New-Object System.Collections.Generic.List[string]
$Segs = New-Object System.Collections.Generic.List[object]

function Guard([string]$s) { if ($s -and $s.Contains(']]>')) { throw "CDATA terminator in input: $s" } }

function EmitText([int]$Page,[string]$Id,[int]$X,[int]$Y,[int]$W,[string]$Text,[string]$Fam,[int]$Fs,[string]$Style,[string]$Col,[string]$Align,[string]$Kind,[string]$Source) {
  Guard $Text
  $st = ''
  if ($Style -ne '') { $st = ' fontStyle="' + $Style + '"' }
  $node = '<Positioned left="' + $X + '" top="' + $Y + '" width="' + $W + '"><Text fontFamily="' + $Fam + '" fontSize="' + $Fs + '" color="' + $Col + '"' + $st + ' textAlign="' + $Align + '" height="1.0"><Raw><![CDATA[' + $Text + ']]></Raw></Text></Positioned>'
  if ($Page -eq 1) { [void]$P1.Add($node) } else { [void]$P2.Add($node) }
  [void]$Segs.Add([pscustomobject]@{
    page=$Page; id=$Id; kind=$Kind; source=$Source; x=$X; y=$Y; width=$W; height=$Fs
    text=$Text; fontFamily=$Fam; fontSize=$Fs; fontStyle=$Style; color=$Col
    textAlign=$Align; encoding='Raw+CDATA'
  })
}

function EmitBox([int]$Page,[string]$Id,[int]$X,[int]$Y,[int]$W,[int]$H,[string]$Col,[string]$Border,[int]$Radius) {
  $b=''; if ($Border -ne '') { $b = ' border="' + $Border + '"' }
  $r=''; if ($Radius -gt 0)  { $r = ' borderRadius="' + $Radius + '"' }
  $node = '<Positioned left="' + $X + '" top="' + $Y + '" width="' + $W + '" height="' + $H + '"><Container width="' + $W + '" height="' + $H + '" color="' + $Col + '"' + $b + $r + '/></Positioned>'
  if ($Page -eq 1) { [void]$P1.Add($node) } else { [void]$P2.Add($node) }
}

function EmitRich([int]$Page,[string]$Id,[int]$X,[int]$Y,[int]$W,[int]$Fs,[string]$Fam) {
  $node = '<Positioned left="' + $X + '" top="' + $Y + '" width="' + $W + '"><Text fontFamily="' + $Fam + '" fontSize="' + $Fs + '" textAlign="START" height="1.0"><Text color="' + $GREEN + '" fontStyle="BOLD"><![CDATA[PAID]]></Text><Raw color="' + $GRAY + '"><![CDATA[ / ]]></Raw><Text color="' + $DARK + '" fontStyle="BOLD"><![CDATA[已结算]]></Text></Text></Positioned>'
  [void]$P2.Add($node)
  [void]$Segs.Add([pscustomobject]@{
    page=$Page; id=$Id; kind='body'; source='TASK.md rich-text status specimen (must not change the amount due)'
    x=$X; y=$Y; width=$W; height=$Fs; text='PAID / 已结算'
    fontFamily=$Fam; fontSize=$Fs; fontStyle='BOLD'; color=$GREEN
    textAlign='START'; encoding='inline spans inside one Text -> shared baseline'
    spans=@(
      [pscustomobject]@{ text='PAID'; color=$GREEN; style='BOLD'; tag='Text' },
      [pscustomobject]@{ text=' / ';  color=$GRAY;  raw=$true;    tag='Raw'  },
      [pscustomobject]@{ text='已结算'; color=$DARK; style='BOLD'; tag='Text' }
    )
  })
}

function EmitHeader([int]$Pg) {
  # +4 px on all four header runs: with height="1.0" the glyph box overhangs the
  # positioned box by ~0.075em, so at y=48 the 40 px title produced ink at y=45,
  # breaking the 48 px safe margin. At y=52 the ink starts at y=49.
  EmitText $Pg 'hdr-title' 48 52 620  '结算单  INVOICE' $FAM 40 'BOLD' $INK  'START' 'body' 'layout label'
  EmitText $Pg 'hdr-sub'   48 104 640 ($script:inv.seller + '  →  ' + $script:inv.buyer) $FAM 26 '' $SUB 'START' 'body' 'inputs/invoice.json seller + buyer'
  EmitText $Pg 'hdr-id'    700 63 452 $script:inv.invoice_id $MONO 28 'BOLD' $INK 'END' 'body' 'inputs/invoice.json invoice_id'
  EmitText $Pg 'hdr-date'  700 104 452 ($script:inv.issued + '  ·  ' + $script:inv.currency) $MONO 26 '' $SUB 'END' 'body' 'inputs/invoice.json issued + currency'
  EmitBox  $Pg 'hdr-rule' 48 146 1104 2 $LINE '' 0
}

function EmitFooter([int]$Pg,[int]$PageNo) {
  EmitText $Pg 'foot-left' 48 1496 780 ($script:inv.seller + '  ·  ' + $script:inv.buyer + '  ·  ' + $script:inv.currency) $FAM 20 '' $MUTE 'START' 'footnote' 'inputs/invoice.json seller + buyer + currency'
  EmitText $Pg 'foot-page' 852 1496 300 ('第 ' + $PageNo + ' 页 / 共 2 页') $FAM 24 '' $INK 'END' 'body' 'layout label'
}

# =============================================================== PAGE 1 ======
EmitHeader 1

EmitBox 1 'card-seller' 48 174 540 130 $CARD '1 SOLID #E5E7EB' 12
EmitBox 1 'card-buyer' 612 174 540 130 $CARD '1 SOLID #E5E7EB' 12
EmitText 1 'lbl-seller' 76 200 440 '卖方 / SELLER' $FAM 24 '' $SUB 'START' 'body' 'layout label'
EmitText 1 'val-seller' 76 244 496 $inv.seller $FAM 32 'BOLD' $INK 'START' 'body' 'inputs/invoice.json seller'
EmitText 1 'lbl-buyer' 640 200 440 '买方 / BUYER' $FAM 24 '' $SUB 'START' 'body' 'layout label'
EmitText 1 'val-buyer' 640 244 496 $inv.buyer $FAM 32 'BOLD' $INK 'START' 'body' 'inputs/invoice.json buyer'

$mx = @(48, 324, 600, 876)
$ml = @('编号', '开票日期', '币种', '税率')
$mv = @($inv.invoice_id, $inv.issued, $inv.currency, ($ratePct.ToString() + '%'))
for ($i = 0; $i -lt 4; $i++) {
  EmitText 1 ('meta-l-' + $i) $mx[$i] 340 270 $ml[$i] $FAM 24 '' $SUB 'START' 'body' 'layout label'
  EmitText 1 ('meta-v-' + $i) $mx[$i] 376 270 $mv[$i] $MONO 30 'BOLD' $INK 'START' 'body' 'inputs/invoice.json field'
}
EmitBox 1 'rule-meta' 48 436 1104 2 $LINE '' 0

EmitText 1 'th-sku'   64  478 170 'SKU'        $FAM 24 '' $SUB 'START' 'body' 'layout label'
EmitText 1 'th-name'  250 478 470 '品名 / Name' $FAM 24 '' $SUB 'START' 'body' 'layout label'
EmitText 1 'th-qty'   736 478 64  '数量'        $FAM 24 '' $SUB 'END'   'body' 'layout label'
EmitText 1 'th-price' 816 478 140 '单价'        $FAM 24 '' $SUB 'END'   'body' 'layout label'
EmitText 1 'th-amt'   976 478 160 '行金额'      $FAM 24 '' $SUB 'END'   'body' 'layout label'
EmitBox 1 'th-rule' 48 516 1104 2 $LINE '' 0

for ($i = 0; $i -lt $lines.Count; $i++) {
  $bt = 522 + ($i * 84); $cy = $bt + 29; $L = $lines[$i]
  EmitText 1 ('cell-sku-'  + $i) 64  $cy 170 $L.sku        $MONO 26 ''         $INK 'START' 'body' ('inputs/invoice.json items[' + $i + '].sku')
  EmitText 1 ('cell-name-' + $i) 250 $cy 470 $L.name       $FAM  26 ''         $INK 'START' 'body' ('inputs/invoice.json items[' + $i + '].name')
  EmitText 1 ('cell-qty-'  + $i) 736 $cy 64  ($L.quantity.ToString()) $MONO 26 '' $INK 'END' 'body' ('inputs/invoice.json items[' + $i + '].quantity')
  EmitText 1 ('cell-unit-' + $i) 816 $cy 140 $L.unit_price $MONO 26 ''         $INK 'END'   'body' ('inputs/invoice.json items[' + $i + '].unit_price')
  EmitText 1 ('cell-amt-'  + $i) 976 $cy 160 $L.line_amount $MONO 26 'BOLD'   $INK 'END'   'body' ('computed: quantity x unit_price = ' + $L.line_amount)
  EmitBox 1 ('row-div-' + $i) 48 ($bt + 84) 1104 1 $LINE2 '' 0
}

EmitBox 1 'ledger-card' 48 902 1104 444 $WHITE '1 SOLID #E5E7EB' 12
EmitText 1 'ledger-head' 80 930 520 '结算明细  SETTLEMENT' $FAM 24 '' $SUB 'START' 'body' 'layout label'
# full card width (48..1151), not an inset pill: the previous 64..1135 inset put the
# band's right border on top of the amount, whose ink ends at x=1134 and touched it.
# A full-bleed row keeps the text at exactly the same place as every other ledger row
# (label x=80, amount right edge x=1136) and leaves the digits 17 px of clearance.
EmitBox 1 'pay-band' 48 1274 1104 52 $GRNBG '1 SOLID #10B981' 0

$totL = @('货品小计', '折扣', '税前货品额', '税额 (6%)', '运费', '应付')
$totV = @($subtotalTxt, ('-' + $discountTxt), $baseTxt, $taxTxt, $shipTxt, $payTxt)
for ($i = 0; $i -lt 6; $i++) {
  $ry = 976 + ($i * 62); $st = ''
  if ($i -eq 5) { $st = 'BOLD' }
  EmitText 1 ('tot-l-' + $i) 80  $ry 500 $totL[$i] $FAM  26 $st $INK 'START' 'body' 'TASK.md required total label'
  EmitText 1 ('tot-v-' + $i) 920 $ry 216 $totV[$i] $MONO 26 $st $INK 'END'   'body' 'computed from inputs/invoice.json (integer cents, round half up)'
  if ($i -lt 5) { EmitBox 1 ('tot-div-' + $i) 80 ($ry + 44) 1056 1 $LINE2 '' 0 }
}
EmitFooter 1 1

# =============================================================== PAGE 2 ======
EmitHeader 2

EmitText 2 'sec-title' 48 180 760 '备注与原样文字' $FAM 36 'BOLD' $INK 'START' 'body' 'layout label'
EmitText 2 'sec-sub'   48 230 760 'NOTES & LITERAL LINES' $FAM 24 '' $SUB 'START' 'body' 'layout label'
EmitBox  2 'rule-sec' 48 270 1104 2 $LINE '' 0

EmitText 2 'notes-head' 48 302 520 'NOTES' $FAM 24 '' $SUB 'START' 'body' 'layout label'
for ($i = 0; $i -lt $inv.notes.Count; $i++) {
  $ny = 346 + ($i * 76)
  EmitText 2 ('note-n-' + $i) 48  $ny 44   (($i + 1).ToString() + '.') $MONO 26 '' $SUB 'START' 'body' 'layout label'
  EmitText 2 ('note-t-' + $i) 104 $ny 1048 $inv.notes[$i] $FAM 26 '' $INK 'START' 'body' ('inputs/invoice.json notes[' + $i + ']')
}
EmitBox 2 'rule-notes' 48 642 1104 2 $LINE '' 0

EmitText 2 'lit-head' 48 674 640 'LITERAL LINES' $FAM 24 '' $SUB 'START' 'body' 'layout label'
for ($i = 0; $i -lt $inv.literal_lines.Count; $i++) {
  $by = 718 + ($i * 98)
  EmitBox 2 ('lit-box-' + $i) 48 $by 1104 84 $CARD '1 SOLID #E5E7EB' 8
  EmitText 2 ('lit-n-' + $i) 76  ($by + 28) 60  ('L' + ($i + 1).ToString()) $MONO 28 '' $MUTE 'START' 'body' 'layout label'
  EmitText 2 ('lit-t-' + $i) 140 ($by + 28) 980 $inv.literal_lines[$i] $MONO 28 '' $INK 'START' 'body' ('inputs/invoice.json literal_lines[' + $i + '] verbatim')
}
EmitBox 2 'rule-lit' 48 1140 1104 2 $LINE '' 0

EmitText 2 'stat-head' 48 1172 640 'STATUS MARK' $FAM 24 '' $SUB 'START' 'body' 'layout label'
EmitRich 2 'stat-line' 48 1218 700 72 $FAM
EmitText 2 'stat-cap' 48 1336 900 ('应付金额（与第 1 页一致）：' + $inv.currency + ' ' + $payTxt) $FAM 26 '' $INK 'START' 'body' 'computed payable, identical to page 1'
EmitFooter 2 2

# ------------------------------------------------------------------ assemble --
function Build([System.Collections.Generic.List[string]]$Nodes) {
  $sb = New-Object System.Text.StringBuilder
  [void]$sb.Append('<Snapshot type="png" background="#FFFFFF">')
  [void]$sb.Append('<Container width="1200" height="1600" color="#FFFFFF"><Stack>')
  foreach ($n in $Nodes) { [void]$sb.Append($n) }
  [void]$sb.Append('</Stack></Container></Snapshot>')
  return $sb.ToString()
}

$utf8 = [System.Text.UTF8Encoding]::new($false)
$v = $Ver.ToString('00')
$f1 = "$TMP\invoice-page-01-v$v.snapshot"
$f2 = "$TMP\invoice-page-02-v$v.snapshot"
[System.IO.File]::WriteAllText($f1, (Build $P1), $utf8)
[System.IO.File]::WriteAllText($f2, (Build $P2), $utf8)

$meta = [pscustomobject]@{
  version = "v$v"
  generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss.fffzzz')
  input = 'tasks/A11-bilingual-invoice/inputs/invoice.json'
  page1_file = ("tmp/$RUN/A11/invoice-page-01-v$v.snapshot")
  page2_file = ("tmp/$RUN/A11/invoice-page-02-v$v.snapshot")
  computation = [pscustomobject]@{
    method = 'integer cents, ROUND_HALF_UP to 0.01'
    order = @('line = quantity * unit_price (exact, 2-dp inputs)',
              'subtotal = sum(line)',
              'tax_base = subtotal - discount',
              'tax = round_half_up(tax_base * rate / 100)',
              'payable = tax_base + tax + shipping')
    lines = $lines
    subtotal_cents = $subtotalC; discount_cents = $discountC; tax_base_cents = $taxBaseC
    tax_numerator = $ratePct; tax_denominator = 100
    tax_exact = $taxExactText; tax_rounded_cents = $taxC
    shipping_cents = $shipC; payable_cents = $payableC
    subtotal = $subtotalTxt; discount = $discountTxt; tax_base = $baseTxt
    tax = $taxTxt; shipping = $shipTxt; payable = $payTxt
  }
  segments = $Segs
}
[System.IO.File]::WriteAllText("$TMP\segments-v$v.json", ($meta | ConvertTo-Json -Depth 8), $utf8)

"written:"
"  $f1  bytes=" + (Get-Item $f1).Length
"  $f2  bytes=" + (Get-Item $f2).Length
"  segments-v$v.json  bytes=" + (Get-Item "$TMP\segments-v$v.json").Length
"line items:"
foreach ($L in $lines) { "  {0,-10} {1,-38} {2,3} x {3,-8} = {4}" -f $L.sku, $L.name, $L.quantity, $L.unit_price, $L.line_amount }
"subtotal=$subtotalTxt discount=$discountTxt base=$baseTxt tax_exact=$taxExactText tax=$taxTxt ship=$shipTxt payable=$payTxt"
