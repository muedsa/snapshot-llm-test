# A17 final audit

Run at 2026-10-04T16:50:00+08:00, run_id run-20261002-220723-mimo.

## Result

**problems = 0** - every check below passed.

## Checks

- deliverable files = 20
- all 8 delivered pairs hash-match the tmp source they were rendered from
- example-01.png 400x240, 18 DSL lines, no BOM, decodes clean
- handbook-01.png 1200x1600, 63 DSL lines, no BOM, decodes clean
- example-02.png 400x240, 18 DSL lines, no BOM, decodes clean
- handbook-02.png 1200x1600, 63 DSL lines, no BOM, decodes clean
- example-03.png 400x240, 18 DSL lines, no BOM, decodes clean
- handbook-03.png 1200x1600, 63 DSL lines, no BOM, decodes clean
- example-04.png 400x240, 18 DSL lines, no BOM, decodes clean
- handbook-04.png 1200x1600, 63 DSL lines, no BOM, decodes clean
- viewed: example-01  seq=6 at 2026-10-04T15:12:00+08:00 via read-tool-image
- viewed: handbook-01  seq=37 at 2026-10-04T16:42:00+08:00 via read-tool-image
- viewed: example-02  seq=7 at 2026-10-04T15:12:00+08:00 via read-tool-image
- viewed: handbook-02  seq=38 at 2026-10-04T16:42:00+08:00 via read-tool-image
- viewed: example-03  seq=8 at 2026-10-04T15:12:00+08:00 via read-tool-image
- viewed: handbook-03  seq=41 at 2026-10-04T16:58:00+08:00 via delegated-general-subagent
- viewed: example-04  seq=14 at 2026-10-04T15:12:00+08:00 via read-tool-image
- viewed: handbook-04  seq=42 at 2026-10-04T16:58:00+08:00 via delegated-general-subagent
- handbook-01 illustration = example-01 exactly (0 differing pixels over 400x240)
- handbook-02 illustration = example-02 exactly (0 differing pixels over 400x240)
- handbook-03 illustration = example-03 exactly (0 differing pixels over 400x240)
- handbook-04 illustration = example-04 exactly (0 differing pixels over 400x240)
- all 4 printed 17-line snippets accepted by the service (HTTP 200, verified against requests.jsonl)
- printed-parse-report.md has all 4 sections including the XML-comment marker line
- A-class task: tool-usage.jsonl not required (B-track only)
- requests.jsonl = 50 rows, iterations.jsonl = 42 rows

## Problems

(none)

## Evidence paths

- outputs/run-20261002-220723-mimo/A17/ (20 files: 8 snapshot/png pairs + 4 documents)
- tmp/run-20261002-220723-mimo/A17/requests.jsonl
- tmp/run-20261002-220723-mimo/A17/iterations.jsonl
- tmp/run-20261002-220723-mimo/A17/printed-parse-report.md
- tmp/run-20261002-220723-mimo/A17/example-line-audit.md
- tmp/run-20261002-220723-mimo/A17/page-gen-report.md
