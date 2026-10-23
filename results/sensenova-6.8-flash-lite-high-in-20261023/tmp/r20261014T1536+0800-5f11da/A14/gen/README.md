# A14 生成与核验记录（临时目录）

本目录保存 A14 的前置校验日志、渲染行记录、审计数据与逐张查看记录。脚本在
`tmp/<run_id>/_suite/gen/`，运行示例：

```
python -I tmp/<run_id>/_suite/gen/a14_pages.py checks   # 前置校验，不发请求
python -I tmp/<run_id>/_suite/gen/a14_pages.py probe    # 布局探针
python -I tmp/<run_id>/_suite/gen/a14_pages.py finals   # 渲染 8 张最终卡
python -I tmp/<run_id>/_suite/gen/a14_audit.py          # 像素审计
python -I tmp/<run_id>/_suite/gen/a14_finalize.py       # 指标 + 使用报告 + 状态
```

- `checks.log` —— `a14_pages.py checks` 的输出（排版/硬约束校验 + 特殊字符核验）。
- `probe.layout.json` —— 探针 DSL 的排版元数据。
- `render-rows.json` —— 最近一次 `finals` 的 8 行请求记录（request_id、字节数、
  DSL 与响应归档路径）。被替换的那几版请求仍在 `../responses/` 里，没有清理。
- `batch-audit.json` —— 像素级审计报告副本（正式交付件在输出目录）。
- `reviews.json` —— 8 张最终服务原图的逐张实际查看记录（查看时间、观察、修改、
  结论）。审计器会把它嵌进 `batch-audit.json` 的 `reviews`。
- `../iterations.jsonl` —— 版本链：看旧图 → 改 → 再渲染 → 看新图比较，
  共 5 个版本、其中 3 次是完整视觉迭代。
- `../requests.jsonl` —— 全部请求（含 3 次 180s 读超时与重试），未覆盖。
- `../preview/a14-probe.png` —— 布局探针（转义、状态符号、折行、右列对齐）。
- `../preview/a14-escape-raw.png` —— 裸 `< > &` 直接写入 text 属性的对照渲染，
  是「服务不解码 XML 实体」这个结论的直接证据。
- `../preview/a14-align-probe.png` —— alignment 语义与盒宽余量探针（盒边界画成
  可见线 + x=88/x=1112 参照线），确定「盒窄于墨宽会折行并裁掉第二行」这个机制。
- `../preview/a14-contact-sheet.png` —— 接触表，仅作全批一致性辅助，不替代逐张查看。
