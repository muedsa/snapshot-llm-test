#!/bin/sh
# Build a task DSL version and render it through the service.
# Usage: sh tmp/<run_id>/_suite/scripts/mk.sh <task> <ver> <gen-relative-path>
set -e
TASK=$1; VER=$2; GEN=$3
R=$(ls tmp | grep -E '^[0-9]{4}-.*-r[0-9]+$' | head -1)
python "$GEN" --ver "$VER" >/dev/null
python "tmp/$R/_suite/scripts/render.py" \
  --dsl "tmp/$R/$TASK/$VER.snapshot" \
  --out "tmp/$R/$TASK/$VER.png" \
  --log "tmp/$R/$TASK/requests.jsonl" \
  --req-id "$TASK-render-$VER" --task "$TASK" \
  --raw-error-dir "tmp/$R/$TASK"
