# Real local orchestration limitation

First real invocation for A22 round-01 failed with `spawnSync ... node.exe EPERM` before the publisher process began. The unchanged script and actual error are preserved in `A22/round-01/round-orchestration-000001.json` and `orchestration-command-result-v001.json`. This wrapper is not considered operationally verified on this sandbox.

Root recovered without escalation by invoking the established publisher directly through exec_command, checking its success, then recording the true round-completed boundary, invoking strict archive-round-metrics directly, checking wx archive success, and recording round-archive-verified. Real publication/archive tool outputs are retained in A22 round-01. Each dependent operation was sequential and checked. No rollback, deletion or overwrite occurred. The limitation did not affect Snapshot rendering or final image bytes. Future rounds in this environment use that direct sequence.
