$objs = @(1..64 | ForEach-Object { [pscustomobject]@{ row = [int](($_ - 1) / 8); color = 'blue'; shape = 'circle' } })
try {
  $x = @(0..7 | ForEach-Object {
      $rr = $_
      $ro = @($objs | Where-Object { $_.row -eq $rr })
      [pscustomobject]@{
        row = $rr
        colors = @($ro | ForEach-Object { $_.color } | Sort-Object -Unique)
        shapes = @($ro | ForEach-Object { $_.shape } | Sort-Object -Unique)
        n_colors = @($ro | ForEach-Object { $_.color } | Sort-Object -Unique).Count
        n_shapes = @($ro | ForEach-Object { $_.shape } | Sort-Object -Unique).Count
      }
    })
  "OK count=" + $x.Count
} catch {
  "ERR: " + $_.Exception.Message
  $_.InvocationInfo.PositionMessage
}
