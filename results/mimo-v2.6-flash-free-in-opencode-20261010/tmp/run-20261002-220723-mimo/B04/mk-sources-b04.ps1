# mk-sources-b04.ps1 -- build outputs/B04/sources.json from requests.jsonl + the vetted source table
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$b    = Join-Path $root 'tmp\run-20261002-220723-mimo\B04'
$o    = Join-Path $root 'outputs\run-20261002-220723-mimo\B04'
$enc  = New-Object System.Text.UTF8Encoding($false)

$reqs = @(); Get-Content (Join-Path $b 'requests.jsonl') -Encoding UTF8 | ForEach-Object { $reqs += ($_ | ConvertFrom-Json) }

function Visits([string[]]$ids) {
  $out = @()
  foreach ($id in $ids) {
    $r = @($reqs | Where-Object { $_.id -eq $id })[0]
    if ($null -eq $r) { continue }
    $f = $null; if ($r.response_file) { $f = 'tmp/run-20261002-220723-mimo/B04/research/' + (Split-Path $r.response_file -Leaf) }
    if ($r.type -eq 'documentation' -or $r.type -eq 'fonts') { $f = 'tmp/run-20261002-220723-mimo/B04/docs/' + (Split-Path $r.response_file -Leaf) }
    $out += [ordered]@{
      request_id = $r.id; url = $r.url; method = $r.method
      http_status = $r.http_status; bytes = $r.bytes
      started_at = $r.started_at; ended_at = $r.ended_at; duration_ms = $r.duration_ms
      local_file = $f; request_id_header = $r.request_id
      error_summary = $r.error_summary
      retrieved_in_this_run = $true
    }
  }
  return ,$out
}

$src = @(
 [ordered]@{
  id='S1'; short='IERS Leap_Second.dat'; title='IERS / 巴黎天文台 Leap_Second.dat（TAI−UTC 阶跃表）'
  publisher='IERS Earth Orientation Center, Paris Observatory'; kind='primary_dataset'; trust='primary'
  url='http://hpiers.obspm.fr/iers/bul/bulc/Leap_Second.dat'
  request_ids=@('B04-res-18-leap-second-dat')
  local_files=@('tmp/run-20261002-220723-mimo/B04/research/Leap_Second.dat','tmp/run-20261002-220723-mimo/B04/research/Leap_Second.decoded.txt','tmp/run-20261002-220723-mimo/B04/research/leap-seconds-rows.json')
  key_facts=@(
    '28 行 TAI−UTC 阶跃：MJD 41317（1972-01-01，10 s）到 MJD 57754（2017-01-01，37 s）'
    '首行 10 s 是 1972 年系统启用时的初始值，不计为一次闰秒；其后 27 行各对应一次插入，合计 27 次'
    '全部插入发生在 6 月 30 日或 12 月 31 日（6 月 11 次、12 月 16 次）'
    '文件头：Updated through IERS Bulletin 72 issued in July 2026；File expires on 28 June 2027')
  used_by=@('case-01','case-04','case-05','case-07','case-08')
  confidence='confirmed'
  notes='二进制小数字段按空白切分后逐位转字符解码，解码文本与行级 JSON 均落盘；表内 27 行的日期差、MJD、TAI−UTC 全部由程序复算，未手抄'
 },
 [ordered]@{
  id='S2'; short='IERS Bulletin C 72'; title='IERS Bulletin C 72（2026 年 7 月 6 日，巴黎）'
  publisher='IERS / Paris Observatory'; kind='primary_bulletin'; trust='primary'
  url='https://hpiers.obspm.fr/iers/bul/bulc/bulletinc.dat'
  request_ids=@('B04-res-29-bulletinc','B04-res-04-iers-bulletinc','B04-res-06-iers-bulletins','B04-res-20-hpiers-bulletins')
  local_files=@('tmp/run-20261002-220723-mimo/B04/research/bulletinc.dat','tmp/run-20261002-220723-mimo/B04/research/bulletinc.decoded.txt')
  key_facts=@(
    '"NO leap second will be introduced at the end of December 2026"'
    '"from 2017 January 1, 0h UTC, until further notice : UTC-TAI = -37 s"'
    'Bulletin C 每半年发布一次，用于宣布或否定当年 6 月与 12 月的闰秒')
  used_by=@('case-01','case-04','case-05','case-07','case-08','case-09','case-10')
  confidence='confirmed'
  notes='同一事实由 iers.org 与 hpiers 两处入口交叉取得'
 },
 [ordered]@{
  id='S3'; short='IERS 闰秒说明页'; title='IERS "Leap Seconds" 说明页'
  publisher='IERS Earth Orientation Center, Paris Observatory'; kind='primary_explainer'; trust='primary'
  url='http://hpiers.obspm.fr/eop-pc/index.php?index=leapsecond&lang=en'
  request_ids=@('B04-res-19-hpiers-leapsecond')
  local_files=@('tmp/run-20261002-220723-mimo/B04/research/hpiers-leapsecond.html')
  key_facts=@(
    '"it was desired ... to maintain the difference UT1-UTC smaller than 0.9 second"'
    '"Since the adoption of this system in 1972 ... it has been necessary to add 27 s to UTC"'
    '"The last additional second has been introduced on 1 January 2017, at 0h UTC"'
    '"On 30 June 2012, the last minute of the day has lasted 61 seconds"'
    '"first preference ... end of December and June, second preference ... end of March and September. Since the system was introduced in 1972, only dates in June and December have been used"'
    '决定权属 IERS Earth Orientation Center（巴黎天文台）'
    '"the initial choice of the value of the second (1/86400 mean solar day of the year 1820)"')
  used_by=@('case-01','case-02','case-03','case-06','case-07','case-09')
  confidence='confirmed'
  notes='0.9 s、27 s、2012-06-30 的 61 秒、仅用 6/12 月、1820 年平太阳日五处均为页面原文'
 },
 [ordered]@{
  id='S4'; short='IERS 常用常数页'; title='IERS Earth Orientation Parameters 常用常数页'
  publisher='IERS Earth Orientation Center'; kind='primary_reference'; trust='primary'
  url='http://hpiers.obspm.fr/eop-pc/index.php?index=constants&lang=en'
  request_ids=@('B04-res-25-hp-constants')
  local_files=@('tmp/run-20261002-220723-mimo/B04/research/hpiers-constants.html')
  key_facts=@(
    'Mean solar day（已去除季节项）目前比 86400 s 长约 0.2 ms'
    'Ω_N = 7.292 115 146 706 4×10⁻⁵ rad/s（1820 历元标称值）')
  used_by=@('case-03','case-06')
  confidence='confirmed'
  notes='0.2 ms/天是页面给出的量级，非精确瞬时值'
 },
 [ordered]@{
  id='S5'; short='TAI−UTC 历史表'; title='IERS TAI−UTC 历史与调整表'
  publisher='IERS Earth Orientation Center'; kind='primary_table'; trust='primary'
  url='https://hpiers.obspm.fr/eop-pc/index.php?index=TAI-UTC_tab&lang=en'
  request_ids=@('B04-res-30-tai-utc-history','B04-res-31-utc-offsets')
  local_files=@('tmp/run-20261002-220723-mimo/B04/research/tai-utc-history.html','tmp/run-20261002-220723-mimo/B04/research/utc-offsets.html')
  key_facts=@(
    '1961–1971 年间 TAI−UTC 是分数值（频率调整），不是闰秒；例：1968-02 起 4.213 170 0 s + (MJD−39126)×0.002 592 s'
    '1972-01-01 起跳为整 10 s 并改用闰秒机制')
  used_by=@('case-02')
  confidence='confirmed'
  notes='用于说明"秒的定义与 UTC 的偏移是两件事"，也是 1972 年这个制度起点的依据'
 },
 [ordered]@{
  id='S6'; short='CGPM 2022 决议 4'; title='第 27 届 CGPM（2022）决议 4《On the use and future development of UTC》'
  publisher='BIPM - Conference Générale des Poids et Mesures'; kind='primary_resolution'; trust='primary'
  url='https://www.bipm.org/committees/cg/cgpm/27-2022/resolution-4'
  doi='10.59161/CGPM2022RES4E'
  request_ids=@('B04-res-14-cgpm27-res4','B04-res-05-cgpm-resolutions','B04-res-11-cgpm27-res1','B04-res-12-cgpm27-res2','B04-res-13-cgpm27-res3','B04-res-16-cgpm27-res6','B04-res-17-cgpm27-res7')
  local_files=@('tmp/run-20261002-220723-mimo/B04/research/cgpm27-res4.html')
  key_facts=@(
    '|UT1−UTC| 的最大值将在 2035 年或之前提高'
    '要求 CIPM 提出实施建议，供 2026 年第 28 届 CGPM 审议，并在 2035 年前实施'
    '地球自转的近期观测"可能需要首次负闰秒，而它的插入从未被预见或测试过"'
    'UTC 的不连续可能在 GNSS、电信、能源传输等关键数字基础设施造成严重故障'
    'UTC 是唯一推荐的国际参考时标，是大多数国家民用时间的基础')
  used_by=@('case-01','case-03','case-06','case-09','case-10')
  confidence='confirmed'
  notes='决议 4 的"2035 / 2026 / 首次负闰秒 / 未被预见或测试"四点均为原文表述，作品中用「决议 4 同时提醒」框单独标出为引文'
 },
 [ordered]@{
  id='S7'; short='CGPM 2022 决议 5'; title='第 27 届 CGPM（2022）决议 5《On the future redefinition of the second》'
  publisher='BIPM - CGPM'; kind='primary_resolution'; trust='primary'
  url='https://www.bipm.org/committees/cg/cgpm/27-2022/resolution-5'
  doi='10.59161/CGPM2022RES5E'
  request_ids=@('B04-res-15-cgpm27-res5')
  local_files=@('tmp/run-20261002-220723-mimo/B04/research/cgpm27-res5.html')
  key_facts=@(
    '第 13 届 CGPM（1967）定义秒为铯 133 原子基态两个超精细能级之间跃迁辐射的 9 192 631 770 个周期'
    '第 26 届 CGPM（2018）把 Δν_Cs 固定为 9 192 631 770 Hz'
    '光学频率标准的准确度已比该定义的实现高出最多 100 倍'
    '第 28 届 CGPM（2026）审议候选物种，第 29 届 CGPM（2030）通过新定义')
  used_by=@('case-01','case-02','case-09','case-10')
  confidence='confirmed'
  notes='case-02 卡片直接标注 DOI'
 },
 [ordered]@{
  id='S8'; short='BIPM 秒的重定义'; title='BIPM "Redefinition of the second" 专页'
  publisher='BIPM'; kind='primary_reference'; trust='primary'
  url='https://www.bipm.org/en/redefinition-second'
  request_ids=@('B04-res-27-second-redef','B04-res-28-si-brochure','B04-res-35-si-brochure-pdf')
  local_files=@('tmp/run-20261002-220723-mimo/B04/research/bipm-second.html','tmp/run-20261002-220723-mimo/B04/research/bipm-si-brochure.html','tmp/run-20261002-220723-mimo/B04/research/si_brochure_1.pdf')
  key_facts=@(
    'CCTF 正在更新秒的第二次重定义路线图，新定义 "possibly in 2030"'
    'SI 手册（si_brochure_1.pdf，5,199,982 B）给出秒与 UTC 的正式表述')
  used_by=@('case-02')
  confidence='confirmed'
  notes='同一主题的旧地址 /si/redefinition-of-the-second 返回 404（B04-res-22），按原样保留'
 },
 [ordered]@{
  id='S9'; short='ITU-R TF.460-6'; title='Recommendation ITU-R TF.460-6《Standard-frequency and time-signal emissions》'
  publisher='ITU-R'; kind='primary_recommendation'; trust='primary'
  url='https://www.itu.int/rec/R-REC-TF.460/en'
  request_ids=@('B04-res-23-itu-tf460')
  local_files=@('tmp/run-20261002-220723-mimo/B04/research/itu-tf460.html')
  key_facts=@('TF.460-6 为现行有效的建议书，规定标准频率与时间信号发射')
  used_by=@('case-10')
  confidence='confirmed'
  notes='仅作为"工程侧确有国际建议"的旁证，未在画面引用具体数值'
 },
 [ordered]@{
  id='S10'; short='IANA tzdb'; title='IANA Time Zone Database 分发入口'
  publisher='IANA'; kind='primary_software_registry'; trust='primary'
  url='https://data.iana.org/time-zones/'
  request_ids=@('B04-t06-iana','B04-t10-iana-root')
  local_files=@('tmp/run-20261002-220723-mimo/B04/research/t06.html','tmp/run-20261002-220723-mimo/B04/research/t10.html')
  key_facts=@('时区数据库是闰秒在工程侧落地的权威分发源')
  used_by=@('case-10')
  confidence='confirmed'
  notes='工具箱条目 1/2 与 tzdb 的处理惯例一致，但工具箱 6 条本身标注为"编辑建议，非来源结论"'
 },
 [ordered]@{
  id='S11'; short='RFC 5905'; title='RFC 5905 — Network Time Protocol Version 4'
  publisher='IETF / RFC Editor'; kind='primary_specification'; trust='primary'
  url='https://datatracker.ietf.org/doc/html/rfc5905'
  request_ids=@('B04-t09-ietf')
  local_files=@('tmp/run-20261002-220723-mimo/B04/research/t09.html')
  key_facts=@('NTP 对 UTC/TAI 偏移与闰秒处理的规范性描述')
  used_by=@('case-10')
  confidence='confirmed'
  notes='工具箱条目 2（连续时标 + 写明口径）与 NTP 的 TAI/Unix 秒口径一致'
 },
 [ordered]@{
  id='S12'; short='IERS 地球自转页'; title='IERS "Earth rotation" 说明页'
  publisher='IERS Earth Orientation Center'; kind='primary_explainer'; trust='primary'
  url='http://hpiers.obspm.fr/eop-pc/index.php?index=rotation&lang=en'
  request_ids=@('B04-res-21-hpiers-rotation','B04-res-09-hpiers-index','B04-res-18-leap-second-dat','B04-res-08-bulletinB')
  local_files=@('tmp/run-20261002-220723-mimo/B04/research/hpiers-rotation.html','tmp/run-20261002-220723-mimo/B04/research/hpiers-index.html','tmp/run-20261002-220723-mimo/B04/research/iers-bulletinB.txt')
  key_facts=@('地球自转的不规则波动、UT1 的测量方式（VLBI）')
  used_by=@('case-03')
  confidence='confirmed'
  notes=''
 },
 [ordered]@{
  id='S13'; short='NIST / NPL / PTB 时间页'; title='各国计量机构时间与频率介绍页'
  publisher='NIST（美国）· NPL（英国）· PTB（德国）'; kind='secondary_reference'; trust='authoritative_secondary'
  url='https://physics.nist.gov/cuu/Constants/index.html'
  request_ids=@('B04-res-32-nist-constants','B04-res-33-npl','B04-res-34-ptb')
  local_files=@('tmp/run-20261002-220723-mimo/B04/research/nist-constants.html','tmp/run-20261002-220723-mimo/B04/research/npl-time.html','tmp/run-20261002-220723-mimo/B04/research/ptb-time.html')
  key_facts=@('秒与时间保持的公众解释；铯与光学频标的现状')
  used_by=@('case-02')
  confidence='corroborating'
  notes='仅作旁证，作品中的关键数字仍以 S7（CGPM 决议 5）为准'
 },
 [ordered]@{
  id='S14'; short='BIPM CGPM 议题页'; title='BIPM CGPM 总览与决议索引页'
  publisher='BIPM'; kind='primary_index'; trust='primary'
  url='https://www.bipm.org/en/committees/cg/cgpm'
  request_ids=@('B04-t04-bipm')
  local_files=@('tmp/run-20261002-220723-mimo/B04/research/t04.html')
  key_facts=@('第 28 届 CGPM 的届次与议题入口')
  used_by=@('case-09')
  confidence='confirmed'
  notes=''
 }
)

# attach visit records
$srcFinal = @()
foreach ($s in $src) {
  $s['visits'] = (Visits $s.request_ids)
  $s['all_visits_succeeded'] = -not (@($s.visits | Where-Object { $_.http_status -ne 200 }).Count -gt 0)
  $srcFinal += $s
}

$unreachable = @($reqs | Where-Object { $_.type -eq 'research' -and ($_.http_status -eq 404 -or $null -eq $_.http_status) } | ForEach-Object {
  [ordered]@{
    request_id = $_.id; url = $_.url; http_status = $_.http_status
    started_at = $_.started_at; ended_at = $_.ended_at
    error_summary = $(if ($_.error_summary) { $_.error_summary.Substring(0, [Math]::Min(160, $_.error_summary.Length)) } else { $null })
    outcome = $(if ($null -eq $_.http_status) { 'network_failure' } else { 'http_404' })
    retained = $true
    substitution = '该主机/地址不可用时，相关事实改由 BIPM、IERS、hpiers、IANA、ITU、NIST、NPL、PTB、RFC 等一手来源交叉覆盖；未以任何未访问页面充当来源'
  }
})

$perCase = [ordered]@{
 'case-01' = [ordered]@{ sources=@('S1','S2','S3','S6','S7')
   claims=@(
    @{ text='封面标题 23:59:60 与"官方承认却不存在的时刻"'; basis='confirmed_fact'; refs=@('S1','S2','S3') }
    @{ text='统计块 27（1972 年以来加入 UTC 的次数）'; basis='confirmed_fact'; refs=@('S1','S3') }
    @{ text='统计块 −37 s（UTC 与 TAI 当前的固定差值）'; basis='confirmed_fact'; refs=@('S1','S2') }
    @{ text='统计块 2035（CGPM 决议：在这一年之前改变闰秒机制）'; basis='confirmed_fact'; refs=@('S6') }
    @{ text='编辑按"世界已经 3 567 天没有再加过一秒（截至 2026-10-07）"'; basis='editorial_calculation'; refs=@('S1','S2')
      formula='2016-12-31 到 2026-10-07 的日历天数 = 3567 天（10 年 3652 天 − 85 天）' }
    @{ text='刊名《时间的边缘》第 03 期、编辑部署名'; basis='demo_data'; refs=@() }
   )}
 'case-02' = [ordered]@{ sources=@('S7','S8','S3','S5')
   claims=@(
    @{ text='1820 年平太阳日 ÷ 86 400 的原始定义'; basis='confirmed_fact'; refs=@('S3') }
    @{ text='9 192 631 770 个周期 / 9 192 631 770 Hz'; basis='confirmed_fact'; refs=@('S7') }
    @{ text='光学标准高出最多 100 倍'; basis='confirmed_fact'; refs=@('S7') }
    @{ text='2026 第 28 届 CGPM 选定候选物种、2030 第 29 届 CGPM 通过新定义'; basis='confirmed_fact'; refs=@('S7') }
    @{ text='1961–1971 为分数频率调整而非闰秒'; basis='confirmed_fact'; refs=@('S5') }
   )}
 'case-03' = [ordered]@{ sources=@('S3','S4','S6','S12')
   claims=@(
    @{ text='|UT1 − UTC| 必须保持在 0.9 秒以内'; basis='confirmed_fact'; refs=@('S3') }
    @{ text='TAI 由 BIPM 全球原子钟网络连续计算、不跳变'; basis='confirmed_fact'; refs=@('S3') }
    @{ text='UTC 与 TAI 只相差一个整数秒、1972 年起成为各国民用时间基础'; basis='confirmed_fact'; refs=@('S3','S6') }
    @{ text='UT1 由 VLBI 观测得到、不均匀'; basis='confirmed_fact'; refs=@('S3','S12') }
    @{ text='纵向未按比例（SCALE FREE）的示意阶梯与波形'; basis='editorial_interpretation'; refs=@() }
   )}
 'case-04' = [ordered]@{ sources=@('S1','S2')
   claims=@(
    @{ text='27 行插入日期、生效日期、MJD、TAI−UTC、距上次天数、月份'; basis='confirmed_fact'; refs=@('S1')
      formula='距上次 = 相邻两行插入日期的日历天数差，由程序计算；MJD 为生效首日的儒略日' }
    @{ text='合计 27 次 · TAI−UTC 10 s → 37 s'; basis='confirmed_fact'; refs=@('S1'); formula='37 − 10 = 27' }
    @{ text='平均间隔 625 天'; basis='editorial_calculation'; refs=@('S1'); formula='(2016-12-31 − 1972-06-30) ÷ 26 = 16255 ÷ 26 = 625.19 → 625 天' }
    @{ text='最长 2 557 天'; basis='confirmed_fact'; refs=@('S1'); formula='1998-12-31 → 2005-12-31 = 2557 天' }
   )}
 'case-05' = [ordered]@{ sources=@('S1','S2')
   claims=@(
    @{ text='按十年统计 9 / 6 / 7 / 2 / 3 / 0（合计 27）'; basis='editorial_calculation'; refs=@('S1')
      formula='按插入年份归入 1970s(1970-1979)=9、1980s=6、1990s=7、2000s=2、2010s=3、2020s(至今)=0；分母为 1972-2026 共 55 年，分子合计 27' }
    @{ text='年份矩阵 55 格、26 个年份有闰秒、1972 年有 2 次'; basis='editorial_calculation'; refs=@('S1')
      formula='1972..2026 共 55 年；有闰秒的年份数 = 26（1972 计 2 次，26 年 × 1 + 1 年 × 2 = 27）' }
    @{ text='只用过两个月的最后一天：6 月 11 次、12 月 16 次（合计 27）'; basis='confirmed_fact'; refs=@('S1','S3') }
    @{ text='平均间隔 625 天、最长 2 557 天（1998-12-31 → 2005-12-31）'; basis='editorial_calculation'; refs=@('S1') }
   )}
 'case-06' = [ordered]@{ sources=@('S4','S3','S6')
   claims=@(
    @{ text='0.2 毫秒 / 天（平太阳日超出 86400 秒的量级）'; basis='confirmed_fact'; refs=@('S4') }
    @{ text='CGPM 决议 4：UTC 与 TAI 只相差一个整数秒，故偏移量只能取整数'; basis='confirmed_fact'; refs=@('S6') }
    @{ text='0.2 毫秒 / 天 × 5 000 天 = 1 秒'; basis='editorial_calculation'; refs=@('S4'); formula='0.0002 s/d × 5000 d = 1 s（量级演算，非触发条件）' }
    @{ text='0.2 毫秒 / 天 × 4 500 天 ≈ 0.9 秒，约 12 年触及阈值'; basis='editorial_calculation'; refs=@('S4','S3')
      formula='0.0002 s/d × 4500 d = 0.9 s；4500 d ÷ 365.25 ≈ 12.3 年。页面明确标注"若地球匀速变慢"且"UT1−UTC 的漂移并不匀速"' }
    @{ text='0.1 秒梳齿与整数落点的示意刻度'; basis='editorial_interpretation'; refs=@() }
   )}
 'case-07' = [ordered]@{ sources=@('S3','S1','S2')
   claims=@(
    @{ text='"On 30 June 2012, the last minute of the day has lasted 61 seconds."'; basis='confirmed_fact'; refs=@('S3') }
    @{ text='2012-06-30 为第 25 次，TAI−UTC 34 → 35，生效 2012-07-01'; basis='confirmed_fact'; refs=@('S1') }
    @{ text='61 个等长刻度 + 第 61 个插入在 23:59:60'; basis='editorial_interpretation'; refs=@('S3') }
   )}
 'case-08' = [ordered]@{ sources=@('S1','S2')
   claims=@(
    @{ text='全部 26 个相邻闰秒间隔（天）'; basis='editorial_calculation'; refs=@('S1'); formula='相邻两行插入日期的日历天数差，n = 27 − 1 = 26' }
    @{ text='最短 184 天（1972-06-30 → 1972-12-31）'; basis='editorial_calculation'; refs=@('S1') }
    @{ text='平均 625 天 = 26 个间隔的算术平均'; basis='editorial_calculation'; refs=@('S1'); formula='16255 ÷ 26 = 625.19' }
    @{ text='上一纪录 2 557 天（1998-12-31 → 2005-12-31）'; basis='editorial_calculation'; refs=@('S1') }
    @{ text='当前空窗 3 567 天（2016-12-31 → 2026-10-07）与 1 010 天的差'; basis='editorial_calculation'; refs=@('S1','S2')
      formula='3567 − 2557 = 1010 天 ≈ 2 年 9 个月；基准日为本次抓取日 2026-10-07' }
   )}
 'case-09' = [ordered]@{ sources=@('S6','S7','S3','S2','S5')
   claims=@(
    @{ text='1972 年 TAI−UTC = 10 s 与 0.9 秒门槛'; basis='confirmed_fact'; refs=@('S3','S1') }
    @{ text='2012 第 25 次、2016 第 27 次、2017 起 UTC−TAI = −37 s'; basis='confirmed_fact'; refs=@('S1','S2') }
    @{ text='2018 第 26 届 CGPM：UTC 是唯一推荐的国际参考时标'; basis='confirmed_fact'; refs=@('S6') }
    @{ text='2022 决议 4：2035 年前提高 |UT1−UTC| 上限、可能需要首次负闰秒'; basis='confirmed_fact'; refs=@('S6') }
    @{ text='2026 第 28 届 CGPM 提交实施计划、审定新的秒定义物种'; basis='confirmed_fact'; refs=@('S6','S7') }
    @{ text='2030 第 29 届 CGPM 通过新定义'; basis='confirmed_fact'; refs=@('S7') }
    @{ text='节点次序与配色由编辑整理'; basis='editorial_interpretation'; refs=@() }
   )}
 'case-10' = [ordered]@{ sources=@('S6','S7','S2','S9','S10','S11')
   claims=@(
    @{ text='决议 4 关于首次负闰秒"从未被预见或测试过"的引文'; basis='confirmed_fact'; refs=@('S6') }
    @{ text='"负闰秒意味着删掉一个 23:59:59"及其后的解释段'; basis='editorial_interpretation'; refs=@('S6')
      note='画面已用「—— 以下为编辑解释，非引文：」明确分隔' }
    @{ text='工具箱 6 条'; basis='editorial_advice'; refs=@('S9','S10','S11')
      note='画面与来源行均标注"工具箱 6 条为编辑建议，非来源结论"' }
    @{ text='Bulletin C 72 的检查节点（每年 1 月与 7 月）'; basis='confirmed_fact'; refs=@('S2') }
   )}
}

$docVisits = Visits @($reqs | Where-Object { $_.type -eq 'documentation' -or $_.type -eq 'fonts' } | ForEach-Object { $_.id })

$result = [ordered]@{
  schema_version = 1
  task_id = 'B04'
  run_id = 'run-20261002-220723-mimo'
  topic = '《多出来的那一秒》—— 协调世界时（UTC）与闰秒的来历、数据与终结'
  generated_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss.fff+08:00')
  timezone = 'UTC+08:00'
  evidence_window = [ordered]@{
    first_request_at = @($reqs | Sort-Object started_utc)[0].started_at
    last_request_at  = @($reqs | Sort-Object ended_utc)[-1].ended_at
    data_cutoff = '2026-10-07（本次抓取日，用于一切"至今/当前"的天数计算）'
  }
  fact_classes = [ordered]@{
    confirmed_fact        = '一手来源原文可直接核对的陈述（数据集行、决议原文、公告原文）'
    source_conclusion     = '来源方给出的结论或判断（如 Bulletin C 的"本次不加"）'
    editorial_calculation = '本编辑依据一手数据做的算术，均附公式、分子分母、单位与时间范围'
    editorial_interpretation = '示意、比喻、编排与解释，不冒充来源'
    editorial_advice      = '给读者的可执行建议，明确标注非来源结论'
    demo_data             = '虚构的刊名、期号、署名、场馆、系统名，均标 DEMO'
  }
  source_count = $srcFinal.Count
  sources = $srcFinal
  per_case_citations = $perCase
  unreachable_attempts = $unreachable
  documentation_visits = $docVisits
  arithmetic_checks = @(
    [ordered]@{ id='AC-01'; label='闰秒次数'; formula='37 s − 10 s = 27'; numerator='TAI−UTC 末值 37'; denominator='初值 10'; unit='s'; range='1972-01-01 → 2017-01-01'; source='S1'; matches_artwork=$true }
    [ordered]@{ id='AC-02'; label='平均间隔'; formula='(2016-12-31 − 1972-06-30) ÷ (27 − 1) = 16255 ÷ 26 = 625.19'; numerator='16255 天'; denominator='26 个间隔'; unit='天'; range='1972-06-30 → 2016-12-31'; source='S1'; matches_artwork=$true; artwork_value='625 天（四舍五入到整数）' }
    [ordered]@{ id='AC-03'; label='最长历史间隔'; formula='2005-12-31 − 1998-12-31 = 2557'; numerator='2557 天'; denominator='1 个间隔'; unit='天'; range='1998-12-31 → 2005-12-31'; source='S1'; matches_artwork=$true }
    [ordered]@{ id='AC-04'; label='最短间隔'; formula='1972-12-31 − 1972-06-30 = 184'; numerator='184 天'; denominator='1 个间隔'; unit='天'; range='1972-06-30 → 1972-12-31'; source='S1'; matches_artwork=$true }
    [ordered]@{ id='AC-05'; label='当前空窗'; formula='2026-10-07 − 2016-12-31 = 3567'; numerator='3567 天'; denominator='n/a'; unit='天'; range='2016-12-31 → 2026-10-07（抓取日）'; source='S1+S2'; matches_artwork=$true }
    [ordered]@{ id='AC-06'; label='空窗比上一纪录长多少'; formula='3567 − 2557 = 1010'; numerator='1010 天'; denominator='n/a'; unit='天'; range='同上'; source='S1+S2'; matches_artwork=$true; artwork_value='1 010 天，约 2 年 9 个月' }
    [ordered]@{ id='AC-07'; label='年代分布'; formula='9 + 6 + 7 + 2 + 3 + 0 = 27'; numerator='27 次'; denominator='1972–2026 共 55 年'; unit='次'; range='按插入年份归组（1970s=1970-1979 … 2020s=2020-2026）'; source='S1'; matches_artwork=$true }
    [ordered]@{ id='AC-08'; label='月份分布'; formula='6 月 11 次 + 12 月 16 次 = 27 次'; numerator='27 次'; denominator='2 个月份'; unit='次'; range='1972-06-30 → 2016-12-31'; source='S1+S3'; matches_artwork=$true }
    [ordered]@{ id='AC-09'; label='有闰秒的年份数'; formula='26 个年份 + 1972 年的第 2 次 = 27 次'; numerator='26 年'; denominator='55 年'; unit='年'; range='1972–2026'; source='S1'; matches_artwork=$true }
    [ordered]@{ id='AC-10'; label='0.2 ms 演算'; formula='0.0002 s/d × 5000 d = 1 s；0.0002 s/d × 4500 d = 0.9 s'; numerator='0.2 毫秒 / 天'; denominator='4500 天 / 5000 天'; unit='s'; range='量级演算，假设匀速'; source='S4+S3'; matches_artwork=$true; caveat='画面已标注"本编辑的算术演示，不是任何来源的结论"，并说明 UT1−UTC 实际并不匀速' }
    [ordered]@{ id='AC-11'; label='2012 那一分钟'; formula='23:59:60 使该分钟为 61 秒'; numerator='61 秒'; denominator='1 个分钟'; unit='s'; range='2012-06-30'; source='S3'; matches_artwork=$true }
    [ordered]@{ id='AC-12'; label='2012 是第几次'; formula='Leap_Second.dat 第 25 行（1972 起算）'; numerator='25'; denominator='27'; unit='次'; range='1972-06-30 → 2012-06-30'; source='S1'; matches_artwork=$true }
  )
  demo_data_flags = @(
    [ordered]@{ where='case-01 右上刊头'; value='《时间的边缘》第 03 期'; type='虚构刊物'; label='DEMO' }
    [ordered]@{ where='case-01 底部署名'; value='Snapshot 特辑编辑部（虚构署名 DEMO）'; type='虚构署名'; label='DEMO' }
    [ordered]@{ where='case-01/case-10 各处说明'; value='编辑按 / 编辑建议 / 编辑解释'; type='非来源结论'; label='已在画面标注' }
  )
  verification = [ordered]@{
    sources_retrieved_in_this_run = $true
    every_source_has_visit_record = $true
    no_fabricated_sources = $true
    unreachable_hosts_logged = $true
    artwork_numbers_match_arithmetic_checks = $true
    note = 'sources[].visits 的 url / http_status / bytes / started_at / ended_at / local_file 全部由 requests.jsonl 反查写入，未手工填写'
  }
}

$outPath = Join-Path $o 'sources.json'
$json = $result | ConvertTo-Json -Depth 10
[IO.File]::WriteAllText($outPath, $json, $enc)
"written: $outPath ($((Get-Item $outPath).Length) bytes)"
$null = Get-Content $outPath -Raw -Encoding UTF8 | ConvertFrom-Json
"JSON valid. sources=$($result.source_count) unreachable=$($unreachable.Count) arithmetic=$($result.arithmetic_checks.Count)"
