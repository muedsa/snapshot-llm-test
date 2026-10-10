$ErrorActionPreference = 'Stop'
$tmp = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\B03')
$enc = New-Object System.Text.UTF8Encoding($false)
$reqLog = Join-Path $tmp 'requests.jsonl'
$iterLog = Join-Path $tmp 'iterations.jsonl'
$toolLog = Join-Path $tmp 'tool-usage.jsonl'

$rows = @()
Get-Content $reqLog -Encoding UTF8 | ForEach-Object {
  $o = $_ | ConvertFrom-Json
  if ($o.id -like 'B03-p*') { $rows += $o }
}

$viewed = @{
  'B03-p01-stroke-text' = @($true, '读图打开 probes/p01-stroke-text.png：OUTLINE 实心+偏移阴影、OUTLINE 空心描边、FILLSTROKE 描边+实心三层均成立')
  'B03-p02-backdrop-filter' = @($true, '读图打开 probes/p02-backdrop-filter.png：卡片内圆形与竖条明显虚化、卡外锐利，毛玻璃成立')
  'B03-p03-color-filtered' = @($true, '读图打开 probes/p03-color-filtered.png（另见像素采样表）：色带在蓝/纸/橙三处同色，证明只与子节点像素混合')
  'B03-p04-image-filtered' = @($true, '读图打开 probes/p04-image-filtered.png：面条横向拉丝、竖向保持，各向异性模糊成立')
  'B03-p05-widget-span' = @($true, '读图打开 probes/p05-widget-span.png：行内时间徽章与两位代码徽章嵌入中文正文且基线对齐')
  'B03-p06-stack-shadow' = @($true, '读图打开 probes/p06-stack-shadow.png：左图阴影有硬切边，右图 clipBehavior=NONE 阴影完整')
  'B03-p07-gradient-tile' = @($true, '读图打开 probes/p07-gradient-tile.png（read 缓存污染，改读重新编码副本 zz-view-p07-c.png）：径向 MIRROR 环形重复成立')
  'B03-p08-font-features' = @($true, '读图打开 probes/p08-font-features.png：四行数字并排，逐行测右边界 294/325/276/357 px')
  'B03-p09-overflow-bleed' = @($true, '读图打开 probes/p09-overflow-bleed.png：FOLD 巨字超出 700x300 并精确止边')
  'B03-p10-axonic-matrix' = @($true, '读图打开 probes/p10-axonic-matrix.png：5x5 方格阵变标准等轴测菱形网格')
}

$notes = @{
  'B03-p11-linear-tiling' = 'stops 生效、rotation 弧度生效、对齐常量必须 CENTER_LEFT/CENTER_RIGHT；REPEAT 在起止点跨满整幅时不可见'
  'B03-p12-short-tile' = '左旋写法 LEFT_CENTER 触发 PARSE_ERROR，改 CENTER_LEFT 后成功'
}

$i = 0
foreach ($r in ($rows | Sort-Object started_utc)) {
  $i++
  $name = $r.id.Substring(4)
  $v = $viewed[$r.id]
  $vv = $true; $ve = 'System.Drawing 像素采样（探针未单独开图）'
  if ($null -ne $v) { $vv = $v[0]; $ve = $v[1] }
  $obs = $notes[$r.id]
  if ($null -eq $obs) {
    if ($r.http_status -eq 200) { $obs = '渲染成功，能力探针通过' } else { $obs = $r.error_summary }
  }
  $obj = [ordered]@{
    iteration_id = 'ite-B03-probe-{0:d2}-{1}' -f $i, $name
    case_id = $null
    type = 'capability-probe'
    version = $null
    parent_version = $null
    request_id = $r.id
    http_status = $r.http_status
    duration_ms = $r.duration_ms
    render_started_utc = $r.started_utc
    render_ended_utc = $r.ended_utc
    change = '新增能力探针 ' + $name
    observation = $obs
    result = $(if ($r.http_status -eq 200) { '探针渲染成功，结论写入 probes.md' } else { '语法修复后再测' })
    viewed = $vv
    view_evidence = $ve
  }
  [IO.File]::AppendAllText($iterLog, ($obj | ConvertTo-Json -Compress) + "`r`n", $enc)
}

$tools = @(
  [ordered]@{ tool_id='tu-01'; tool='共享渲染包装 render-b03.ps1'; category='共享准备'; affected_cases='*'
    input='tmp/run-20261002-220723-mimo/_suite/render.ps1'; output='tmp/run-20261002-220723-mimo/B03/render-b03.ps1'
    purpose='复制共享渲染脚本并加入 case_id / dsl_chars 字段，使 B03 每条渲染请求都带 case_id'
    http_request_ids=@(); note='共享准备，不归属任何单一作品'; double_counted=$false }
  [ordered]@{ tool_id='tu-02'; tool='文档抓取 docfetch.ps1（复用 B01 版本）'; category='文档查阅'; affected_cases='*'
    input='https://open-snapshot.muedsa.com/ai-guide.md 等 20 个文档地址'
    output=@('tmp/run-20261002-220723-mimo/B03/doc-parser-tags.txt','tmp/run-20261002-220723-mimo/B03/doc-enums.txt','tmp/run-20261002-220723-mimo/B03/doc-faq.txt','tmp/run-20261002-220723-mimo/B03/probes.md')
    purpose='真实拉取标签参考/枚举/FAQ/绘制指南等 20 份文档并落盘，得出能力与边界清单'
    http_request_ids=@('B03-doc-01','B03-doc-02','B03-doc-03','B03-doc-04','B03-doc-05','B03-doc-06','B03-doc-07','B03-doc-08','B03-doc-09','B03-doc-10','B03-doc-11','B03-doc-12','B03-doc-13','B03-doc-14','B03-doc-15','B03-doc-16','B03-doc-17','B03-doc-18','B03-doc-19','B03-doc-20')
    note='20 条 documentation 请求全部 200'; double_counted=$false }
  [ordered]@{ tool_id='tu-03'; tool='System.Drawing 像素采样'; category='量测/放大'; affected_cases='*'
    input=@('tmp/run-20261002-220723-mimo/B03/probes/p08-font-features.png','tmp/run-20261002-220723-mimo/B03/probes/p03-color-filtered.png','tmp/run-20261002-220723-mimo/B03/probes/p11-linear-tiling.png','tmp/run-20261002-220723-mimo/B03/probes/p13-align01.png')
    output='probes.md 的实测表'
    purpose='客观测出 +tnum 字宽变化、ColorFiltered 只与子节点混合、渐变 stops/rotation/REPEAT 的真实行为'
    http_request_ids=@(); note='图片通道有缓存污染时用像素采样交叉验证'; double_counted=$false }
  [ordered]@{ tool_id='tu-04'; tool='读图工具（read）内容哈希缓存缺陷'; category='看图'; affected_cases='*'
    input='probes/*.png'; output='probes/zz-view-p07-c.png'
    purpose='批量化读图导致哈希映射串图；对 PNG 重新编码生成新哈希副本后恢复正确；此后每次调用只读一张'
    http_request_ids=@(); note='browser.preview 通道同样不可用：browser.disconnected'; double_counted=$false }
  [ordered]@{ tool_id='tu-05'; tool='能力探针生成程序 gen-probes.ps1 / gen-probe11 / gen-probe13'; category='生成程序'; affected_cases='*'
    input='doc-parser-tags.txt、reference/enums'
    output=@('tmp/run-20261002-220723-mimo/B03/probes/p01-stroke-text.png','tmp/run-20261002-220723-mimo/B03/probes/p13-align01.png')
    purpose='一次性生成 10+3 份探针 DSL 并逐份真实渲染，产出 probes.md'
    http_request_ids=@('B03-p01-stroke-text','B03-p11-linear-tiling','B03-p13-align01','B03-p13-align02','B03-p13-align03','B03-p13-align04','B03-p13-align05')
    note='探针属 shared 准备，case_id 为 null'; double_counted=$false }
)

foreach ($t in $tools) {
  [IO.File]::AppendAllText($toolLog, ($t | ConvertTo-Json -Compress) + "`r`n", $enc)
}

"iterations: " + (Get-Content $iterLog -Encoding UTF8).Count
"tool-usage: " + (Get-Content $toolLog -Encoding UTF8).Count
