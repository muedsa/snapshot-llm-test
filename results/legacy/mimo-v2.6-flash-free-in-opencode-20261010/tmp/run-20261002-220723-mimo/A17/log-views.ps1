$ErrorActionPreference = "Stop"
$T = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\A17')
$L = Join-Path $T "log-iter.ps1"
$now = "2026-10-04T16:58:00+08:00"
$reqs = Get-Content (Join-Path $T "requests.jsonl") | ForEach-Object { $_ | ConvertFrom-Json }
function Dur($id) { $r = $reqs | Where-Object { $_.id -eq $id } | Select-Object -Last 1; if ($r) { return $r.duration_ms } else { return $null } }

# seq 39/40 recorded an attempt to read these two pages with the local image tool; that tool
# returned stale/rotating frames for that path, so the content was confirmed through a
# delegated viewer instead. These rows record the view that actually landed.
$rows = @(
  @{ v="handbook-03-v03"; p="handbook-03-v03"; req="A17-pg03d";
     obs="delegated viewer read the delivered PNG literally: badge 'P3 · 文本与颜色', title '原样保留的文本与尾随透明度', desc '谁修剪空白、谁保留空白，以及颜色末尾两位', heading '可复制运行：16 行原文 + 1 行省略标注（文件共 18 行）', marker '<!--省略 example-03.snapshot 第 14、15 行（两条图例行）；完整文件共 18 行 -->', 4 pitfall bullets including '&amp; 不会被解码，会原样显示' and 'Raw 写在 Text 之外会直接 400', 5 right-column bullets, footer 'A17 文档手册 · 第 3 / 4 页 · 文本与颜色'" },
  @{ v="handbook-04-v03"; p="handbook-04-v03"; req="A17-pg04d";
     obs="delegated viewer read the delivered PNG literally: badge 'P4 · 滤镜与自检', title '背景滤镜、子树滤镜与自检', desc '先分清滤的是身后还是自己，再逐层做验证', heading '可复制运行：16 行原文 + 1 行省略标注（文件共 18 行）', marker '<!--省略 example-04.snapshot 第 5、6 行（两条色带）；完整文件共 18 行 -->', 4 pitfall bullets, 5 right-column bullets including '毛玻璃通常需要 ClipRect / ClipRRect 限区', footer 'A17 文档手册 · 第 4 / 4 页 · 滤镜与自检'" }
)

foreach ($r in $rows) {
  & $L -Version ($r.v + "-view2") -Parent $r.p -Type "visual" `
       -Purpose "content-verify the delivered page after the local read tool returned stale frames for that path" `
       -Dsl ("tmp/run-20261002-220723-mimo/A17/" + $r.v + ".snapshot") `
       -Image ("tmp/run-20261002-220723-mimo/A17/" + $r.v + ".png") `
       -RequestId $r.req -HttpStatus 200 -DurationMs (Dur $r.req) `
       -ViewedAt $now -ViewMethod "delegated-general-subagent" `
       -Observed $r.obs -Change "none (verification only)" -Category "verification" | Out-Null
}
Write-Output ("iterations rows = " + (Get-Content (Join-Path $T "iterations.jsonl")).Count)
