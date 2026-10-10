param([string]$Script, [string]$OutDsl, [string]$OutGeom, [int]$Seed = 20261004)
try {
  & $Script -Seed $Seed -OutDsl $OutDsl -OutGeom $OutGeom
} catch {
  Write-Output ("ERR: " + $_.Exception.Message)
  Write-Output ("TYPE: " + $_.Exception.GetType().FullName)
  Write-Output $_.InvocationInfo.PositionMessage
  Write-Output $_.ScriptStackTrace
  if ($_.Exception.InnerException) { Write-Output ("INNER: " + $_.Exception.InnerException.Message) }
}
