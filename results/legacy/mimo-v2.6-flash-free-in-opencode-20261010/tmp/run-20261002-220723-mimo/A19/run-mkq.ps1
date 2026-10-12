param([string]$Script, [string]$SceneJson, [string]$OutQuestions, [string]$OutAnswers)
try {
  & $Script -SceneJson $SceneJson -OutQuestions $OutQuestions -OutAnswers $OutAnswers
} catch {
  Write-Output ("ERR: " + $_.Exception.Message)
  Write-Output ("TYPE: " + $_.Exception.GetType().FullName)
  Write-Output $_.InvocationInfo.PositionMessage
  Write-Output $_.ScriptStackTrace
  if ($_.Exception.InnerException) { Write-Output ("INNER: " + $_.Exception.InnerException.Message) }
}
