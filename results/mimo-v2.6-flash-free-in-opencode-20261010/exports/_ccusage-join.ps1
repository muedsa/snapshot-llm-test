param(
  [Parameter(Mandatory = $true)][string]$Root,
  [Parameter(Mandatory = $true)][string]$CcRaw,
  [Parameter(Mandatory = $true)][string]$SessionsJson,
  [Parameter(Mandatory = $true)][string]$OutMd,
  [string]$ParentId = "ses_f031101b7ffeD7ubHPRzDVybL9"
)

$ErrorActionPreference = "Stop"

$cc = (Get-Content $CcRaw -Raw | ConvertFrom-Json)
$all = (Get-Content $SessionsJson -Raw | ConvertFrom-Json)

$meta = @{}
foreach ($s in $all.data) { $meta[$s.id] = $s }

$usage = @{}
foreach ($u in $cc.sessions) { $usage[$u.sessionId] = $u }

$children = @($all.data | Where-Object { $_.parentID -eq $ParentId } | Sort-Object { $_.time.created })
$parent = $meta[$ParentId]

function U([string]$id) {
  if ($usage.ContainsKey($id)) { return $usage[$id] } else { return $null }
}
function N([long]$v) { return $v.ToString("N0") }
function M([double]$v) { return ('${0:F6}' -f $v) }
# reasoning tokens = totalTokens - (input + output + cache read + cache write)
function Get-Reasoning($u) {
  $sum = [long]$u.inputTokens + [long]$u.outputTokens + [long]$u.cacheReadTokens + [long]$u.cacheCreationTokens
  $r = [long]$u.totalTokens - $sum
  if ($r -lt 0) { return 0L }
  return $r
}

$scope = @($children)
if ($parent) { $scope = @($parent) + $scope }

$totIn = 0L; $totOut = 0L; $totCR = 0L; $totCW = 0L; $totR = 0L; $totAll = 0L; $totCost = 0.0
$childTotIn = 0L; $childTotOut = 0L; $childTotCR = 0L; $childTotCW = 0L; $childTotR = 0L; $childTotAll = 0L; $childTotCost = 0.0

foreach ($s in $scope) {
  $u = U $s.id
  if (-not $u) { continue }
  $totIn += [long]$u.inputTokens; $totOut += [long]$u.outputTokens
  $totCR += [long]$u.cacheReadTokens; $totCW += [long]$u.cacheCreationTokens
  $totR += (Get-Reasoning $u)
  $totAll += [long]$u.totalTokens; $totCost += [double]$u.totalCost
}
foreach ($s in $children) {
  $u = U $s.id
  if (-not $u) { continue }
  $childTotIn += [long]$u.inputTokens; $childTotOut += [long]$u.outputTokens
  $childTotCR += [long]$u.cacheReadTokens; $childTotCW += [long]$u.cacheCreationTokens
  $childTotR += (Get-Reasoning $u)
  $childTotAll += [long]$u.totalTokens; $childTotCost += [double]$u.totalCost
}

$models = @{}
foreach ($s in $scope) {
  $u = U $s.id
  if (-not $u) { continue }
  foreach ($m in $u.modelBreakdowns) {
    if (-not $models.ContainsKey($m.modelName)) {
      $models[$m.modelName] = [pscustomobject]@{ name=$m.modelName; input=0L; output=0L; cr=0L; cw=0L; reasoning=0L; total=0L; cost=0.0; sessions=0 }
    }
    $e = $models[$m.modelName]
    $e.input += [long]$m.inputTokens
    $e.output += [long]$m.outputTokens
    $e.cr += [long]$m.cacheReadTokens
    $e.cw += [long]$m.cacheCreationTokens
    $e.total += ([long]$m.inputTokens + [long]$m.outputTokens + [long]$m.cacheReadTokens + [long]$m.cacheCreationTokens)
    $e.cost += [double]$m.cost
    $e.sessions += 1
  }
  # attribute the session's reasoning tokens to its single model (all sessions here use one model)
  $used = @($u.modelsUsed)
  if ($used.Count -eq 1 -and $models.ContainsKey($used[0])) {
    $models[$used[0]].reasoning += (Get-Reasoning $u)
    $models[$used[0]].total += (Get-Reasoning $u)
  }
}

$scopeIds = @{}
foreach ($s in $scope) { $scopeIds[$s.id] = $true }
$unmatched = @($cc.sessions | Where-Object { -not $scopeIds.ContainsKey($_.sessionId) })
$noUsage = @($children | Where-Object { -not (U $_.id) })

$lines = New-Object System.Collections.Generic.List[string]
$add = { param($t) $lines.Add($t) }

$parentLabel = ''
if ($parent) { $parentLabel = '（' + $parent.title + '）' }

& $add '# OpenCode 会话 Token 消耗汇总'
& $add ''
& $add ('- 生成时间：{0}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss K'))
& $add ('- 统计来源：`npx ccusage@latest opencode session --json --no-color`（原始输出见 [_ccusage_raw.json](_ccusage_raw.json)）')
& $add ('- 会话元数据：`opencode-cli.exe api get /api/session`')
& $add ('- 父会话：`{0}`{1}' -f $ParentId, $parentLabel)
& $add ('- 统计范围：父会话 + 其 {0} 个子线程（`parentID` = `{1}`）' -f $children.Count, $ParentId)
& $add '- 估算成本为 ccusage 依据 LiteLLM 价格表计算；`mimo-v2.6-flash-free` 为免费模型，金额仅供参照。'
& $add ''
& $add '## 总体汇总（父会话 + 全部子线程）'
& $add ''
& $add '| 指标 | 数值 |'
& $add '| --- | ---: |'
& $add ('| 会话数 | {0} |' -f $scope.Count)
& $add ('| Input tokens | {0} |' -f (N $totIn))
& $add ('| Output tokens | {0} |' -f (N $totOut))
& $add ('| Reasoning tokens（由总 tokens 差额推算） | {0} |' -f (N $totR))
& $add ('| Cache read tokens | {0} |' -f (N $totCR))
& $add ('| Cache write tokens | {0} |' -f (N $totCW))
& $add ('| 总 tokens | {0} |' -f (N $totAll))
& $add ('| 估算成本 | {0} |' -f (M $totCost))
& $add ''
& $add '### 子线程小计'
& $add ''
& $add '| 指标 | 数值 |'
& $add '| --- | ---: |'
& $add ('| 子线程数 | {0} |' -f $children.Count)
& $add ('| Input tokens | {0} |' -f (N $childTotIn))
& $add ('| Output tokens | {0} |' -f (N $childTotOut))
& $add ('| Reasoning tokens（由总 tokens 差额推算） | {0} |' -f (N $childTotR))
& $add ('| Cache read tokens | {0} |' -f (N $childTotCR))
& $add ('| Cache write tokens | {0} |' -f (N $childTotCW))
& $add ('| 总 tokens | {0} |' -f (N $childTotAll))
& $add ('| 估算成本 | {0} |' -f (M $childTotCost))
& $add ''
& $add '## 子线程明细'
& $add ''
& $add '| # | 创建时间 (UTC+8) | session id | 标题 | agent | 模型 | Input | Output | Reasoning | Cache read | Cache write | 合计 | 占子线程总量 | 估算成本 |'
& $add '| ---: | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |'

$i = 0
foreach ($s in $children) {
  $i++
  $u = U $s.id
  $created = ([DateTimeOffset]::FromUnixTimeMilliseconds([long]$s.time.created)).ToOffset([TimeSpan]::FromHours(8)).ToString('yyyy-MM-dd HH:mm')
  $title = "$($s.title)".Replace('|', '\|')
  if ($u) {
    $share = 0.0
    if ($childTotAll -gt 0) { $share = ([double]$u.totalTokens / $childTotAll * 100) }
    $modelsUsed = ($u.modelsUsed -join ', ')
    & $add ('| {0} | {1} | `{2}` | {3} | {4} | {5} | {6} | {7} | {8} | {9} | {10} | {11} | {12:F1}% | {13} |' -f `
      $i, $created, $s.id, $title, $s.agent, $modelsUsed, `
      (N $u.inputTokens), (N $u.outputTokens), (N (Get-Reasoning $u)), (N $u.cacheReadTokens), (N $u.cacheCreationTokens), `
      (N $u.totalTokens), $share, (M $u.totalCost))
  } else {
    & $add ('| {0} | {1} | `{2}` | {3} | {4} | - | - | - | - | - | - | - | 0.0% | - |' -f $i, $created, $s.id, $title, $s.agent)
  }
}
& $add ('| | | **合计** | | | | **{0}** | **{1}** | **{2}** | **{3}** | **{4}** | **{5}** | **100.0%** | **{6}** |' -f `
  (N $childTotIn), (N $childTotOut), (N $childTotR), (N $childTotCR), (N $childTotCW), (N $childTotAll), (M $childTotCost))
& $add ''

if ($parent) {
  $pu = U $parent.id
  & $add '## 父会话本身（不计入上面的子线程合计）'
  & $add ''
  & $add '| session id | 标题 | agent | Input | Output | Reasoning | Cache read | Cache write | 合计 | 估算成本 |'
  & $add '| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |'
  if ($pu) {
    & $add ('| `{0}` | {1} | {2} | {3} | {4} | {5} | {6} | {7} | {8} | {9} |' -f $parent.id, "$($parent.title)".Replace('|','\|'), $parent.agent, `
      (N $pu.inputTokens), (N $pu.outputTokens), (N (Get-Reasoning $pu)), (N $pu.cacheReadTokens), (N $pu.cacheCreationTokens), (N $pu.totalTokens), (M $pu.totalCost))
  } else {
    & $add ('| `{0}` | {1} | {2} | - | - | - | - | - | - | - |' -f $parent.id, $parent.title, $parent.agent)
  }
  & $add ''
}

& $add '## 模型明细（父会话 + 子线程）'
& $add ''
& $add '| 模型 | 会话数 | Input | Output | Reasoning | Cache read | Cache write | 合计 | 估算成本 |'
& $add '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |'
foreach ($m in ($models.Values | Sort-Object -Property total -Descending)) {
  & $add ('| {0} | {1} | {2} | {3} | {4} | {5} | {6} | {7} | {8} |' -f $m.name, $m.sessions, (N $m.input), (N $m.output), (N $m.reasoning), (N $m.cr), (N $m.cw), (N $m.total), (M $m.cost))
}
& $add ''

& $add '## 备注与数据完整性'
& $add ''
& $add ('- 统计范围：父会话 1 个 + 子线程 {0} 个，共 {1} 个会话，均按 `sessionId` 与 ccusage 用量记录一一对应。' -f $children.Count, $scope.Count)
if ($noUsage.Count -gt 0) {
  $ids = ($noUsage | ForEach-Object { '`' + $_.id + '`' }) -join ', '
  & $add ('- 范围内但 ccusage 无用量记录的会话 {0} 个：{1}' -f $noUsage.Count, $ids)
} else {
  & $add ('- 范围内 {0} 个会话在 ccusage 中均有用量记录，无缺失项。' -f $scope.Count)
}
& $add '- `Reasoning` 列为 `totalTokens` 减去 input/output/cache 四项之和的差额（ccusage JSON 未单列 reasoning 字段），因此各列相加等于“合计”。'
& $add '- `Cache write tokens` 全为 0，说明这些会话未产生缓存写入计费。'
& $add ''
& $add '本文件由 [_ccusage-join.ps1](_ccusage-join.ps1) 生成：以 [_ccusage_raw.json](_ccusage_raw.json)（ccusage 输出）与 `/api/session` 元数据按 `sessionId` 关联；token 数为各会话累计值。'

[System.IO.File]::WriteAllLines($OutMd, $lines, (New-Object System.Text.UTF8Encoding($false)))
"written: $OutMd ($($lines.Count) lines)"
