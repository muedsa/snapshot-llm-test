$ErrorActionPreference = 'Stop'
$tmp = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\B03')
$enc = New-Object System.Text.UTF8Encoding($false)
$reqLog = Join-Path $tmp 'requests.jsonl'
$iterLog = Join-Path $tmp 'iterations.jsonl'

$reqs = @()
Get-Content $reqLog -Encoding UTF8 | ForEach-Object { $reqs += ($_ | ConvertFrom-Json) }

function Req([string]$rid, [int]$wantStatus) {
  foreach ($r in $reqs) { if ($r.id -eq $rid -and $r.http_status -eq $wantStatus) { return $r } }
  throw ("request not found: {0} status {1}" -f $rid, $wantStatus)
}

$plan = @(
  # ---- baselines (round 1) ----
  @{ n='c03-r1'; case='case-03'; type='baseline'; ver='v1'; rid='B03-case-03-r1'; st=200
     ch='首版 1600x640 音乐节票根（ColorFiltered 双色套印为主导技术）'
     ob='渲染成功，字节与日志一致，尺寸 1600x640 与 DSL 一致'
     rs='首版成立，进入视觉迭代'
     vw=$true; ve='读图 outputs/.../B03/case-03/final.png：票面结构与套印错位成立' }
  @{ n='c04-r1'; case='case-04'; type='baseline'; ver='v1'; rid='B03-case-04-r1'; st=200
     ch='首版 1920x1080 圈速板（ImageFiltered 各向异性模糊为主导技术）'
     ob='语法修复后渲染成功，字节 218985 与日志一致，尺寸 1920x1080 与 DSL 一致'
     rs='首版成立，进入视觉迭代'
     vw=$true; ve='读图 outputs/.../B03/case-04/final.png：条纹与大字时间成立' }
  @{ n='c05-r1'; case='case-05'; type='baseline'; ver='v1'; rid='B03-case-05-r1'; st=200
     ch='首版 1000x1414 城市鸟类图鉴内页（行内 WidgetSpan 为主导技术）'
     ob='渲染成功，字节 141209 与日志一致，尺寸 1000x1414 与 DSL 一致'
     rs='首版成立，进入视觉迭代'
     vw=$true; ve='读图 outputs/.../B03/case-05/final.png：行内徽章与正文基线对齐' }
  @{ n='c06-r1'; case='case-06'; type='baseline'; ver='v1'; rid='B03-case-06-r1'; st=200
     ch='首版 1080x1440 折叠城市封面（SizedOverflowBox 巨字出血为主导技术）'
     ob='渲染成功，字节 92281 与日志一致，尺寸 1080x1440 与 DSL 一致'
     rs='首版成立，进入视觉迭代'
     vw=$true; ve='读图 outputs/.../B03/case-06/final.png：刊头与折面图形成立' }
  @{ n='c07-r1'; case='case-07'; type='baseline'; ver='v1'; rid='B03-case-07-r1'; st=200
     ch='首版 1748x760 登机牌（REPEAT 渐变条带为主导技术）'
     ob='渲染成功，字节 122969 与日志一致，尺寸 1748x760 与 DSL 一致'
     rs='首版成立，进入视觉迭代'
     vw=$true; ve='读图 outputs/.../B03/case-07/final.png：斜纹条带与票面分区成立' }
  @{ n='c08-r1'; case='case-08'; type='baseline'; ver='v1'; rid='B03-case-08-r1'; st=200
     ch='首版 1200x1500 ELEVATION 深度与材质规范（boxShadow 多层阴影为主导技术）'
     ob='语法修复后渲染成功，字节 202447 与日志一致，尺寸 1200x1500 与 DSL 一致'
     rs='首版成立，进入视觉迭代'
     vw=$true; ve='读图 outputs/.../B03/case-08/final.png：阴影阶梯逐级可见' }
  @{ n='c09-r1'; case='case-09'; type='baseline'; ver='v1'; rid='B03-case-09-r1'; st=200
     ch='首版 1920x480 东港站到发看板'
     ob='渲染成功，字节 124832 与日志一致，尺寸 1920x480 与 DSL 一致'
     rs='首版成立'
     vw=$true; ve='读图 outputs/.../B03/case-09/final.png：车次行距与到发分区成立' }
  @{ n='c10-r1'; case='case-10'; type='baseline'; ver='v1'; rid='B03-case-10-r1'; st=200
     ch='首版 1200x1200 软木园等轴测导览图（Transform 16 元矩阵为主导技术）'
     ob='渲染成功但画面故障：脚本内 $U 与 $u 大小写冲突令 UNIT 失效导致体块比例错误；IsoTop/IsoLeft/IsoRight 的 transform matrix 又带了与 Positioned 重复的平移'
     rs='读图诊断出两处结构性错误，进入修复'
     vw=$true; ve='读图 outputs/.../B03/case-10/final.png（已存档 attempts/case-10-r1.png 60654 字节）：体块比例失真' },

  # ---- visual iterations ----
  @{ n='c03-v2'; case='case-03'; type='visual'; ver='v2'; rid='B03-case-03-r2'; st=200
     ch='存根 STUB 与 NO. 合并为单行「存根 STUB NO.」、编号下移 y388→372；正文右档 (960,400,200,200) 新增蓝色二色套印版画与图注「二色套印 PLATE 02」'
     ob='首版存根标题拆成两行读作意外折行；正文右半约 200x600 死白'
     rs='round 2 渲染后读图：标题单行、右档补满，接受'
     vw=$true; ve='读图 outputs/.../B03/case-03/final.png（65155 字节）' }
  @{ n='c04-v2'; case='case-04'; type='visual'; ver='v2'; rid='B03-case-04-r2'; st=200
     ch='IBlur 条纹顶点 396→40、步长 36→28（绝对色带落到 y400..674）；黄色加 alpha 改 #FFD16680 / #FFD16666，橙色改 #E4622CB3'
     ob='条纹 top 是相对 IBlur 框(y=360) 的值，原写法使色带落在 y756..1102，横穿 GHOST 与底部统计行；纯黄底上白色 200px 时间数字对比不足'
     rs='round 2 渲染后 GHOST 与统计行完全清空，时间数字清晰'
     vw=$true; ve='读图 outputs/.../B03/case-04/final.png（180230 字节）+ 坐标核算' }
  @{ n='c04-v3'; case='case-04'; type='visual'; ver='v3'; rid='B03-case-04-r3'; st=200
     ch='DELTA 区块加独立卡片 (1300,564,548,116)，内文按 24px 内缩 x1300→1324、宽 548→500，游标移到进度条末端 x1618'
     ob='round 2 中 DELTA 文字与色条贴着卡片边，和上方三张 SECTOR 卡的 24px 内缩不一致'
     rs='round 3 渲染，读图确认四张卡右边界同为 1848、内缩一致'
     vw=$true; ve='读图 outputs/.../B03/case-04/final.png（179949 字节）' }
  @{ n='c05-v2'; case='case-05'; type='visual'; ver='v2'; rid='B03-case-05-r2'; st=200
     ch='图框底部补分隔线 y618、观测说明 y632、采样/时间/单位行 y666；页脚死白处新增「辨识要点 IDENTIFICATION」标题与第二段行内徽章（4 枚新 chip）'
     ob='首版图框下半与 y1050..1190 两处大面积空白'
     rs='round 2 渲染后两处空白填满，新增段落止于 y1190，未与 y1200 正文相撞'
     vw=$true; ve='读图 outputs/.../B03/case-05/final.png（182307 字节）' }
  @{ n='c06-v2'; case='case-06'; type='visual'; ver='v2'; rid='B03-case-06-r2'; st=200
     ch='刊头 fontSize 250→320，Bleed 框定为 (48,0,1032,360)'
     ob='首版 FOLDCITY 约 83% 可见，右缘裁切像失误而不是出血'
     rs='round 2 渲染，准备逐像素核对墨迹'
     vw=$true; ve='读图 outputs/.../B03/case-06/final.png（88971 字节）' }
  @{ n='c06-v3'; case='case-06'; type='visual'; ver='v3'; rid='B03-case-06-r3'; st=200
     ch='Bleed 内 Text 加 maxLines="1"（已写入 DSL，渲染无任何变化）'
     ob='PNG 字节与 round 2 完全相同（sha 516CCB8B…），墨迹仍止于 x=891：SizedOverflowBox 把自身宽度当作换行约束传给 Text，maxLines 被渲染器忽略'
     rs='记入 probes.md §9，判定该写法无效，改用加宽裁切框'
     vw=$true; ve='System.Drawing 逐像素测墨迹 x=63..891；Get-FileHash 对比 r2/r3 完全一致' }
  @{ n='c06-v4'; case='case-06'; type='visual'; ver='v4'; rid='B03-case-06-r4'; st=200
     ch='Bleed 框宽 1032→2000（裁切框越出页面），撤下无效的 maxLines'
     ob='框宽 2000 > 字宽 1610 → 不再换行，ClipRect 不再切割，改由 1080px 页边裁切'
     rs='round 4 渲染，墨迹 x=63..1079（页宽 1080）= 真出血'
     vw=$true; ve='读图 outputs/.../B03/case-06/final.png（93707 字节）+ 墨迹 x=63..1079' }
  @{ n='c07-v2'; case='case-07'; type='visual'; ver='v2'; rid='B03-case-07-r2'; st=200
     ch='「次日 +1」移到 (604,388,170,30)；新增右栏 航程/03:35/机型 与 常旅客/TIDE-8842170；栅格步长 260→268'
     ob='首版右下两块死白、次日 +1 与 02:15 基线不齐、第四格贴着右栏'
     rs='round 2 渲染'
     vw=$true; ve='读图 outputs/.../B03/case-07/final.png（133923 字节）' }
  @{ n='c07-v3'; case='case-07'; type='visual'; ver='v3'; rid='B03-case-07-r3'; st=200
     ch='右栏 x880→900、宽 270→240，与第四格 x900 对齐（含 航程/03:35/机型/常旅客 四项）'
     ob='读图发现新右栏与相邻行「登机 BOARD」相差 20px，纵向错位'
     rs='round 3 渲染，坐标核对四列同为 96/364/632/900'
     vw=$true; ve='读图 outputs/.../B03/case-07/final.png（133901 字节）' }
  @{ n='c07-v4'; case='case-07'; type='visual'; ver='v4'; rid='B03-case-07-r4'; st=200
     ch='存根右侧补「旅客 PASSENGER / CHEN/YI-HAN」右对齐列；日期改右对齐；条码重排为 230px 条 + 21x10 间隙 = 满宽 440'
     ob='存根 x1470..1656、y110..390 约 190x280 空白，条码只占左半宽'
     rs='round 4 渲染，读图确认存根左右平衡'
     vw=$true; ve='读图 outputs/.../B03/case-07/final.png（140684 字节）' }
  @{ n='c08-v2'; case='case-08'; type='visual'; ver='v2'; rid='B03-case-08-r2'; st=200
     ch='A 段栅格步长 375→363（卡片右边界 1152→1128，与全页分隔线对齐）；C 段 Stack 由 440x200 收紧为 400x170'
     ob='A 段卡片比上下分隔线多出 24px；C 段原几何只吃掉约 10px 阴影，两块面板几乎看不出差别'
     rs='round 2 渲染'
     vw=$true; ve='读图 outputs/.../B03/case-08/final.png（202221 字节）+ 右边界像素实测 x=1127' }
  @{ n='c08-v3'; case='case-08'; type='visual'; ver='v3'; rid='B03-case-08-r3'; st=200
     ch='左侧 Stack 显式加 clipBehavior="HARD_EDGE"，标题改「clipBehavior=HARD_EDGE 被裁切」'
     ob='逐像素采样 y=1258..1312，左右两半完全相同（y=1272 均为 #E8EAEC），裁剪并未生效'
     rs='round 3 渲染后仍完全相同，原方案被推翻，转做探针 p19 定位真相'
     vw=$true; ve='System.Drawing 像素采样左右两半逐点比对' }
  @{ n='c08-v4'; case='case-08'; type='visual'; ver='v4'; rid='B03-case-08-r4'; st=200
     ch='C 段整体改版为「子节点裁剪」对照：灰框 + 橙卡 + OVERFLOW 标签，HARD_EDGE 被裁 vs NONE 溢出；标题改「Stack 裁剪行为」；新增脚注「实测 p19：Stack 裁的是子节点本身，boxShadow 不参与裁剪」'
     ob='探针 p19 证明 Stack 只裁子节点、从不裁 boxShadow，原「阴影裁剪对照」在该渲染器上根本画不出来'
     rs='round 4 渲染，逐像素复核左卡底 y=1223（框边 1224）vs 右卡底 y=1293，差 70px'
     vw=$true; ve='读图 outputs/.../B03/case-08/final.png（210984 字节）+ 像素复核 1223/1293' }
  @{ n='c09-v1'; case='case-09'; type='visual'; ver='v1'; rid=$null; st=$null
     ch='无改版：首版经读图与坐标核对直接通过，保持 round 1 为最终稿'
     ob='车次行距、到发分区、字节与尺寸核对均无问题，未发现需修正的缺陷'
     rs='case-09 最终稿 = round 1'
     vw=$true; ve='读图 outputs/.../B03/case-09/final.png（124832 字节）' }
  @{ n='c10-v1'; case='case-10'; type='visual'; ver='v1'; rid='B03-case-10-r2'; st=200
     ch='变量改名 $U→$UNIT 规避大小写冲突；IsoTop/IsoLeft/IsoRight 的 transform matrix 去掉与 Positioned 重复的平移'
     ob='比例恢复正常，但塔身仍被后画的绿色方块盖住：体块按数组原始顺序绘制，没有按深度排序'
     rs='round 2 渲染，问题缩小到绘制次序'
     vw=$true; ve='读图 attempts/case-10-r2.png（115917 字节）' }
  @{ n='c10-v2'; case='case-10'; type='visual'; ver='v2'; rid='B03-case-10-r3'; st=200
     ch='体块改为单一数组并按 (u+v) 升序、u 次序排序后绘制；树从 (0,0) 移到 (0,5)'
     ob='探针取样：塔身在 r2 为 #7FB07A/#7FB07A/#4F7A45（被树色覆盖），r3 为 #C98A4A/#E9B978/#DCA464（正确塔色）；迁树后 (201,680)/(150,690) 取样 #7FB07A/#3F6B3A'
     rs='遮挡关系正确，5 树 5 馆全部按深度渲染'
     vw=$true; ve='读图 outputs/.../B03/case-10/final.png（113583 字节）+ 定点探针取色' }
  @{ n='c10-v3'; case='case-10'; type='visual'; ver='v3'; rid='B03-case-10-r4'; st=200
     ch='图例改为两行带键：地面（步道/草坪/水景）与展馆（儿童馆/花房/主展馆/观景塔/茶室），色块自 x=140 起步长 160、标签自 x=72 起宽 60'
     ob='首版图例只列 3 项地面材质，画面却有 5 座馆体，图例与画面不符'
     rs='round 4 渲染，读图确认 5 馆逐一入表'
     vw=$true; ve='读图 outputs/.../B03/case-10/final.png（120494 字节）' },

  # ---- evidence corrections for probe conclusions ----
  @{ n='p06-correct'; case=$null; type='evidence-correction'; ver=$null; rid='B03-p06-stack-shadow'; st=200
     ch='更正 p06 结论：原记「默认 Stack 硬切阴影、NONE 阴影完整」是错的'
     ob='几何上阴影只到 y≈239 而 Stack 底 y=240，根本没有可裁空间；两半阴影在 y=214..266 逐点相同，唯一差异 y=246..252 来自左右不同的标签文字'
     rs='改写 probes.md §6，并新增探针 p19 用 4x2 对照重测'
     vw=$true; ve='System.Drawing 对 probes/p06-stack-shadow.png 逐行逐列采样' }
  @{ n='p09-correct'; case=$null; type='evidence-correction'; ver=$null; rid='B03-p09-overflow-bleed'; st=200
     ch='更正 p09 结论：原记「巨字超出并精确止边」是换行误读'
     ob='橙字墨迹只到 x=19..533，仅 2 个字形：FOLD 在 700px 框内要占 1080px，SizedOverflowBox 把自身宽度当换行约束，第一行只剩 FO，LD 落到第二行被 300px 框吃掉'
     rs='改写 probes.md §9，并由 case-06 三次实测给出可行写法（裁切框必须宽于字）'
     vw=$true; ve='System.Drawing 对 probes/p09-overflow-bleed.png 求墨迹包围盒与行带分布' }
)

$i = 30
foreach ($p in $plan) {
  $i++
  $req = $null
  if ($null -ne $p.rid) { $req = Req $p.rid ([int]$p.st) }
  $obj = [ordered]@{
    iteration_id = 'ite-B03-' + $p.n
    case_id = $p.case
    type = $p.type
    version = $p.ver
    parent_version = $(if ($p.type -eq 'visual' -and $p.ver -ne 'v1') { 'v' + ([int]($p.ver.Substring(1)) - 1) } else { $null })
    request_id = $p.rid
    http_status = $(if ($null -ne $req) { $req.http_status } else { $null })
    duration_ms = $(if ($null -ne $req) { $req.duration_ms } else { $null })
    render_started_utc = $(if ($null -ne $req) { $req.started_utc } else { $null })
    render_ended_utc = $(if ($null -ne $req) { $req.ended_utc } else { $null })
    change = $p.ch
    observation = $p.ob
    result = $p.rs
    viewed = $p.vw
    view_evidence = $p.ve
  }
  [IO.File]::AppendAllText($iterLog, ($obj | ConvertTo-Json -Compress) + "`n", $enc)
}

"iterations now: " + (Get-Content $iterLog -Encoding UTF8).Count
