"""One-shot task wrap-up: iterations log, task-metrics.json, suite-state update."""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, r'tmp\20261004-182918\_suite')
import finalize  # noqa: E402
import state as S  # noqa: E402
import snapkit  # noqa: E402


def wrapup(task_id, started, first_image, ended, iterations, artifacts,
           visual_evidence, unresolved=None, notes=None, status='completed',
           rounds=None, cases=None):
    snapkit.configure(task_id, os.path.join(S.OUT_ROOT, task_id),
                      os.path.join(S.TMP_ROOT, task_id))
    for it in iterations:
        v, par, kind, dsl, img, viewed, obs, chg, complete = it
        snapkit.log_iteration(
            version=v, parent=par, kind=kind, dsl_file=dsl, image_file=img,
            viewed_at=viewed, observed=obs, changes=chg,
            compared=('accepted' if complete else 'not accepted'), complete=complete)
    m = finalize.build(task_id, started, first_image, ended)
    S.finish_task(task_id, status, artifacts=artifacts,
                  visual_evidence=visual_evidence, unresolved=unresolved or [],
                  rounds=rounds or ['round-01'], cases=cases or [], notes=notes)
    return m