$a = "plain 中文 “curly” end"
Write-Output ("A len=" + $a.Length)
$b = 'single 中文 “curly” end'
Write-Output ("B len=" + $b.Length)
$arr = @(
  "element1 中文 “curly” tail",
  "element2"
)
Write-Output ("C count=" + $arr.Count)
