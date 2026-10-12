# A01–A21 阶段审计修正 v002

结果：passed_with_documented_audit_reader_correction。2026-10-05T12:04:42.175Z → 2026-10-05T12:04:43.866Z。

本文件明确 supersedes-v001。原 progress-audit-through-A21-v001.json/md 保留且SHA256未变。原三条“round record time lies outside actual boundaries”属于审计读取器漏掉 iterations.recorded_at 的误报；任务记录、轮事件和归档指标从未修改。

实际重新核验 648 个保护文件SHA、188 个指定文件和 51 组原PNG/DSL/响应/提交/归档版本字节链，均保持。没有新HTTP、render、view或像素分析；不触A22文件，不修改状态、outputs、报告或指标。

|轮次|真实start UTC|真实completed UTC|history / completed|recorded_at在界内|
|---|---|---|---:|---|
|round-01|2026-10-05T01:19:23.342Z|2026-10-05T01:27:28.541Z|6 / 2|通过|
|round-02|2026-10-05T01:29:17.831Z|2026-10-05T01:37:19.969Z|6 / 2|通过|
|round-03|2026-10-05T01:39:20.177Z|2026-10-05T01:49:59.692Z|6 / 2|通过|

六条原被误判记录：

- A21-iteration-000005：2026-10-05T01:22:19.889Z，字段 recorded_at，round-01 真实边界内；原读取结果没有time字段。
- A21-iteration-000006：2026-10-05T01:22:19.898Z，字段 recorded_at，round-01 真实边界内；原读取结果没有time字段。
- A21-iteration-000011：2026-10-05T01:31:15.499Z，字段 recorded_at，round-02 真实边界内；原读取结果没有time字段。
- A21-iteration-000012：2026-10-05T01:31:15.503Z，字段 recorded_at，round-02 真实边界内；原读取结果没有time字段。
- A21-iteration-000017：2026-10-05T01:41:38.338Z，字段 recorded_at，round-03 真实边界内；原读取结果没有time字段。
- A21-iteration-000018：2026-10-05T01:41:38.342Z，字段 recorded_at，round-03 真实边界内；原读取结果没有time字段。

18条iteration history、六条completed记录与不可覆盖archive history完全对应；请求起止、版本time、viewed_at、registered_at等实际字段也核在界内。三个start/completed边界与轮指标精确一致。独立只读代理另行复核同样通过。

三条旧告警保留于 correction_evidence.prior_round_warnings；当前issues=0。

题级统计沿用哈希不变的A01–A21顶层原记录，不加入shared/A22+、不双加round明细。原snapshot_state、gallery/index/helper和suite_pointer_fingerprints已明确标为v001历史观察；本次不重读或误称当前总指针保持静止，不宣称全套完成。

原JSON SHA256 999d47379f91cb4f57504563720347465c45a740e628c5be6f38d70e82ce167c；原Markdown SHA256 eba3df236eeffdbbcd494f5aa02a5ec95913b4a0602367fc51dbd68c471896b2。完整648 SHA、188指定文件、51链、字段修正、真实边界与原误报详见 progress-audit-through-A21-v002.json。

all_writes_finished=true。
