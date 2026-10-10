$ErrorActionPreference = 'Stop'
$root = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'outputs\run-20261002-220723-mimo')
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add('http://127.0.0.1:8765/')
$listener.Start()
$logPath = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\B02\httpsrv.log')
[IO.File]::WriteAllText($logPath, "started " + (Get-Date).ToString('o') + "`n")
$utf8 = New-Object System.Text.UTF8Encoding($false)
while ($listener.IsListening) {
  $ctx = $listener.GetContext()
  $req = $ctx.Request
  $resp = $ctx.Response
  try {
    $rel = [Uri]::UnescapeDataString($req.Url.AbsolutePath.TrimStart('/'))
    $full = Join-Path $root ($rel -replace '/', '\')
    if (Test-Path $full -PathType Leaf) {
      $bytes = [IO.File]::ReadAllBytes($full)
      $ext = [IO.Path]::GetExtension($full).ToLower()
      $ct = 'application/octet-stream'
      if ($ext -eq '.png') { $ct = 'image/png' }
      elseif ($ext -eq '.jpg' -or $ext -eq '.jpeg') { $ct = 'image/jpeg' }
      elseif ($ext -eq '.html') { $ct = 'text/html; charset=utf-8' }
      elseif ($ext -eq '.md' -or $ext -eq '.snapshot' -or $ext -eq '.json' -or $ext -eq '.jsonl') { $ct = 'text/plain; charset=utf-8' }
      $resp.StatusCode = 200
      $resp.ContentType = $ct
      $resp.ContentLength64 = $bytes.Length
      $resp.OutputStream.Write($bytes, 0, $bytes.Length)
      [IO.File]::AppendAllText($logPath, "200 $rel`n", $utf8)
    } else {
      $msg = $utf8.GetBytes('not found: ' + $rel)
      $resp.StatusCode = 404
      $resp.ContentLength64 = $msg.Length
      $resp.OutputStream.Write($msg, 0, $msg.Length)
      [IO.File]::AppendAllText($logPath, "404 $rel`n", $utf8)
    }
  } catch {
    try { $resp.StatusCode = 500 } catch {}
    [IO.File]::AppendAllText($logPath, "ERR $($_.Exception.Message)`n", $utf8)
  }
  try { $resp.Close() } catch {}
}
