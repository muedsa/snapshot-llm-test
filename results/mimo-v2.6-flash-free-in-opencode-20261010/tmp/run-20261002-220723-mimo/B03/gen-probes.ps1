# B03 capability probes: generate 10 small probe DSLs, render each through the real service.
$ErrorActionPreference = 'Stop'
$tmp = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\B03')
$rend = Join-Path $tmp 'render-b03.ps1'
$log  = Join-Path $tmp 'requests.jsonl'
$pdir = Join-Path $tmp 'probes'
if (!(Test-Path $pdir)) { New-Item -ItemType Directory -Force -Path $pdir | Out-Null }

$probes = @{}

$probes['p01-stroke-text'] = @'
<Snapshot type="png" background="#0B1020">
<Container width="800" height="440" color="#0B1020" padding="(40,40)">
<Column>
<Text fontFamily="Inter Black" fontSize="84" color="#F2C14E" letterSpacing="2" textShadow="0 6 18 #00000099,-4 -3 #E4622C88">OUTLINE</Text>
<Text fontFamily="Inter Black" fontSize="84" color="transparent" letterSpacing="2" foregroundColor="#7FD4C1" foregroundMode="STROKE" foregroundStrokeWidth="2">OUTLINE</Text>
<Text fontFamily="Inter Black" fontSize="76" color="#12303A" letterSpacing="2" foregroundColor="#E4622C" foregroundMode="STROKE_AND_FILL" foregroundStrokeWidth="6">FILLSTROKE</Text>
<Text fontFamily="Inter" fontSize="22" color="#9FB3C8">STROKE probe / textShadow multi / letterSpacing</Text>
</Column>
</Container>
</Snapshot>
'@

$probes['p02-backdrop-filter'] = @'
<Snapshot type="png" background="#0E1A2B">
<Container width="800" height="400" color="#0E1A2B">
<Stack clipBehavior="NONE">
<Positioned left="0" top="0" width="800" height="400">
<Container width="800" height="400" gradientType="RADIAL" gradientColors="#FF6B35,#2EC4B6,#1B3A5C,#0B1020" gradientStops="0,0.4,0.75,1" gradientCenter="TOP_LEFT" gradientRadius="1"/>
</Positioned>
<Positioned left="150" top="110" width="150" height="150"><Container width="150" height="150" shape="CIRCLE" color="#FFD166"/></Positioned>
<Positioned left="470" top="210" width="240" height="130"><Container width="240" height="130" borderRadius="20" color="#EF476F"/></Positioned>
<Positioned left="80" top="40" width="16" height="330"><Container width="16" height="330" color="#FFFFFFAA"/></Positioned>
<Positioned left="80" top="150" width="420" height="180">
<ClipRRect borderRadius="28">
<Container width="420" height="180" color="#FFFFFF1A">
<BackdropFilter sigmaX="14" sigmaY="14">
<Container width="420" height="180" color="#FFFFFF14"/>
</BackdropFilter>
</Container>
</ClipRRect>
</Positioned>
<Positioned left="110" top="182" width="360" height="116">
<Text fontFamily="Inter" fontSize="20" color="#FFFFFF">FROSTED / BackdropFilter sigma 14</Text>
</Positioned>
</Stack>
</Container>
</Snapshot>
'@

$probes['p03-color-filtered'] = @'
<Snapshot type="png">
<Container width="800" height="420" color="#F5EFE2">
<Stack>
<Positioned left="0" top="0" width="800" height="420"><Container width="800" height="420" color="#F5EFE2"/></Positioned>
<Positioned left="60" top="60" width="300" height="300"><Container width="300" height="300" color="#2E6FB7"/></Positioned>
<Positioned left="440" top="60" width="300" height="300"><Container width="300" height="300" color="#E4622C"/></Positioned>
<Positioned left="230" top="140" width="340" height="140">
<ColorFiltered color="#0B3B3A" blendMode="MULTIPLY">
<Column>
<Container width="340" height="46" color="#FFD166"/>
<Container width="340" height="46" color="#00000000"/>
<Container width="340" height="46" color="#06D6A0"/>
</Column>
</ColorFiltered>
</Positioned>
<Positioned left="60" top="374" width="680" height="30">
<Text fontFamily="Inter" fontSize="18" color="#5B5647">MULTIPLY band across blue / paper / orange + transparent gap</Text>
</Positioned>
</Stack>
</Container>
</Snapshot>
'@

$probes['p04-image-filtered'] = @'
<Snapshot type="png" background="#08090D">
<Container width="800" height="400" color="#08090D">
<Stack clipBehavior="NONE">
<Positioned left="0" top="150" width="800" height="120">
<ImageFiltered sigmaX="40" sigmaY="1">
<Column>
<Container width="800" height="24" color="#E4622C"/>
<Container width="640" height="24" color="#FFD166"/>
<Container width="720" height="24" color="#06D6A0"/>
<Container width="500" height="24" color="#4CC9F0"/>
</Column>
</ImageFiltered>
</Positioned>
<Positioned left="60" top="44" width="680" height="90">
<Text fontFamily="Inter Black" fontSize="64" color="#FFFFFF">2:03.418</Text>
</Positioned>
<Positioned left="60" top="310" width="680" height="40">
<Text fontFamily="Inter" fontSize="20" color="#8892A6">ImageFiltered sigmaX=40 sigmaY=1 (anisotropic)</Text>
</Positioned>
</Stack>
</Container>
</Snapshot>
'@

$probes['p05-widget-span'] = @'
<Snapshot type="png">
<Container width="800" height="360" color="#FFFDF7" padding="48">
<Text fontFamily="Noto Sans CJK SC" fontSize="25" color="#1C1C1C" height="1.8">
<Raw>观测记录里，时间一律写作 </Raw><WidgetSpan alignment="MIDDLE"><Container width="176" height="34" color="#0B3B3A" borderRadius="17" alignment="CENTER"><Text fontFamily="Noto Sans Mono CJK SC" fontSize="17" color="#7FD4C1">06:30-08:00</Text></Container></WidgetSpan><Raw> ，鸟种用 </Raw><WidgetSpan alignment="MIDDLE"><Container width="52" height="34" color="#E4622C" borderRadius="17" alignment="CENTER"><Text fontFamily="Inter" fontSize="18" color="#FFFFFF">03</Text></Container></WidgetSpan><Raw> 这样的两位代码，数量字段一律右对齐，合计与明细必须相等。</Raw>
</Text>
</Container>
</Snapshot>
'@

$probes['p06-stack-shadow'] = @'
<Snapshot type="png" background="#E9ECEF">
<Container width="800" height="360" color="#E9ECEF">
<Row>
<Container width="400" height="360" padding="(40,40)">
<Column>
<SizedBox width="320" height="200">
<Stack>
<Positioned left="40" top="20" width="240" height="150"><Container width="240" height="150" borderRadius="18" color="#FFFFFF" boxShadow="0 16 26 0 #00000059"/></Positioned>
</Stack>
</SizedBox>
<Text fontFamily="Inter" fontSize="15" color="#495057">DEFAULT STACK CLIP</Text>
</Column>
</Container>
<Container width="400" height="360" padding="(40,40)">
<Column>
<SizedBox width="320" height="200">
<Stack clipBehavior="NONE">
<Positioned left="40" top="20" width="240" height="150"><Container width="240" height="150" borderRadius="18" color="#FFFFFF" boxShadow="0 16 26 0 #00000059"/></Positioned>
</Stack>
</SizedBox>
<Text fontFamily="Inter" fontSize="15" color="#495057">clipBehavior NONE</Text>
</Column>
</Container>
</Row>
</Container>
</Snapshot>
'@

$probes['p07-gradient-tile'] = @'
<Snapshot type="png">
<Container width="800" height="400" color="#0B3B3A">
<Stack>
<Positioned left="0" top="0" width="400" height="400">
<Container width="400" height="400" gradientType="LINEAR" gradientColors="#E4622C,#0B3B3A" gradientStops="0,0.5" gradientTileMode="REPEAT" gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT" gradientRotation="0.7853982"/>
</Positioned>
<Positioned left="400" top="0" width="400" height="400">
<Container width="400" height="400" gradientType="RADIAL" gradientColors="#7FD4C1,#0B3B3A" gradientStops="0,0.35" gradientTileMode="MIRROR" gradientCenter="CENTER" gradientRadius="0.22"/>
</Positioned>
<Positioned left="20" top="360" width="360" height="26">
<Text fontFamily="Inter" fontSize="16" color="#FFFFFF">LINEAR REPEAT + rotation</Text>
</Positioned>
<Positioned left="420" top="360" width="360" height="26">
<Text fontFamily="Inter" fontSize="16" color="#FFFFFF">RADIAL MIRROR</Text>
</Positioned>
</Stack>
</Container>
</Snapshot>
'@

$probes['p08-font-features'] = @'
<Snapshot type="png" background="#FFFFFF">
<Container width="900" height="320" color="#FFFFFF" padding="(24,30)">
<Column>
<Text fontFamily="Inter" fontSize="40" color="#111111">1111 8888 0000</Text>
<Text fontFamily="Inter" fontSize="40" color="#111111" fontFeatures="+tnum">1111 8888 0000</Text>
<Text fontFamily="Noto Sans Mono CJK SC" fontSize="40" color="#111111">1111 8888 0000</Text>
<Text fontFamily="Inter" fontSize="40" color="#E4622C" fontFeatures="+tnum">2026-10-06 09:41</Text>
<Text fontFamily="Inter" fontSize="15" color="#6B7280">row1 default / row2 +tnum / row3 mono / row4 +tnum digits</Text>
</Column>
</Container>
</Snapshot>
'@

$probes['p09-overflow-bleed'] = @'
<Snapshot type="png" background="#F2F4F7">
<Container width="700" height="300" color="#F2F4F7">
<Stack>
<Positioned left="0" top="0" width="700" height="300">
<SizedBox width="700" height="300">
<ClipRect>
<SizedOverflowBox width="700" height="300" alignment="BOTTOM_LEFT">
<Text fontFamily="Inter Black" fontSize="400" color="#E4622C">FOLD</Text>
</SizedOverflowBox>
</ClipRect>
</SizedBox>
</Positioned>
<Positioned left="20" top="16" width="400" height="26">
<Text fontFamily="Inter" fontSize="16" color="#3B4252">SizedOverflowBox + ClipRect</Text>
</Positioned>
</Stack>
</Container>
</Snapshot>
'@

$probes['p10-axonic-matrix'] = @'
<Snapshot type="png" background="#F7F3EA">
<Container width="600" height="600" color="#F7F3EA">
<Transform matrix="(0.8660254,0.5,0,0,-0.8660254,0.5,0,0,0,0,1,0,300,60,0,1)">
<Column>
<Row><Container width="60" height="60" color="#0B3B3A"/><Container width="60" height="60" color="#7FD4C1"/><Container width="60" height="60" color="#0B3B3A"/><Container width="60" height="60" color="#7FD4C1"/><Container width="60" height="60" color="#0B3B3A"/></Row>
<Row><Container width="60" height="60" color="#E4622C"/><Container width="60" height="60" color="#FFF3E0"/><Container width="60" height="60" color="#0B3B3A"/><Container width="60" height="60" color="#FFF3E0"/><Container width="60" height="60" color="#E4622C"/></Row>
<Row><Container width="60" height="60" color="#7FD4C1"/><Container width="60" height="60" color="#0B3B3A"/><Container width="60" height="60" color="#FFD166"/><Container width="60" height="60" color="#0B3B3A"/><Container width="60" height="60" color="#7FD4C1"/></Row>
<Row><Container width="60" height="60" color="#FFF3E0"/><Container width="60" height="60" color="#E4622C"/><Container width="60" height="60" color="#FFF3E0"/><Container width="60" height="60" color="#E4622C"/><Container width="60" height="60" color="#FFF3E0"/></Row>
<Row><Container width="60" height="60" color="#0B3B3A"/><Container width="60" height="60" color="#7FD4C1"/><Container width="60" height="60" color="#0B3B3A"/><Container width="60" height="60" color="#7FD4C1"/><Container width="60" height="60" color="#0B3B3A"/></Row>
</Column>
</Transform>
</Container>
</Snapshot>
'@

$results = @()
foreach ($name in ($probes.Keys | Sort-Object)) {
  $dsl = Join-Path $pdir ($name + '.snapshot')
  $png = Join-Path $pdir ($name + '.png')
  [IO.File]::WriteAllText($dsl, $probes[$name].Trim() + "`r`n", (New-Object Text.UTF8Encoding($false)))
  $rid = 'B03-' + $name
  & $rend -DslPath $dsl -OutPath $png -TaskId 'B03' -ReqId $rid -CaseId $null -LogPath $log | Out-Null
  $sz = if (Test-Path $png) { (Get-Item $png).Length } else { 0 }
  $results += ("{0} -> {1} bytes" -f $name, $sz)
}
$results
