param([string]$Root = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\A16'), [int]$Port = 8123)
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$Port/")
$listener.Start()
"listening on $Port"
while ($listener.IsListening) {
  try {
    $ctx = $listener.GetContext()
    $name = [System.IO.Path]::GetFileName($ctx.Request.Url.LocalPath)
    $file = Join-Path $Root $name
    if ($name -and [System.IO.File]::Exists($file)) {
      $bytes = [System.IO.File]::ReadAllBytes($file)
      $ctx.Response.ContentType = "image/png"
      $ctx.Response.ContentLength64 = $bytes.Length
      $ctx.Response.OutputStream.Write($bytes, 0, $bytes.Length)
    } else {
      $msg = [System.Text.Encoding]::UTF8.GetBytes("not found")
      $ctx.Response.StatusCode = 404
      $ctx.Response.OutputStream.Write($msg, 0, $msg.Length)
    }
    $ctx.Response.Close()
  } catch { }
}
