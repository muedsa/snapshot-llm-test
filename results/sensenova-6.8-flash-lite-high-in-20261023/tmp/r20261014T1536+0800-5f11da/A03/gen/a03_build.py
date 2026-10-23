"""A03 步骤 4：构造最终 "System Pulse" 监控卡 DSL 并提交真实服务。

坐标约定：本文件里所有 *_X/*_Y 都是**画布绝对坐标**（左上原点，x 向右、y 向下，像素）。
根 Container 用 padding="(32,32)" 施加安全边距，Stack 的原点因此在 (32,32)，
所以 <Positioned> 里写的是 绝对坐标 − 32（见 L()/T()）。
v1 的缺陷正是漏掉了这个 −32，导致 LIVE/第三张指标卡贴住画布右缘、
REVIEW 旋转后右下角几乎被画布裁掉 —— 见 repair-log.json 的 V-1。

布局（画布 1280×800，安全边距 32 → 内容区 x 32..1248、y 32..768）：

  y  34..87     标题 "System Pulse" fontSize 44 粗体（x 32 起）
  y  42..78     右上 LIVE 96×36，x 1152..1248 —— 与标题（x 32..~370）横向不重叠
  y 124..274    三个等宽指标卡：宽 384、间距 32 → x 32..416 / 448..832 / 864..1248
  y 360         1px 分隔线（274 与 446 的中点）
  y 446..596    中央说明卡 500×150，x 390..890（圆角 24）
  y 446..596    彩色细条 5 条，x 250..1030 —— 越过卡的左右两侧边界 140px
                ClipRRect(24) + BackdropFilter(σ=10) 只模糊卡内背景，文字在滤镜外
  y 659..737    右下 REVIEW 160×56，视觉逆时针 8°（θ=-8°，列主序 4×4 外层带括号）
                旋转后外接框 166.2×77.7，中心 (1158,698)，四角都在安全区内

用法：
  python a03_build.py                 # 预览（写 tmp/preview/v{n}.png）
  python a03_build.py --final         # 预览 + 写 outputs/（最终交付）
  VERSION=v3 python a03_build.py
"""

from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a03_io as IO  # noqa: E402

# --- 参数 ---------------------------------------------------------------
VERSION = os.environ.get("VERSION", "v2")
FAMILY = "Inter"          # /fonts 已确认存在（含 Semi Bold / Black 字重）
BG = "#0B1220"
SAFE = 32
CW, CH = 1280, 800


def L(v: float) -> float:
    """绝对 x → Positioned left（减去根 padding 的水平分量）。"""
    return int(v - SAFE)


def T(v: float) -> float:
    """绝对 y → Positioned top（减去根 padding 的竖直分量）。"""
    return int(v - SAFE)


# --- 画布绝对坐标 -------------------------------------------------------
TITLE_X, TITLE_Y = 32, 34

LIVE_W, LIVE_H = 96, 36
LIVE_X, LIVE_Y = CW - SAFE - LIVE_W, 42          # 1152..1248 × 42..78

METRIC_TOP, METRIC_H, METRIC_W, METRIC_GAP = 124, 150, 384, 32
METRICS = [
    ("USAGE 72%", "#38BDF8"),
    ("LATENCY 148 ms", "#FBBF24"),
    ("SUCCESS 99.2%", "#34D399"),
]

DIVIDER_X, DIVIDER_Y, DIVIDER_W = 32, 360, CW - 2 * SAFE   # (274+446)/2 = 360

CARD_W, CARD_H, CARD_X, CARD_Y = 500, 150, 390, 446        # 390..890 × 446..596
STRIPE_W, STRIPE_X = 780, 250                               # 250..1030，越过 390/890
STRIPE_COLORS = ["#F472B6", "#38BDF8", "#A78BFA", "#34D399", "#FBBF24"]

REV_W, REV_H = 160, 56
REV_CX, REV_CY = 1158, 698                                  # 旋转后外接框中心
REV_X, REV_Y = REV_CX - REV_W // 2, REV_CY - REV_H // 2    # 1078..1238 × 670..726

# θ = -8°：屏幕坐标 y 向下，rotationZ(θ>0) 视觉为顺时针，
# 故「视觉逆时针 8°」用 θ = -8°。列主序展开、外层必须有括号、值间无空格。
_TH = math.radians(-8.0)
_C, _S = math.cos(_TH), math.sin(_TH)
ROT = "(" + ",".join(f"{x:.7f}" for x in (
    _C, _S, 0.0, 0.0,
    -_S, _C, 0.0, 0.0,
    0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 1.0,
)) + ")"


def stripes() -> str:
    bars = "\n".join(
        f'            <Container width="{STRIPE_W}" height="10" color="{c}"/>'
        for c in STRIPE_COLORS)
    return f'''      <!-- 背景彩色细条：x {STRIPE_X}..{STRIPE_X + STRIPE_W}，
           越过说明卡左右两侧边界（{CARD_X} / {CARD_X + CARD_W}） -->
      <Positioned left="{L(STRIPE_X)}" top="{T(CARD_Y)}">
        <Container width="{STRIPE_W}" height="{CARD_H}" color="transparent">
          <Column mainAxisAlignment="SPACE_AROUND">
{bars}
          </Column>
        </Container>
      </Positioned>'''


def metric_card(i: int, label: str, accent: str) -> str:
    x = SAFE + i * (METRIC_W + METRIC_GAP)
    return f'''      <Positioned left="{L(x)}" top="{T(METRIC_TOP)}">
        <Container width="{METRIC_W}" height="{METRIC_H}" borderRadius="20"
                   color="#101B2E" border="1 SOLID #233049"
                   boxShadow="0 8 20 0 #00000040 NORMAL">
          <Column mainAxisAlignment="CENTER" crossAxisAlignment="CENTER">
            <Text fontFamily="{FAMILY}" fontSize="28" color="#FFFFFF">{label}</Text>
            <Container width="72" height="22" color="transparent">
              <Container width="72" height="4" borderRadius="2" color="{accent}"/>
            </Container>
          </Column>
        </Container>
      </Positioned>'''


def build() -> str:
    cards = "\n".join(metric_card(i, t, c) for i, (t, c) in enumerate(METRICS))
    return f'''<Snapshot background="{BG}" type="png">
  <!-- 根容器给出画布尺寸（<Snapshot> 没有 width/height）+ 32px 安全边距 -->
  <Container width="{CW}" height="{CH}" color="{BG}" padding="({SAFE},{SAFE})">
    <Stack fit="EXPAND" clipBehavior="NONE">

      <!-- 标题：44 号粗体，绝对 x {TITLE_X} -->
      <Positioned left="{L(TITLE_X)}" top="{T(TITLE_Y)}">
        <Text fontFamily="{FAMILY}" fontSize="44" fontStyle="BOLD"
              color="#FFFFFF">System Pulse</Text>
      </Positioned>

      <!-- 右上 LIVE 96×36，绝对 x {LIVE_X}..{LIVE_X + LIVE_W} -->
      <Positioned left="{L(LIVE_X)}" top="{T(LIVE_Y)}">
        <Container width="{LIVE_W}" height="{LIVE_H}" borderRadius="18"
                   color="#052E16" border="1 SOLID #16A34A">
          <Stack fit="EXPAND" clipBehavior="NONE">
            <Positioned left="16" top="14">
              <Container width="8" height="8" borderRadius="4" color="#22C55E"/>
            </Positioned>
            <Positioned left="32" top="0">
              <Container width="56" height="{LIVE_H}" alignment="CENTER_LEFT">
                <Text fontFamily="{FAMILY}" fontSize="18" fontStyle="BOLD"
                      color="#4ADE80" letterSpacing="2">LIVE</Text>
              </Container>
            </Positioned>
          </Stack>
        </Container>
      </Positioned>

      <!-- 第一行：三个等宽指标卡（宽 {METRIC_W}，间距 {METRIC_GAP}） -->
{cards}

      <!-- 分隔线 -->
      <Positioned left="{L(DIVIDER_X)}" top="{T(DIVIDER_Y)}">
        <Container width="{DIVIDER_W}" height="1" color="#1B2740"/>
      </Positioned>

{stripes()}

      <!-- 只模糊卡内背景：ClipRRect 限定圆角区域 + BackdropFilter，子节点透明占位 -->
      <Positioned left="{L(CARD_X)}" top="{T(CARD_Y)}">
        <ClipRRect borderRadius="24">
          <BackdropFilter sigmaX="10" sigmaY="10" tileMode="CLAMP">
            <Container width="{CARD_W}" height="{CARD_H}" color="transparent"/>
          </BackdropFilter>
        </ClipRRect>
      </Positioned>

      <!-- 说明卡卡体：半透明填充，让模糊出来的色彩可见 -->
      <Positioned left="{L(CARD_X)}" top="{T(CARD_Y)}">
        <Container width="{CARD_W}" height="{CARD_H}" borderRadius="24"
                   color="#FFFFFF1A" border="1 SOLID #38BDF8"/>
      </Positioned>

      <!-- 文字在滤镜之外：保持清晰 -->
      <Positioned left="{L(CARD_X)}" top="{T(CARD_Y)}">
        <Container width="{CARD_W}" height="{CARD_H}" alignment="CENTER">
          <Text fontFamily="{FAMILY}" fontSize="28" color="#FFFFFF"
                letterSpacing="0.5">Background-only blur</Text>
        </Container>
      </Positioned>

      <!-- 右下 REVIEW 160×56，视觉逆时针 8°，绕自身中心 -->
      <Positioned left="{L(REV_X)}" top="{T(REV_Y)}">
        <Transform matrix="{ROT}" alignment="CENTER">
          <Container width="{REV_W}" height="{REV_H}" borderRadius="12"
                     color="#FFFFFF33" border="1 SOLID #FFFFFF66">
            <Text fontFamily="{FAMILY}" fontSize="24" fontStyle="BOLD"
                  color="#FFFFFF" letterSpacing="2">REVIEW</Text>
          </Container>
        </Transform>
      </Positioned>

    </Stack>
  </Container>
</Snapshot>'''


def main() -> None:
    dsl = build()
    final = "--final" in sys.argv
    rid = f"req-a03-{VERSION}-final" if final else f"req-a03-{VERSION}-preview"
    rec = IO.submit(
        dsl,
        label=f"A03 System Pulse {VERSION}" + (" 最终交付" if final else " 预览"),
        rid=rid,
        out_png="system-pulse.png" if final else None,
        out_dsl="system-pulse.snapshot" if final else None,
        kind="render",
        dsl_version=VERSION,
    )
    ok = rec["_ok"]
    out, tmp = IO.dirs()
    (tmp / "preview").mkdir(parents=True, exist_ok=True)
    if ok:
        (tmp / "preview" / f"{VERSION}.png").write_bytes(
            (tmp / "responses" / f"{rid}.body").read_bytes())
    (tmp / f"{VERSION}.json").write_text(json.dumps(
        {"version": VERSION, "final": final, "request_id": rec["request_id"],
         "http_status": rec["http_status"], "content_type": rec["content_type"],
         "response_bytes": rec["response_bytes"], "ok": ok,
         "output_png": S_rel(out / "system-pulse.png") if (ok and final) else None,
         "output_dsl": S_rel(out / "system-pulse.snapshot") if (ok and final) else None,
         "error": rec["_error_json"], "dsl_version_path": rec["request_path"],
         "matrix": ROT}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(VERSION, "final" if final else "preview", rec["http_status"],
          rec["content_type"], rec["response_bytes"], "OK" if ok else "FAIL")
    if not ok:
        print(rec["_error_json"])


def S_rel(p: Path) -> str:
    import suite as S
    return S.rel(p)


if __name__ == "__main__":
    main()
