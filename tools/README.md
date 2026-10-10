# 题库维护与发布检查

维护对象为 `task-suite/`，作者评分与客观参照在 `evaluation/`。
`results/` 是归档结果，不作为题面维护的输入。改进编号与临时审查资料保存在
已忽略的 `reviews-temp/`，不提交、不分发给被测模型。

## 同步修改

本项目采用“保持双份题面、发布前检查一致性”的方式：
修改 `TASK.md` 的要求时，同步 `task.json.prompt`，保留完整正文、空格和换行语义。
标题同时同步 `catalog.json` 与总清单；PNG/DSL路径和尺寸同时更新 Markdown 图片表、
`required_outputs` 以及目录中的图片数量。新增或删除额外交付时更新
`additional_outputs` 和 Markdown 的“额外文件”声明。

A21/A22 所有交付路径都相对本题输出根。顶层清单是完整集合，`rounds` 是归属索引，
两处声明不表示两份文件。修改后同步轮次文档、每轮清单与顶层表格；
保留任务根累计报告和各轮报告，不能二次拼接 `round-XX/`。

A 类专用 JSON 的最小字段在各题 `templates/audit-fields.json`；
`task.json.audit_templates` 把实际交付路径关联到字段说明。
B04 的来源记录使用 `templates/sources-fields.json`。
新增字段说明须同步题面链接与 `artifacts` 定义；这些是要求，不能预填答案或成功记录。
B 类完成标准与变更历史在 `AGENTS.md` 和作品集模板中维护。
变更影响验收口径时也检查对应作者评分清单，避免出现公开要求和评分互相矛盾。

## 验证

从仓库根运行：

```sh
python -B tools/validate_task_contracts.py
python -B -m unittest discover -s tools -p "test_*.py"
python -B tools/release-suite-task-pack.py --refresh-manifest
git diff --check
```

`validate_task_contracts.py` 核对30题的身份/题面、图片表、附加文件、多轮完整路径、
轮次文件引用与审计字段覆盖；它不运行作图任务，也不读取模型结果。
测试在临时题库副本注入题面漂移、图片尺寸错误、交付遗漏、轮次路径错误和模板失效，
确认这些错误会被拦截。发布脚本会调用该检查，现有CI也会运行全部作者侧测试。

`validate_a08_wayfinding.py` 额外检查A08地图/路径的语义与作者参照。
只有有意更改A08输入并复核设计后才使用 `--refresh-reference`。
`--refresh-manifest` 只刷新当前题库文件的实际字节哈希，不代表题面或视觉质量已通过。
发布检查记录在 `evaluation/task-suite/authoring-validation.json`。
涉及计算或几何的要求须做独立可行性检查；题目需要作者渲染试作时，保留真实响应与看图证据。
静态检查通过不能宣称完成整套模型作图试跑。

## 提交范围

审查正式差异、测试结果与清单哈希变化，只提交题库、作者评分及必要工具。
不提交 `reviews-temp/`、运行缓存或临时试作；不访问或改动归档的 `results/`。
