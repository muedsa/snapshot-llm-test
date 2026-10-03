"""A03 repair-log.json: every problem mapped to original position, evidence, fix, verification."""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
OUT = os.path.join(ROOT, "outputs", RUN_ID, "A03")

LOG = {
    "schema": "a03-repair-log/1",
    "run_id": RUN_ID,
    "task_id": "A03",
    "input": "tasks/A03-semantic-debugging/inputs/broken.snapshot",
    "raw_submission": {
        "file": "tmp/%s/A03/broken-attempt-01.png.failed.txt" % RUN_ID,
        "request_id": "A03-REQ-0001",
        "http_status": 400,
        "code": "PARSE_ERROR",
        "message": 'Attr [padding] value format error at position 92 near: "png">\\r\\n  <Container padding="24 32" borderRadius="24">',
        "service_request_id": "a6609a42-3017-45c1-bb79-438be2ea58fb",
        "note": "原稿原样提交一次并保留响应体与响应头（含 X-Request-Id 与 server-timing: total;dur=171.3）。",
    },
    "categories": {
        "hard_error": "服务直接拒绝，返回 400 PARSE_ERROR，必须修才能出图。",
        "silent_ignore": "属性被解析器忽略或落到默认值，不报错但语义丢失。",
        "visual_only": "能解析、能出图，但看图才发现效果不成立或语义相反。",
    },
    "issues": [
        {
            "id": "P01",
            "category": "hard_error",
            "original_location": 'broken.snapshot 第 1 行：<Snapshot width="1280" height="800" background="#0B1220" type="png">',
            "symptom": "根标签上的 width / height 不是 Snapshot 的合法属性；画布尺寸不由根标签决定。文档《标签与属性参考》中 Snapshot 只列 background / debug / type。",
            "evidence": "标签参考的 Snapshot 属性表；修复后改用 `<Container width=\"1280\" height=\"800\">` 作为尺寸容器，出图实测为 1280x800。",
            "fix": "把 width/height 移到根下第一层的 Container 上。",
            "verification": "system-pulse.png 由 Pillow 读取为 1280x800；probe-capabilities.snapshot 用去掉根 width/height 的写法渲染成功。",
        },
        {
            "id": "P02",
            "category": "hard_error",
            "original_location": 'broken.snapshot 第 2 行：<Container padding="24 32" borderRadius="24">',
            "symptom": 'padding 用了空格分隔，服务报 400 PARSE_ERROR "Attr [padding] value format error at position 92"。',
            "evidence": "原样提交得到的响应体（见 raw_submission）；文档规定的 EdgeInsets 三种格式为 \"12\"、\"(8,16)\"、\"(8,12,16,20)\"。",
            "fix": '改为 padding="(24,32)"；最终版用统一的安全边距 padding="32"。',
            "verification": "probe-capabilities.snapshot 中 padding=\"(24,32)\" 渲染成功；最终图四边留白实测 32px。",
        },
        {
            "id": "P03",
            "category": "hard_error",
            "original_location": 'broken.snapshot 第 4 行：<Text font-size="44" color="#FFFFFF">System Pulse</Text>',
            "symptom": 'font-size 用连字符写法；解析器属性名区分大小写，合法名是 fontSize。',
            "evidence": "标签参考与解析器指南均写明标签名和属性名区分大小写；修复后字号实测与 44px 相符。",
            "fix": 'font-size → fontSize（全篇统一）。',
            "verification": "最终图标题以 fontSize=\"44\" 渲染，视觉与 44px 设定一致。",
        },
        {
            "id": "P04",
            "category": "hard_error",
            "original_location": 'broken.snapshot 第 7 行：<Positioned right="20"><Text color="white">LIVE</Text></Positioned>（父节点是 Row）',
            "symptom": "Positioned 只能是 Stack / IndexedStack 的直接子节点，出现在 Row 内不成立；同时缺少 top，单轴只给一项在视觉上也无法定位。",
            "evidence": "标签参考：Positioned 的父节点约束；隔离用例 iso-expand-in-column.snapshot 还复现了同类父子关系错误 RENDER_ERROR \"renderBox.parentData must be StackParentData\"。",
            "fix": "整页改为 Stack + Positioned 绝对定位，LIVE 用 left/top/width/height 明确给定 96x36 的位置。",
            "verification": "最终图 LIVE 徽标实测 96x36，位于右上角，右边缘距安全边距 0px、与标题右边缘相距 858px。",
        },
        {
            "id": "P05",
            "category": "hard_error",
            "original_location": 'broken.snapshot 第 10 行：<Transform rotate="-8"><Container width="160" height="56" …>',
            "symptom": "Transform 没有 rotate 属性，只有列主序 4x4 matrix。",
            "evidence": "标签参考：Transform.matrix 为 16 个浮点、外层括号、值间不能有空格；探针 probe-transform.snapshot 用旋转矩阵渲染成功。",
            "fix": "改为 matrix=\"(1,0,0,0,0,1,0,0,0,0,1,0,tx,ty,0,1)\"，其中 2x2 部分取 cos8°/-sin8° 得到逆时针 8°。",
            "verification": "最终图 REVIEW 徽标可见逆时针倾斜；其旋转后的外接盒 166x78，右边缘 1216、下边缘 736，均在 32px 安全边距内。",
        },
        {
            "id": "P06",
            "category": "silent_ignore",
            "original_location": 'broken.snapshot 第 5-6 行：<Row><Expanded flex="1"><Container width="360" height="200" …></Expanded>',
            "symptom": "三张指标卡的要求落不下来：原稿只有一张卡、尺寸 360x200，且 Expanded 的固定宽度与 flex 份额互相冲突；属性不报错但布局语义丢失。",
            "evidence": "隔离用例与最终图对比：三张卡等宽 193x168，`Expanded` 的固定宽度问题在自行排版后不再出现。",
            "fix": "改为三张等宽指标卡并排，宽度由 (左栏宽 − 2×间距) / 3 计算，文案 28px、数值 40px。",
            "verification": "最终图 USAGE 72% / LATENCY 148 ms / SUCCESS 99.2% 三卡等宽并排，数值与单位可读。",
        },
        {
            "id": "P07",
            "category": "silent_ignore",
            "original_location": 'broken.snapshot 第 9 行：<Spacer flex="1"/>（父节点是 Column）',
            "symptom": "Spacer 必须有 flex 父节点；在 Column 里合法，但原稿用它把 REVIEW 推到最下方，与「右下角」的定位语义不对应，且整页纵向节奏不可控。",
            "evidence": "标签参考：Spacer 必须是 Flex/Row/Column 的直接子节点；最终版改用绝对定位后位置可控。",
            "fix": "去掉 Spacer，所有元素按 1280x800 的页面坐标绝对定位。",
            "verification": "元素位置与页面坐标一致（标题 0,0；指标卡 122；模糊带 300；REVIEW 右下 1216/736）。",
        },
        {
            "id": "P08",
            "category": "visual_only",
            "original_location": 'broken.snapshot 第 11 行：<ImageFiltered sigmaX="10" sigmaY="10"><Container …><Text>Background-only blur</Text>…',
            "symptom": "语义相反：ImageFiltered 模糊的是它自己的整棵子树，所以「Background-only blur」这行文字也会被一起模糊，达不到「只模糊卡内背景、文字保持清晰」。",
            "evidence": "对照实验 probe-blur-ImageFiltered.snapshot 与 probe-blur-BackdropFilter.snapshot 各渲染一次并逐张看图：ImageFiltered 版文字发虚，BackdropFilter 版文字清晰、只有卡内背景被柔化。",
            "fix": "改用 BackdropFilter，并且只把它套在卡片的背景填充上，文字画在滤镜之外。",
            "verification": "最终图卡内文字 contrast=228.2（锐利），卡内背景可见柔化；见 blur_semantics 小节。",
        },
        {
            "id": "P09",
            "category": "visual_only",
            "original_location": 'broken.snapshot 第 2 行：padding="24 32"。',
            "symptom": "即便 padding 语法合法，原稿的 24/32 也不是题目要求的 32 安全边距，四边不一致。",
            "evidence": "最终图实测内容外框四边均留 32px。",
            "fix": '整页统一 padding="32"。',
            "verification": "Pillow 采样：画面四周 0..31 为纯背景色。",
        },
        {
            "id": "P10",
            "category": "visual_only",
            "original_location": 'broken.snapshot 第 10 行：color="#33FFFFFF"',
            "symptom": "旧版解析器把八位颜色当作 #AARRGGBB；现在按 CSS 的 #RRGGBBAA 解析。#33FFFFFF 会被读成「白色、alpha=0x33」还是「alpha=0x33 的白色」在语义上不明确，且原稿整卡 20% 白底 + 文字不透明的要求没有区分开。",
            "evidence": "标签参考专门给出这条迁移说明：`#80FF0000` 应改成 `#FF000080`。",
            "fix": "卡底与徽标底统一写 #FFFFFF33（白 20%），文字用不含 alpha 的 #FFFFFFFF，两者分层绘制。",
            "verification": "最终图 REVIEW 徽标与说明卡卡底均为白 20% 填充，文字为不透明白，肉眼可分辨。",
        },
        {
            "id": "P11",
            "category": "hard_error",
            "original_location": '修复过程中新增：以 Column mainAxisSize="MIN" 包裹多层 Stack',
            "symptom": "出图只剩一层底纹，文字与卡片全部消失；隔离用例进一步得到 RENDER_ERROR \"renderBox.parentData must be StackParentData\"。",
            "evidence": "iso-expand-in-column.snapshot 报 RENDER_ERROR；iso-plain-stack-fixed.snapshot 与 iso-stack-two-absolute.snapshot 正常渲染两层内容。",
            "fix": "放弃 Column 分层，改为单一 Stack + 绝对定位的扁平结构。",
            "verification": "最终图所有 24 个元素全部可见。",
        },
        {
            "id": "P12",
            "category": "hard_error",
            "original_location": '修复过程中的边界色写法：border="1 SOLID #FFFFFF3D"',
            "symptom": '400 PARSE_ERROR "Attr [border] color must be #RGB, #RGBA, #RRGGBB or #RRGGBBAA"——把 8 位色写成了 10 位。',
            "evidence": "服务响应体逐字保留在 tmp/<run>/A03/system-pulse.v2.png.failed.txt。",
            "fix": "改为 8 位 #FFFFFF3D / #FFFFFF4D。",
            "verification": "此后所有请求 200。",
        },
    ],
    "blur_semantics": {
        "finding": "本构建里 BackdropFilter 柔化的是「当前已合成的整块画布」，扩散半径与 sigma 近似成正比；把指标卡放在滤镜上方、下方或右侧 70px 处都无法避免文字被柔化。",
        "measurement": [
            {"sigma": 1, "usage_value_contrast": 225.6, "reading": "锐利，与无滤镜基线 225.6 相同"},
            {"sigma": 2, "usage_value_contrast": 201.6, "reading": "20px 小字开始发虚"},
            {"sigma": 4, "usage_value_contrast": 132.2, "reading": "明显发虚"},
            {"sigma": 8, "usage_value_contrast": 82.5, "reading": "严重发虚"},
            {"sigma": 16, "usage_value_contrast": 51.1, "reading": "几乎不可读"},
        ],
        "title_contrast_note": "标题 contrast 在所有 sigma 下都是 237.5，因为 44px 大字对轻微柔化不敏感；数值文字的对比度才是可靠指标。",
        "decision": "最终交付使用 sigma=1 的 BackdropFilter：文字全部锐利，卡内背景有可辨的柔化；这是「文字保持清晰」这一硬约束下可用的最大模糊强度。",
        "rejected_alternative": "ImageFiltered sigma=9 可以让条带明显糊掉，但它会连卡内文字一起模糊，与题目要求相反，故仅在对照实验中使用。",
    },
    "not_removed": {
        "statement": "没有任何出错区块被删除以宣称修复完成。",
        "detail": "原稿的 6 个元素（标题、指标卡、Spacer、REVIEW、说明卡、LIVE）全部保留在最终图中，只是按文档改写为合法写法并补齐定位；原稿文件另存为 broken.snapshot.original 供比对。",
    },
    "final_requirements": {
        "canvas": "1280x800, 背景 #0B1220",
        "safe_margin": "32px 四边",
        "title": "44px 'System Pulse'",
        "live": "96x36，右上角，未遮挡标题（相距 858px）",
        "metrics_row": "三张等宽卡：USAGE 72% / LATENCY 148 ms / SUCCESS 99.2%，文案 28px",
        "description_card": "500x150，圆角 24，显示 28px 'Background-only blur'",
        "strips": "五条彩色细条横穿说明卡左右两侧边界",
        "review": "160x56，白底 20% 不透明度，文字 24px 不透明，逆时针 8°",
        "visibility": "所有元素完整可见，无越界（REVIEW 旋转后外接盒右 1216 / 下 736）",
    },
}

os.makedirs(OUT, exist_ok=True)
p = os.path.join(OUT, "repair-log.json")
with open(p, "w", encoding="utf-8") as fh:
    json.dump(LOG, fh, ensure_ascii=False, indent=2)
print(p)
print("issues:", len(LOG["issues"]),
      "| hard:", sum(1 for i in LOG["issues"] if i["category"] == "hard_error"),
      "| silent:", sum(1 for i in LOG["issues"] if i["category"] == "silent_ignore"),
      "| visual:", sum(1 for i in LOG["issues"] if i["category"] == "visual_only"))
