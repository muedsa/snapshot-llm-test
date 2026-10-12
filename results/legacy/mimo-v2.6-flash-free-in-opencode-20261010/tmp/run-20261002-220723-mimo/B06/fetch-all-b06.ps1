# fetch-all-b06.ps1 -- real documentation + research fetch for B06, logs every request
$ErrorActionPreference = 'Continue'
$dir = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\B06')
$fetch = Join-Path $dir 'fetch-b06.ps1'
$docsDir = Join-Path $dir 'docs'
$resDir  = Join-Path $dir 'research'
$log = Join-Path $dir 'requests.jsonl'
$utf8 = New-Object System.Text.UTF8Encoding($false)

$docs = @(
  ,@('B06-doc-01-ai-guide',    'https://open-snapshot.muedsa.com/ai-guide.md',                       'ai-guide.md')
  ,@('B06-doc-02-parser-tags', 'https://snapshot.muedsa.com/reference/parser-tags/',                 'doc-parser-tags.txt')
  ,@('B06-doc-03-painting',    'https://snapshot.muedsa.com/guides/painting/',                       'doc-painting.txt')
  ,@('B06-doc-04-enums',       'https://snapshot.muedsa.com/reference/enums/',                       'doc-enums.txt')
  ,@('B06-doc-05-transform',   'https://snapshot.muedsa.com/widgets/layout/transform/',              'doc-transform.txt')
  ,@('B06-doc-06-rendering',   'https://snapshot.muedsa.com/guides/rendering/',                      'doc-rendering.txt')
  ,@('B06-doc-07-decor-box',   'https://snapshot.muedsa.com/widgets/painting/decorated-box/',        'doc-decorated-box.txt')
  ,@('B06-doc-08-source-index','https://snapshot.muedsa.com/reference/source-index/',                'doc-source-index.txt')
  ,@('B06-doc-09-faq',         'https://snapshot.muedsa.com/reference/faq/',                         'doc-faq.txt')
)
$fonts = @('B06-font-01-list', 'https://open-snapshot.muedsa.com/fonts', 'fonts.json')
$res = @(
  ,@('B06-res-01-tiered-price', 'https://sousuo.www.gov.cn/search-gov/data?t=zhengcelibrary&q=%E5%B1%85%E6%B0%91%E7%94%B5%E4%BB%B7%20%E9%98%B6%E6%A2%AF%E7%94%B5%E4%BB%B7&n=10&p=1&sort=score&sortType=1', 'res-01-tiered-price.json')
  ,@('B06-res-02-price-tag',    'https://sousuo.www.gov.cn/search-gov/data?t=zhengcelibrary&q=%E6%98%8E%E7%A0%81%E6%A0%87%E4%BB%B7&n=10&p=1', 'res-02-price-tag.json')
  ,@('B06-res-03-label',        'https://sousuo.www.gov.cn/search-gov/data?t=zhengcelibrary&q=%E8%8D%AF%E5%93%81%E8%AF%B4%E6%98%8E%E4%B9%A6&n=10&p=1', 'res-03-label.json')
  ,@('B06-res-04-checkup',      'https://sousuo.www.gov.cn/search-gov/data?t=zhengcelibrary&q=%E5%81%A5%E5%BA%B7%E4%BD%93%E6%A3%80&n=10&p=1', 'res-04-checkup.json')
  ,@('B06-res-05-installment',  'https://sousuo.www.gov.cn/search-gov/data?t=zhengcelibrary&q=%E4%BF%A1%E7%94%A8%E5%8D%A1%E5%88%86%E6%9C%9F%20%E6%89%8B%E7%BB%A9%E8%B4%B9&n=10&p=1', 'res-05-installment.json')
  ,@('B06-res-06-deposit',      'https://sousuo.www.gov.cn/search-gov/data?t=zhengcelibrary&q=%E4%BD%8F%E6%88%BF%E7%A7%9F%E8%B5%81%20%E6%8A%BC%E9%87%91&n=10&p=1', 'res-06-deposit.json')
  ,@('B06-res-07-parcel',       'https://sousuo.www.gov.cn/search-gov/data?t=zhengcelibrary&q=%E5%BF%AB%E9%80%92%E6%9C%8D%E5%8A%A1&n=10&p=1', 'res-07-parcel.json')
  ,@('B06-res-08-parking',      'https://sousuo.www.gov.cn/search-gov/data?t=zhengcelibrary&q=%E6%9C%BA%E5%8A%A8%E8%BD%A6%E5%81%9C%E6%94%BE%E6%9C%8D%E5%8A%A1%E6%94%B6%E8%B4%B9&n=10&p=1', 'res-08-parking.json')
  ,@('B06-res-09-metro',        'https://sousuo.www.gov.cn/search-gov/data?t=zhengcelibrary&q=%E5%9F%8E%E5%B8%82%E8%BD%A8%E9%81%93%E4%BA%A4%E9%80%9A%20%E8%BF%90%E8%90%A5%E6%9C%8D%E5%8A%A1%E8%A7%84%E8%8C%83&n=10&p=1', 'res-09-metro.json')
  ,@('B06-res-10-weather',      'https://sousuo.www.gov.cn/search-gov/data?t=zhengcelibrary&q=%E9%99%8D%E6%B0%B4%E6%A6%82%E7%8E%87%20%E9%A2%84%E6%8A%A5&n=10&p=1', 'res-10-weather.json')
  ,@('B06-res-11-cma',          'https://www.cma.gov.cn/',                                            'res-11-cma.html')
  ,@('B06-res-12-nmpa',         'https://www.nmpa.gov.cn/',                                           'res-12-nmpa.html')
  ,@('B06-res-13-nhc',          'https://www.nhc.gov.cn/',                                            'res-13-nhc.html')
  ,@('B06-res-14-spb',          'https://www.spb.gov.cn/',                                            'res-14-spb.html')
  ,@('B06-res-15-samr',         'https://www.samr.gov.cn/',                                           'res-15-samr.html')
  ,@('B06-res-16-ndrc',         'https://www.ndrc.gov.cn/',                                           'res-16-ndrc.html')
  ,@('B06-res-17-govall-label', 'https://sousuo.www.gov.cn/search-gov/data?t=govall&q=%E7%94%A8%E8%8D%AF%E6%8C%87%E5%AF%BC&n=10&p=1', 'res-17-govall-label.json')
  ,@('B06-res-18-govall-deposit','https://sousuo.www.gov.cn/search-gov/data?t=govall&q=%E6%8A%BC%E9%87%91%20%E9%80%80%E7%A7%9F&n=10&p=1', 'res-18-govall-deposit.json')
)

function Run-One($entry, $outDir, $type) {
  $id = $entry[0]; $url = $entry[1]; $out = Join-Path $outDir $entry[2]
  & $fetch -Url $url -TaskId 'B06' -ReqId $id -OutPath $out -LogPath $script:log -Type $type
}

foreach ($d in $docs)  { Run-One $d $docsDir 'documentation' }
Run-One $fonts $docsDir 'fonts'
foreach ($r in $res)   { Run-One $r $resDir  'research' }

$rows = [IO.File]::ReadAllLines($log)
$objs = @(); foreach ($l in $rows) { if ($l.Trim()) { $objs += ($l | ConvertFrom-Json) } }
"requests=$($objs.Count)"
$objs | Group-Object type | ForEach-Object { "  $($_.Name)=$($_.Count)" }
$objs | Group-Object http_status | ForEach-Object { "  http=$($_.Name) count=$($_.Count)" }
$objs | Where-Object { $_.http_status -ne 200 } | ForEach-Object { "  FAIL $($_.id)  $($_.http_status)  $($_.url)" }
