$ErrorActionPreference = 'Stop'
'--- default aliases starting with r/t ---'
Get-Alias | Where-Object { $_.Definition -match '^(r|t)$' -or $_.Name -match '^[rt]$' } | Format-Table Name,Definition -AutoSize | Out-String
'--- function R definition ---'
function R([double]$x,[double]$y,[double]$w,[double]$h,[string]$bg,[string]$border,[int]$rad) { return 'ok' }
function T([double]$x,[double]$y,[double]$w,[double]$h,[int]$fs,[string]$col,[string]$al,[bool]$bold,[string]$txt) { return 'ok' }
$cb = (Get-Command -Name R -CommandType Function).ScriptBlock
'R param count: ' + $cb.ParamBlock.Parameters.Count
$cb2 = (Get-Command -Name T -CommandType Function).ScriptBlock
'T param count: ' + $cb2.ParamBlock.Parameters.Count
'R call: ' + (R 280.0 160.0 1040.0 760.0 '#FFFFFF' ('2 SOLID ' + '#475569') 0)
