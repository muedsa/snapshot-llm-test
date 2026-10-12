# A06 independent input review

Run: `20261002-204314-6f31`; task: A06.

Actually read TASK.md, AGENTS.md, task.json, inputs/graph.json, inputs/README.md, task run-config.json, root run-config.json, catalog.json. Inputs unchanged. This review uses only task input and saved independent computation; it does not assert any image has been viewed.

There are 14 nodes, 16 prerequisite edges, 2 feedback edges. Excluding feedback, Kahn sorting visits every node and the graph is acyclic. Layers represent earliest dependency depth (zero-based). Layer order is N01; N02/N03; N04/N05; N06/N07; N08; N09; N10; N11; N12; N13; N14. The two longest paths each contain 11 nodes and differ only in the content/layout branch (N05→N06) and data/chart branch (N04→N07).

Important semantic checks for the actual diagram:

- N03→N06 skips one layer. It must not look connected to N04 or N05 where it passes their layer.
- N04→N13 is a long forward prerequisite, not a feedback. It should run around nodes and be an unbroken solid route with a clear arrow into N13.
- Both feedback arrows return to N08. N09→N08 means failed first rendering returns to construction; N10→N08 means visual inspection discovers a problem that requires fixing the DSL. The separate ordinary edge N10→N11 remains in the DAG.
- Where two edges cross without a connection marker, they do not create a relationship.
- Every node ID and complete label must be visible; node text at least 22 and annotations at least 18.
- graph-audit.json must include the actual drawn position/route of each feedback edge, not only input semantics.

Preserved local read failure: an initial attempted TASK path `tasks/A06-dependency-map/TASK.md` did not exist. The catalog was then read and the correct `tasks/A06-dependency-graph/` path used. This was a local read error, not an HTTP request or Snapshot DSL/render failure.

Independent computation files: `audit-v001.cjs`, `independent-facts-v001.json`. Generated facts include SHA-256 of the original graph JSON, each node's input/output neighbors, all longest paths, skip-layer edges and exact feedback semantics.
