# opencode Token 消耗报告：主/子代理会话

- 生成时间：2026-10-07 18:12:24
- 生成脚本：`build-token-report.py`（位于 `exports/build-token-report.py`）
- token 数据：ccusage（复用缓存 ccusage-opencode-session.json）
- 会话元数据：opencode 本地库 `~/.local/share/opencode/opencode.db`（可用环境变量 `OPENCODE_DB` 覆盖）
- 主会话：`ses_ef98bd6aeffe3JjdCvjLdue0qL` — 执行A01–A24与B01–B06全量任务
- 主会话工作目录：`.`
- 主会话时间：2026-10-04 18:27 → 2026-10-07 16:55（70h28m）
- 子代理会话数：38（38 个有 ccusage token 记录，0 个无记录）
- 报告输出：`exports/opencode-token-usage.md`

## 1. 汇总

| 范围 | 会话数 | 输入 | 输出 | 推理 | 缓存读取 | 总 tokens | 记录成本 (USD) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 主会话（父） | 1 | 8,492,247 | 228,122 | 108,730 | 74,943,724 | 83,772,823 | 0.0000 |
| 子代理合计 | 38 | 13,629,829 | 3,092,980 | 1,794,126 | 959,746,506 | 978,263,441 | 0.0000 |
| **本会话树合计** | 39 | **22,122,076** | **3,321,102** | **1,902,856** | **1,034,690,230** | **1,062,036,264** | **0.0000** |

> 推理 tokens 取自 opencode 库 `session.tokens_reasoning`；其余列取自 ccusage。ccusage 的 totalTokens 不含推理部分，两者口径不同，勿直接相减。
> 会话树内缓存读取占总量 97.4%。

> 成本说明：`space-bunny-free` 在 LiteLLM 定价表中缺失（ccusage 标记 `missingPricing`），因此本会话树所有成本列为 0，不代表实际免费。

## 2. 主会话明细

| 字段 | 值 |
|---|---|
| Session ID | `ses_ef98bd6aeffe3JjdCvjLdue0qL` |
| 标题 | 执行A01–A24与B01–B06全量任务 |
| Agent / Model | build / space-bunny-free |
| 创建 / 最后更新 | 2026-10-04 18:27 / 2026-10-07 16:55 |
| 输入 / 输出 tokens | 8,492,247 / 228,122 |
| 缓存读取 tokens | 74,943,724 |
| 总 tokens | 83,772,823 |
| 使用模型 | space-bunny-free |

## 3. 子代理明细（按创建时间）

| # | 任务 | Session ID | 开始 | 时长 | 输入 | 输出 | 缓存读取 | 总 tokens | 成本 |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|
| 1 | Execute A06 dependency graph task | `ef92f99c7ffeqFakS0EHS1jpqO` | 2026-10-04 20:08 | 37m | 175,142 | 39,429 | 9,791,761 | 10,068,771 | 0.0000 |
| 2 | Execute A07 transit topology task | `ef92f991cffemVWbbSKxD7PVJ2` | 2026-10-04 20:08 | 10m | 50,897 | 1,119 | 229,503 | 313,851 | 0.0000 |
| 3 | Execute A08 wayfinding task | `ef92f9905ffe62CRXtdwPMBLov` | 2026-10-04 20:08 | 56m | 265,210 | 67,038 | 26,179,156 | 26,604,474 | 0.0000 |
| 4 | Execute A07 transit topology | `ef8f9c893ffeaOVxrRYzIOau9W` | 2026-10-04 21:06 | 12m | 53,045 | 1,215 | 146,736 | 233,104 | 0.0000 |
| 5 | Execute A09 transform atlas | `ef8f9c886ffeBOjTDgqvmuWrGN` | 2026-10-04 21:06 | 57m | 221,803 | 52,104 | 17,383,032 | 17,746,389 | 0.0000 |
| 6 | Execute A10 compositing lab | `ef8f9c87effeoYVjHshzep5220` | 2026-10-04 21:06 | 57m | 199,464 | 53,506 | 16,919,983 | 17,229,789 | 0.0000 |
| 7 | Execute A11 bilingual invoice | `ef8f9c875ffeEbu4SwuRBPPVb0` | 2026-10-04 21:06 | 1h06m | 239,725 | 82,809 | 22,622,889 | 22,997,821 | 0.0000 |
| 8 | Build A07 metro map deliverables | `ef8bb38caffeRZTJ6M5UmHRqUX` | 2026-10-04 22:15 | 1h42m | 99,667 | 60,789 | 19,899,136 | 20,155,287 | 0.0000 |
| 9 | Build A12 responsive system | `ef8bb38beffenhsv52YG6VrBAR` | 2026-10-04 22:15 | 1h58m | 369,419 | 85,377 | 28,226,660 | 28,773,192 | 0.0000 |
| 10 | Build A13 brand delivery | `ef8bb37c7ffehrNqXhmGwUcrpT` | 2026-10-04 22:15 | 1h04m | 229,353 | 69,865 | 22,032,876 | 22,391,783 | 0.0000 |
| 11 | Build A14 content stress batch | `ef8bb37bdffefUN6EtdcBwO2CB` | 2026-10-04 22:15 | 1h09m | 227,687 | 63,272 | 21,712,435 | 22,060,840 | 0.0000 |
| 12 | Build A15 reconstruction | `ef84d3fb8ffe39iaM9a4GvUD6v` | 2026-10-05 00:15 | 1h31m | 378,373 | 204,121 | 50,232,064 | 50,814,558 | 0.0000 |
| 13 | Build A16 data forensics | `ef84d3f95ffeoe9TbpJENFKdJ5` | 2026-10-05 00:15 | 54m | 297,555 | 51,201 | 11,773,423 | 12,165,040 | 0.0000 |
| 14 | Build A17 DSL handbook | `ef84d3f83ffeX1b5EPeQsurX9J` | 2026-10-05 00:15 | 1h35m | 531,459 | 98,110 | 32,627,345 | 33,306,778 | 0.0000 |
| 15 | Build A18 three-act story | `ef84d3f78ffe96PqaV8EmXAZE6` | 2026-10-05 00:15 | 1h20m | 412,811 | 57,596 | 21,545,915 | 22,094,717 | 0.0000 |
| 16 | Build A19 visual puzzle | `ef7f4c29dffelPcfO3ZxgDT42w` | 2026-10-05 01:51 | 1h27m | 509,043 | 93,098 | 24,662,760 | 25,346,537 | 0.0000 |
| 17 | Build A20 dense annotation | `ef7f4c291ffesgabv1RaZN8MRz` | 2026-10-05 01:51 | 7m | 43,796 | 35,787 | 652,160 | 731,743 | 0.0000 |
| 18 | Build A23 animation storyboard | `ef7f4c288ffeUlF6KitrGhLAa1` | 2026-10-05 01:51 | 43m | 200,494 | 97,337 | 19,650,688 | 19,948,519 | 0.0000 |
| 19 | Build A24 release plan | `ef7f4c15effeQTQ8A0kQrtzmy9` | 2026-10-05 01:51 | 1h14m | 339,879 | 194,114 | 41,634,944 | 42,168,937 | 0.0000 |
| 20 | Build A20 dense annotation map | `ef7a1b266ffepul2EU75yTUNrz` | 2026-10-05 03:22 | 9m | 40,619 | 1,864 | 225,718 | 300,507 | 0.0000 |
| 21 | Build A21 three-round launch | `ef7a1b25affey4jcKXLhpWtX5M` | 2026-10-05 03:22 | 1h30m | 277,602 | 106,896 | 35,471,718 | 35,921,768 | 0.0000 |
| 22 | Build A22 three-round correction | `ef7a1b251ffehDeQWOFXvaI7R6` | 2026-10-05 03:22 | 1h38m | 353,568 | 101,443 | 38,903,680 | 39,418,790 | 0.0000 |
| 23 | Build B01 ten showcases | `ef73ce0b8ffeWiCF7ct8yIwLhs` | 2026-10-05 05:12 | 47m | 206,388 | 56,728 | 15,653,846 | 15,957,912 | 0.0000 |
| 24 | Build B02 ten touchpoints | `ef73ce042ffef1HJTLOVqS6yiQ` | 2026-10-05 05:12 | 47m | 251,632 | 145,652 | 17,657,984 | 18,055,268 | 0.0000 |
| 25 | Build B03 creative frontier | `ef73ce01effe4tpj34IXO7S5Js` | 2026-10-05 05:12 | 46m | 171,444 | 56,842 | 15,227,241 | 15,473,402 | 0.0000 |
| 26 | Finish B01 ten showcases | `ef64bc49dffes17fDqvtZUdCfv` | 2026-10-05 09:36 | 2h28m | 334,867 | 105,588 | 62,254,934 | 62,756,580 | 0.0000 |
| 27 | Finish B02 ten touchpoints | `ef64ba898ffeVtBhbgjBv0bd1T` | 2026-10-05 09:36 | 58m | 203,468 | 73,570 | 18,978,204 | 19,281,316 | 0.0000 |
| 28 | Finish B03 creative frontier | `ef64ba0c3ffeEwAs0EEV95rilr` | 2026-10-05 09:36 | 2h28m | 473,592 | 176,955 | 74,884,027 | 75,627,315 | 0.0000 |
| 29 | Finish B01 remaining cases | `ef5bbd66effer5SR020HBtRpuk` | 2026-10-05 12:13 | 1h28m | 265,737 | 77,843 | 29,897,814 | 30,255,363 | 0.0000 |
| 30 | Finish B03 remaining cases | `ef5bbbfa5ffeQS1lJRSxIWBKt0` | 2026-10-05 12:13 | 1h58m | 590,207 | 117,749 | 41,177,978 | 41,926,278 | 0.0000 |
| 31 | Finish B03 reports and logs | `ef54c58d6ffeYBFwD1mIIsg5sA` | 2026-10-05 14:15 | 1h46m | 2,352,136 | 71,019 | 26,764,941 | 29,245,740 | 0.0000 |
| 32 | Build B04 researched special | `ef54c1f07ffeSqdt5IWbnh1KPH` | 2026-10-05 14:15 | 2h11m | 355,807 | 156,944 | 49,886,145 | 50,446,938 | 0.0000 |
| 33 | Build B05 product from zero | `ef4d1ec88ffeXSOckGL7KlBZjL` | 2026-10-05 16:28 | 59m | 619,082 | 67,468 | 16,832,339 | 17,551,004 | 0.0000 |
| 34 | Build B06 everyday information | `ef4d1ac66ffeIJA4wedLfrXB2H` | 2026-10-05 16:29 | 1h00m | 236,029 | 65,309 | 16,605,835 | 16,947,745 | 0.0000 |
| 35 | Finish B05 six more cases | `ef47fa3b2ffeb7jq1xky6dYR6O` | 2026-10-05 17:58 | 1h20m | 119,237 | 21,703 | 4,852,920 | 5,015,794 | 0.0000 |
| 36 | Finish B05 cases 7-10 | `ef4312372ffemZswuR4fPiiP4c` | 2026-10-05 19:24 | 2h59m | 886,030 | 121,541 | 53,565,641 | 54,635,092 | 0.0000 |
| 37 | Finish B06 seven more cases | `ef3562d9effetJwH1Z9LJjT4au` | 2026-10-05 23:23 | 1h00m | 740,026 | 72,378 | 16,325,621 | 17,160,789 | 0.0000 |
| 38 | Complete B06 cases 8-10 and wrap | `eeef70988ffezasPtY49WPzu0V` | 2026-10-06 19:46 | 1h29m | 307,536 | 87,601 | 36,656,454 | 37,133,710 | 0.0000 |

> Session ID 为简写（省略 `ses_` 前缀），完整列表见附录 A。

### 3.1 子代理 token 排行

| 排名 | 任务 | Session ID | 总 tokens | 占比 |
|---:|---|---|---:|---:|
| 1 | Finish B03 creative frontier | `ef64ba0c3ffeEwAs0EEV95rilr` | 75,627,315 | 7.7% |
| 2 | Finish B01 ten showcases | `ef64bc49dffes17fDqvtZUdCfv` | 62,756,580 | 6.4% |
| 3 | Finish B05 cases 7-10 | `ef4312372ffemZswuR4fPiiP4c` | 54,635,092 | 5.6% |
| 4 | Build A15 reconstruction | `ef84d3fb8ffe39iaM9a4GvUD6v` | 50,814,558 | 5.2% |
| 5 | Build B04 researched special | `ef54c1f07ffeSqdt5IWbnh1KPH` | 50,446,938 | 5.2% |
| 6 | Build A24 release plan | `ef7f4c15effeQTQ8A0kQrtzmy9` | 42,168,937 | 4.3% |
| 7 | Finish B03 remaining cases | `ef5bbbfa5ffeQS1lJRSxIWBKt0` | 41,926,278 | 4.3% |
| 8 | Build A22 three-round correction | `ef7a1b251ffehDeQWOFXvaI7R6` | 39,418,790 | 4.0% |
| 9 | Complete B06 cases 8-10 and wrap | `eeef70988ffezasPtY49WPzu0V` | 37,133,710 | 3.8% |
| 10 | Build A21 three-round launch | `ef7a1b25affey4jcKXLhpWtX5M` | 35,921,768 | 3.7% |
| 11 | Build A17 DSL handbook | `ef84d3f83ffeX1b5EPeQsurX9J` | 33,306,778 | 3.4% |
| 12 | Finish B01 remaining cases | `ef5bbd66effer5SR020HBtRpuk` | 30,255,363 | 3.1% |
| 13 | Finish B03 reports and logs | `ef54c58d6ffeYBFwD1mIIsg5sA` | 29,245,740 | 3.0% |
| 14 | Build A12 responsive system | `ef8bb38beffenhsv52YG6VrBAR` | 28,773,192 | 2.9% |
| 15 | Execute A08 wayfinding task | `ef92f9905ffe62CRXtdwPMBLov` | 26,604,474 | 2.7% |
| 16 | Build A19 visual puzzle | `ef7f4c29dffelPcfO3ZxgDT42w` | 25,346,537 | 2.6% |
| 17 | Execute A11 bilingual invoice | `ef8f9c875ffeEbu4SwuRBPPVb0` | 22,997,821 | 2.4% |
| 18 | Build A13 brand delivery | `ef8bb37c7ffehrNqXhmGwUcrpT` | 22,391,783 | 2.3% |
| 19 | Build A18 three-act story | `ef84d3f78ffe96PqaV8EmXAZE6` | 22,094,717 | 2.3% |
| 20 | Build A14 content stress batch | `ef8bb37bdffefUN6EtdcBwO2CB` | 22,060,840 | 2.3% |
| 21 | Build A07 metro map deliverables | `ef8bb38caffeRZTJ6M5UmHRqUX` | 20,155,287 | 2.1% |
| 22 | Build A23 animation storyboard | `ef7f4c288ffeUlF6KitrGhLAa1` | 19,948,519 | 2.0% |
| 23 | Finish B02 ten touchpoints | `ef64ba898ffeVtBhbgjBv0bd1T` | 19,281,316 | 2.0% |
| 24 | Build B02 ten touchpoints | `ef73ce042ffef1HJTLOVqS6yiQ` | 18,055,268 | 1.8% |
| 25 | Execute A09 transform atlas | `ef8f9c886ffeBOjTDgqvmuWrGN` | 17,746,389 | 1.8% |
| 26 | Build B05 product from zero | `ef4d1ec88ffeXSOckGL7KlBZjL` | 17,551,004 | 1.8% |
| 27 | Execute A10 compositing lab | `ef8f9c87effeoYVjHshzep5220` | 17,229,789 | 1.8% |
| 28 | Finish B06 seven more cases | `ef3562d9effetJwH1Z9LJjT4au` | 17,160,789 | 1.8% |
| 29 | Build B06 everyday information | `ef4d1ac66ffeIJA4wedLfrXB2H` | 16,947,745 | 1.7% |
| 30 | Build B01 ten showcases | `ef73ce0b8ffeWiCF7ct8yIwLhs` | 15,957,912 | 1.6% |
| 31 | Build B03 creative frontier | `ef73ce01effe4tpj34IXO7S5Js` | 15,473,402 | 1.6% |
| 32 | Build A16 data forensics | `ef84d3f95ffeoe9TbpJENFKdJ5` | 12,165,040 | 1.2% |
| 33 | Execute A06 dependency graph task | `ef92f99c7ffeqFakS0EHS1jpqO` | 10,068,771 | 1.0% |
| 34 | Finish B05 six more cases | `ef47fa3b2ffeb7jq1xky6dYR6O` | 5,015,794 | 0.5% |
| 35 | Build A20 dense annotation | `ef7f4c291ffesgabv1RaZN8MRz` | 731,743 | 0.1% |
| 36 | Execute A07 transit topology task | `ef92f991cffemVWbbSKxD7PVJ2` | 313,851 | 0.0% |
| 37 | Build A20 dense annotation map | `ef7a1b266ffepul2EU75yTUNrz` | 300,507 | 0.0% |
| 38 | Execute A07 transit topology | `ef8f9c893ffeaOVxrRYzIOau9W` | 233,104 | 0.0% |

### 3.2 按任务分组

| 类别 | 会话数 | 输入 | 输出 | 缓存读取 | 总 tokens | 占比 |
|---|---:|---:|---:|---:|---:|---:|
| A 类 | 22 | 5,516,611 | 1,618,090 | 462,524,582 | 470,793,195 | 48.1% |
| B 类 | 16 | 8,113,218 | 1,474,890 | 497,221,924 | 507,470,246 | 51.9% |
| 其他/未知 | 0 | 0 | 0 | 0 | 0 | 0.0% |

### 3.3 模型构成

| 模型 | 会话数 | 输入 | 输出 | 缓存读取 | 总 tokens | 定价 |
|---|---:|---:|---:|---:|---:|---|
| `space-bunny-free` | 39 | 22,122,076 | 3,321,102 | 1,034,690,230 | 1,060,133,408 | 缺失（成本按 0 计） |

## 4. 观察

- 子代理最高消耗：`Finish B03 creative frontier`（`ef64ba0c3ffeEwAs0EEV95rilr`），75,627,315 tokens，占子代理总量 7.7%。
- 子代理最低消耗：`Execute A07 transit topology`（`ef8f9c893ffeaOVxrRYzIOau9W`），233,104 tokens。
- 子代理平均每会话总 tokens 25,743,774，主会话为 83,772,823，主会话高于子代理均值。
- 缓存读取占子代理总量 98.1%，占主会话 89.5%；实际负载主要看输入+输出，缓存读取多为重复上下文复用。
- 输入+输出（不含缓存）合计 25,443,178 tokens，其中子代理占 61.6% 输入、93.1% 输出——内容产出几乎全部由子代理完成，主会话主要负责调度与汇总。
- 同一任务可能对应多个子会话（首轮 + 续做），属于上下文压缩或平台中断后的续跑，统计时应按“子代理会话”而非“任务数”理解。

## 附录 A：完整子代理 Session ID

```
ses_ef92f99c7ffeqFakS0EHS1jpqO  Execute A06 dependency graph task (@general subagent)
ses_ef92f991cffemVWbbSKxD7PVJ2  Execute A07 transit topology task (@general subagent)
ses_ef92f9905ffe62CRXtdwPMBLov  Execute A08 wayfinding task (@general subagent)
ses_ef8f9c893ffeaOVxrRYzIOau9W  Execute A07 transit topology (@general subagent)
ses_ef8f9c886ffeBOjTDgqvmuWrGN  Execute A09 transform atlas (@general subagent)
ses_ef8f9c87effeoYVjHshzep5220  Execute A10 compositing lab (@general subagent)
ses_ef8f9c875ffeEbu4SwuRBPPVb0  Execute A11 bilingual invoice (@general subagent)
ses_ef8bb38caffeRZTJ6M5UmHRqUX  Build A07 metro map deliverables (@general subagent)
ses_ef8bb38beffenhsv52YG6VrBAR  Build A12 responsive system (@general subagent)
ses_ef8bb37c7ffehrNqXhmGwUcrpT  Build A13 brand delivery (@general subagent)
ses_ef8bb37bdffefUN6EtdcBwO2CB  Build A14 content stress batch (@general subagent)
ses_ef84d3fb8ffe39iaM9a4GvUD6v  Build A15 reconstruction (@general subagent)
ses_ef84d3f95ffeoe9TbpJENFKdJ5  Build A16 data forensics (@general subagent)
ses_ef84d3f83ffeX1b5EPeQsurX9J  Build A17 DSL handbook (@general subagent)
ses_ef84d3f78ffe96PqaV8EmXAZE6  Build A18 three-act story (@general subagent)
ses_ef7f4c29dffelPcfO3ZxgDT42w  Build A19 visual puzzle (@general subagent)
ses_ef7f4c291ffesgabv1RaZN8MRz  Build A20 dense annotation (@general subagent)
ses_ef7f4c288ffeUlF6KitrGhLAa1  Build A23 animation storyboard (@general subagent)
ses_ef7f4c15effeQTQ8A0kQrtzmy9  Build A24 release plan (@general subagent)
ses_ef7a1b266ffepul2EU75yTUNrz  Build A20 dense annotation map (@general subagent)
ses_ef7a1b25affey4jcKXLhpWtX5M  Build A21 three-round launch (@general subagent)
ses_ef7a1b251ffehDeQWOFXvaI7R6  Build A22 three-round correction (@general subagent)
ses_ef73ce0b8ffeWiCF7ct8yIwLhs  Build B01 ten showcases (@general subagent)
ses_ef73ce042ffef1HJTLOVqS6yiQ  Build B02 ten touchpoints (@general subagent)
ses_ef73ce01effe4tpj34IXO7S5Js  Build B03 creative frontier (@general subagent)
ses_ef64bc49dffes17fDqvtZUdCfv  Finish B01 ten showcases (@general subagent)
ses_ef64ba898ffeVtBhbgjBv0bd1T  Finish B02 ten touchpoints (@general subagent)
ses_ef64ba0c3ffeEwAs0EEV95rilr  Finish B03 creative frontier (@general subagent)
ses_ef5bbd66effer5SR020HBtRpuk  Finish B01 remaining cases (@general subagent)
ses_ef5bbbfa5ffeQS1lJRSxIWBKt0  Finish B03 remaining cases (@general subagent)
ses_ef54c58d6ffeYBFwD1mIIsg5sA  Finish B03 reports and logs (@general subagent)
ses_ef54c1f07ffeSqdt5IWbnh1KPH  Build B04 researched special (@general subagent)
ses_ef4d1ec88ffeXSOckGL7KlBZjL  Build B05 product from zero (@general subagent)
ses_ef4d1ac66ffeIJA4wedLfrXB2H  Build B06 everyday information (@general subagent)
ses_ef47fa3b2ffeb7jq1xky6dYR6O  Finish B05 six more cases (@general subagent)
ses_ef4312372ffemZswuR4fPiiP4c  Finish B05 cases 7-10 (@general subagent)
ses_ef3562d9effetJwH1Z9LJjT4au  Finish B06 seven more cases (@general subagent)
ses_eeef70988ffezasPtY49WPzu0V  Complete B06 cases 8-10 and wrap (@general subagent)
```

## 附录 B：复现方式

```bash
# 1. 拉取 token 数据（脚本默认复用上一步的 JSON 缓存）
npx -y ccusage@latest opencode session --json --no-color --offline

# 2. 生成报告（主会话缺省自动推断；首次运行会自动做第 1 步）
python build-token-report.py
```

会话元数据由脚本直接从 opencode 本地 SQLite 库读取（只读打开），
库位置按 `OPENCODE_DB` → 各平台惯例（`~/.local/share/opencode`、
`~/AppData/Local/opencode` 等）依次探测。手动查看：

```bash
sqlite3 "${OPENCODE_DB:-$HOME/.local/share/opencode/opencode.db}" \
  "select id, parent_id, title, time_created from session;"
```

可覆盖的配置：

| 变量 / 参数 | 作用 |
|---|---|
| `--parent` / `OPENCODE_SESSION_ID` | 主会话 ID，缺省自动推断 |
| `--db` / `OPENCODE_DB` | opencode.db 路径，缺省按平台惯例探测 |
| `--raw` | ccusage JSON 缓存路径（默认与脚本同目录） |
| `--out` | 报告输出路径（默认与脚本同目录） |
| `--refresh` | 强制重新调用 ccusage，不复用缓存 |

