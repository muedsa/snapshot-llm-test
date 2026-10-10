# printed snippet parse verification

Each handbook page prints 16 verbatim lines of the matching example-0N.snapshot
plus one DSL-comment marker line, 17 lines total. This rebuilds exactly that
17-line text from the shipped example file and sends it to the service at 400x240
to prove the printed text is real, parseable DSL rather than decoration.
The marker line is an XML comment, so it must be skipped by the parser for the
snippet to load.

## printed-01  (17 lines, omits example-01.snapshot 11 12)
- source: outputs/run-20261002-220723-mimo/A17/example-01.snapshot (18 lines)
- request id: A17-printed01
- status: reused request A17-printed01 (HTTP 200, 2027.3 ms)
- result: rendered earlier in this run

## printed-02  (17 lines, omits example-02.snapshot 12 13)
- source: outputs/run-20261002-220723-mimo/A17/example-02.snapshot (18 lines)
- request id: A17-printed02
- status: rendered
- result: OK 200 1380.3 ms -> tmp\run-20261002-220723-mimo\A17\printed-02.png

## printed-03  (17 lines, omits example-03.snapshot 14 15)
- source: outputs/run-20261002-220723-mimo/A17/example-03.snapshot (18 lines)
- request id: A17-printed03
- status: rendered
- result: OK 200 2135.4 ms -> tmp\run-20261002-220723-mimo\A17\printed-03.png

## printed-04  (17 lines, omits example-04.snapshot 5 6)
- source: outputs/run-20261002-220723-mimo/A17/example-04.snapshot (18 lines)
- request id: A17-printed04
- status: rendered
- result: OK 200 1187 ms -> tmp\run-20261002-220723-mimo\A17\printed-04.png

