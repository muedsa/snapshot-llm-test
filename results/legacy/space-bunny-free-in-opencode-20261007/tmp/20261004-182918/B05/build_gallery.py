"""生成 B05 的 gallery.html —— 纯静态 HTML，不含任何 <script>。

之前那版用 JS 在页面里拼卡片，静态检查无法验证链接，且禁用脚本就什么都看不到。
这里改成由脚本把 10 张卡直接写成静态 HTML：零脚本、零 CDN，
只靠相对链接就能本地打开并点开原图。
"""
import io
import os

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
D = os.path.join(ROOT, "outputs", "20261004-182918", "B05")

CASES = [
    ("case-01", "01", "首次拍摄引导：对齐锚点标记牌", 420, 900, "手机竖屏（20:9）",
     "林知远（租客）", "2026-09-30 09:38",
     "在被产品拒绝之前先学会「对着牌拍」，完成第一条可入库记录",
     "进行中 · 步骤 2/12 · K-01 已识别，快门可用",
     "取景框 + 锚点牌检测框是产品的记忆点：别的租房 App 只有「拍照」，"
     "这里必须让用户看见系统在看什么。"),
    ("case-02", "02", "拍摄成功回执：锚点 K-01 的即时判定", 900, 430,
     "手机横屏（半屏回执 sheet）", "林知远（租客）", "2026-09-30 09:41",
     "3 秒内确认这条记录已入库，并看到它会和哪一次比对",
     "成功 · 对照基准锁定 2023-07-01 首拍 · 差分待判定",
     "差分被明确标注为「待判定」，因为要等 12 个锚点拍完统一算——系统不假装当场就有结论。"),
    ("case-03", "03", "拒绝入档：光线不足 + 未识别标记牌", 420, 900,
     "手机竖屏（告警页）", "林知远（租客）", "2026-09-30 16:07",
     "知道为什么失败、失败会怎样影响押金结算、以及下一步做什么",
     "异常 · E-02 判定暂挂 · 重拍期限 10-07",
     "失败页把「被拒绝的证据」和「系统为什么拒绝」放在同一屏；顶部是倒计时不是道歉。"),
    ("case-04", "04", "退租差分总览：新增 / 已修复 / 未变化 / 暂挂", 1600, 1000,
     "桌面浏览器窗口（16:10）", "陆文君（房东）", "2026-09-30 18:04",
     "逐锚点看 Δ，把「谁的责任」定下来，并生成可打印的交接报告",
     "差分已生成 · 责任 ¥200 · E-02 暂挂 ¥0",
     "四类状态用四种颜色 + 左侧色条在同一张表里对齐；「暂挂」占一整行而不是被悄悄丢掉。"),
    ("case-05", "05", "退租交接报告（双方签字页）", 1240, 1754,
     "打印 A4 纵向（150dpi）", "陆文君 + 林知远 + 周敏", "2026-10-01",
     "把桌面上的差分结论压缩成一页可签字、可存档的凭证",
     "结束态 · ¥200 待三方确认 · E-02 仍暂挂",
     "整页只有一种强调色（锚点牌黄）+ 一个责任数字；签字区占整页约 1/6，因为这份纸的任务是被签字。"),
    ("case-06", "06", "退租倒计时与未完成项", 396, 484,
     "智能手表显示屏（深色 OLED）", "林知远（正在搬箱子）", "2026-10-05 20:12",
     "抬腕 3 秒知道还差什么、期限还剩几天、责任是否变化",
     "待办提醒 · 10/12 进入差分 · 还有 2 天",
     "整块表盘只允许一个数字（10/12 进度环）和一个黄色物体（E-02 标记牌）。"),
    ("case-07", "07", "报修流转：业主 / 租客 / 维修方时间轴", 420, 900,
     "手机竖屏（工单详情）", "陆文君（房东，定责前回看）", "2025-06-18 → 06-25",
     "看清一次维修从报修到闭环留下了哪些可核对的记录",
     "已闭环 · R-2506-042 · 费用 ¥260",
     "第 4 个节点「B-02 复拍入库」正是 case-04 里 B-02 判「已修复」的依据——两图可互相印证。"),
    ("case-08", "08", "分享给下一任租客的「这套房的故事」", 900, 1900,
     "手机长图（点开即全屏）", "陆文君导出 → 下一任租客", "2026-10-01",
     "30 秒看完 39 个月里发生了什么，并知道哪些事已经替我做完了",
     "含 2 处新增损伤的坦白说明 + E-02 暂挂",
     "正文改用衬线体读起来像一份交接说明，与前面所有无衬线的操作界面明确区分。"),
    ("case-09", "09", "冰箱上的维修速查卡", 1050, 760,
     "打印 A5 横向卡片（贴冰箱门）", "任何一个住在这套房里的人", "2026-10-01 打印",
     "3 秒找到该找谁，30 秒知道上次换了什么件",
     "三个联系方式 · 三个修过的位置 · E-02 未确认",
     "卡片逻辑：巨大可读字号、极少颜色、一张表对齐；左上角的黄黑标记牌图案让它和现场那些牌属于同一套东西。"),
    ("case-10", "10", "三年房龄履历曲线", 1600, 1000,
     "桌面浏览器窗口（年度视图）", "陆文君（明年还要经手另外 7 套）", "2026-10-01",
     "看三年曲线，回答「哪些位置在反复坏」和「这套房被照顾得怎么样」",
     "年度视图 · 下一次体检 2027-01-05",
     "39 个月逐月读数做成主曲线，两次维修是曲线上肉眼可见的两个下降台阶——履历不是表格，是能看出趋势的东西。"),
]

CSS = """
  :root { --ink:#141b26; --ink2:#43536b; --ink3:#8494a8; --paper:#f7f4ee;
          --card:#fff; --line:#ded7cb; --blue:#1e4fd8; --yellow:#f5c518;
          --green:#1f8a5c; --red:#d93b2b; --amber:#e08a0b; --night:#0e1622; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--paper); color:var(--ink);
         font-family:"Inter","Noto Sans CJK SC","PingFang SC","Microsoft YaHei",sans-serif;
         line-height:1.65; }
  .wrap { max-width:1180px; margin:0 auto; padding:0 24px 80px; }
  header.hero { background:var(--night); color:#fff; padding:44px 0 40px;
                border-bottom:6px solid var(--yellow); }
  header.hero .wrap { padding-bottom:0; }
  .tag { display:inline-block; background:var(--yellow); color:#14181f;
         font-weight:800; font-size:12px; letter-spacing:1.4px;
         padding:5px 11px; border-radius:6px; }
  h1 { font-size:34px; margin:16px 0 6px; letter-spacing:-.5px; }
  .sub { color:#a8b6c6; font-size:15px; margin:0 0 18px; }
  .decl { border-left:3px solid var(--amber); background:#1a2635; color:#c8d4e0;
          font-size:13px; padding:12px 16px; border-radius:0 8px 8px 0; }
  .decl b { color:var(--yellow); }
  h2 { font-size:20px; margin:44px 0 6px; padding-bottom:10px;
       border-bottom:1px solid var(--line); }
  h2 .n { color:var(--ink3); font-family:"DejaVu Sans Mono",monospace; margin-right:10px; }
  .lede { color:var(--ink2); font-size:14px; margin:0 0 18px; max-width:860px; }
  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(330px,1fr)); gap:20px; }
  figure { background:var(--card); border:1px solid var(--line); border-radius:12px;
           overflow:hidden; margin:0; display:flex; flex-direction:column; }
  figure .shot { display:block; background:#ece7dd; text-align:center;
                 border-bottom:1px solid var(--line); }
  figure .shot img { max-width:100%; height:auto; display:block; margin:0 auto; }
  .cap { padding:14px 16px 16px; }
  .cap .row { display:flex; align-items:baseline; gap:8px; margin-bottom:4px; }
  .cap .id { font-family:"DejaVu Sans Mono",monospace; font-weight:700;
             font-size:12px; color:var(--ink3); letter-spacing:1px; }
  .cap .dims { margin-left:auto; font-family:"DejaVu Sans Mono",monospace;
               font-size:11px; color:var(--ink3); background:#f2efe9;
               padding:2px 8px; border-radius:5px; }
  .cap h3 { font-size:16px; margin:2px 0 8px; }
  .cap dl { margin:0; font-size:12.5px; color:var(--ink2); }
  .cap dt { color:var(--ink3); font-size:11px; letter-spacing:.6px; margin-top:8px; }
  .cap dd { margin:1px 0 0; }
  .links { margin-top:12px; display:flex; gap:8px; flex-wrap:wrap; }
  .links a { font-size:12px; text-decoration:none; color:var(--blue);
             border:1px solid #c9d6f5; border-radius:7px; padding:4px 10px; }
  .links a:hover { background:#eef2fe; }
  table.facts { width:100%; border-collapse:collapse; font-size:13.5px; }
  table.facts th, table.facts td { text-align:left; padding:8px 10px;
      border-bottom:1px solid var(--line); vertical-align:top; }
  table.facts th { color:var(--ink3); font-weight:600; font-size:12px; width:150px; }
  table.facts td.mono { font-family:"DejaVu Sans Mono",monospace; }
  .pill { display:inline-block; font-size:11px; padding:2px 8px; border-radius:999px;
          font-weight:700; }
  .p-new { background:#fbe5e2; color:#a32b1e; }
  .p-fix { background:#ddf0e6; color:#146244; }
  .p-same { background:#d9e2fb; color:#14379b; }
  .p-hold { background:#fdf0d9; color:#96590a; }
  .note { background:#fffdf6; border:1px solid #f0e2bd; border-radius:10px;
          padding:14px 18px; font-size:13.5px; color:var(--ink2); margin-top:18px; }
  .note b { color:var(--ink); }
  .chain { font-family:"DejaVu Sans Mono",monospace; font-size:12.5px;
           line-height:2.0; color:var(--ink2); background:#fff;
           border:1px solid var(--line); border-radius:10px; padding:14px 18px;
           overflow-x:auto; white-space:pre; }
  footer { margin-top:56px; padding-top:18px; border-top:1px solid var(--line);
           font-size:12px; color:var(--ink3); }
  code { font-family:"DejaVu Sans Mono",monospace; font-size:12px;
         background:#f2efe9; padding:1px 5px; border-radius:4px; }
"""


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


cards = []
for cid, n, title, w, h, carrier, actor, when, intent, state, note in CASES:
    cards.append("""    <figure>
      <a class="shot" href="{cid}/final.png" target="_blank" rel="noopener">
        <img src="{cid}/final.png" alt="{cid} {title}" loading="lazy" /></a>
      <div class="cap">
        <div class="row"><span class="id">{cid}</span>
          <span class="dims">{w} &times; {h}</span></div>
        <h3>{n} · {title}</h3>
        <dl>
          <dt>载体</dt><dd>{carrier}</dd>
          <dt>谁在看 · 什么时候</dt><dd>{actor} · {when}</dd>
          <dt>用户意图</dt><dd>{intent}</dd>
          <dt>状态</dt><dd>{state}</dd>
          <dt>视觉主张</dt><dd>{note}</dd>
        </dl>
        <div class="links">
          <a href="{cid}/final.png" target="_blank" rel="noopener">原始尺寸 PNG</a>
          <a href="{cid}/final.snapshot">同版 DSL</a>
          <a href="{cid}/case.md">自检说明</a>
        </div>
      </div>
    </figure>""".format(cid=cid, n=n, title=esc(title), w=w, h=h,
                         carrier=esc(carrier), actor=esc(actor), when=esc(when),
                         intent=esc(intent), state=esc(state), note=esc(note)))

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>房谱 HOMESPEC · B05 作品集（10 个关键使用画面）</title>
<style>{css}</style>
</head>
<body>

<header class="hero">
  <div class="wrap">
    <span class="tag">B05 · 从零构想产品并设计 10 个关键使用画面</span>
    <h1>房谱 HOMESPEC · 住址履历</h1>
    <p class="sub">
      同一套房 <code>云栖里 3 号楼 1602 室</code>，12 个位置锚点，39 个月，
      10 个真实会被打开的时刻。全部画面由 Snapshot DSL 渲染，载体分别是
      手机竖屏 ×3 / 手机横屏 / 桌面 ×2 / 打印 A4 / 手表 / 手机长图 / 打印 A5。
    </p>
    <div class="decl">
      <b>虚构声明</b> · 房谱 HOMESPEC 是本任务从零构想的虚构产品，
      不是任何已部署、已上市或已申请专利的产品。品牌、公司名、人物、地址、单号、
      金额、读数、评分全部为<b>自拟演示数据</b>。本任务<b>未做任何真实用户验证</b>
      （无可用受访者、未做可用性测试、未做付费意愿调查）。全部画面为静态设计，
      不存在可运行的前端程序或后端服务；界面中的差分、识别与责任划分是设计意图，
      不是已实现的算法输出。
    </div>
  </div>
</header>

<div class="wrap">

  <h2><span class="n">00</span>产品与共同事实</h2>
  <p class="lede">
    住址履历在人手里断了：一套房从交付到再次交付通常经历 3–8 次入住，
    每一任租客都拍照，但照片没有坐标、没有时间顺序，也没有和下一次比对过。
    房谱把一间房拆成一组固定的位置锚点，让每一次进入、维修、退租
    都在<b>同一个锚点</b>上留下可核对的一条记录。
  </p>
  <table class="facts">
    <tr><th>住址</th><td class="mono">云栖里 3 号楼 1602 室（虚构）</td></tr>
    <tr><th>锚点</th><td>12 个，编号规则 <code>区域-序号</code>；重点出现
      K-01 / K-02 / B-02 / W-02 / A-01 / E-02</td></tr>
    <tr><th>时间线</th><td class="mono">2023-07-01 入住 → R-2403-118 →
      R-2506-042 → 2026-09-30 退租（共 39 个月）</td></tr>
    <tr><th>退租差分</th><td>
      <span class="pill p-same">未变化 5</span>
      <span class="pill p-fix">已修复 2</span>
      <span class="pill p-new">新增损伤 2</span>
      <span class="pill p-hold">无法比对 1</span>
      <span style="color:#8494a8">（另 2 个锚点本轮未涉及）</span></td></tr>
    <tr><th>责任判定</th><td class="mono">租客 ¥200 = K-01 划痕 ¥120 +
      W-02 钉孔 ¥80；暂挂项不判责</td></tr>
    <tr><th>电表读数</th><td class="mono">入住 1284 kWh → 退租 3611 kWh</td></tr>
    <tr><th>人物</th><td>林知远（租客）· 陆文君（房东）· 老周（维修）·
      周敏（云栖里运营）</td></tr>
    <tr><th>三条机制</th><td>① 锚点：拍不到标记牌一律拒绝入档　
      ② 差分：Δ = 本次 − 上一次，只有「新增损伤」进入责任判定　
      ③ 履历：记录跨人跨年累积，可一次性交给下一任</td></tr>
    <tr><th>明确不做</th><td>不做签约 / 支付托管 / 租赁撮合；不做 AI 修图；
      不上传无锚点的随手拍</td></tr>
  </table>

  <h2><span class="n">→</span>旅程顺序</h2>
  <p class="lede">
    十件不是十个界面，是同一条被走完的旅程。每一件回答一个具体的人在具体时刻
    需要回答的问题，并把状态交给下一件：
  </p>
  <div class="chain">01 学会规则 → 02 确认成立 → 03 被拒绝（失败分支）
04 全轮判定（E-02 暂挂在表里占一整行）
05 签字                                    06 抬腕提醒（同一 10-07 期限，还剩 2 天）
07 往回追溯（解释「已修复 2」的依据） → 08 交给下一任租客
09 半年后贴在冰箱上（不依赖谁还会打开 App） → 10 回到 39 个月曲线
                                                    ↓
                            底部「加入下一轮日常轮拍」接回 01 的第一次拍摄</div>

  <h2><span class="n">01–10</span>十个关键使用画面</h2>
  <p class="lede">
    每一件都贴合它真实的载体与观看环境：手机取景页、手机横屏回执、手机失败告警、
    桌面判定表、打印签字页、手表提醒、手机工单详情、手机长图分享卡、打印冰箱卡片、
    桌面年度视图。点击任意一张可打开原始尺寸 PNG。
  </p>
  <div class="grid">
{cards}
  </div>

  <div class="note">
    <b>跨画面一致性</b> · 住址、锚点编号、两条工单号、时间线、差分四分类、
    责任金额、电表读数在 10 张图中含义完全一致。E-02 是贯穿全程的那一条线：
    case-03 被拒 → case-04 暂挂 → case-05 签字时仍未决 → case-06 抬腕补拍提醒 →
    case-08 交接时坦白告知 → case-09 卡片上写「不是没问题，是还不知道」→
    case-10 排进下一轮半年轮拍。一个产品在失败时诚实，比它在成功时好看更重要。
  </div>

  <h2><span class="n">→</span>文稿入口</h2>
  <p class="lede">
    完整的状态传递（含每张画面携带了哪些量）见
    <a href="journey.json">journey.json</a>；作品映射、自定完成标准与逐件自检证据见
    <a href="portfolio.json">portfolio.json</a>；策展逻辑见
    <a href="portfolio.md">portfolio.md</a>；DSL 应用与踩坑见
    <a href="snapshot-usage.md">snapshot-usage.md</a>；产品说明与验证边界见
    <a href="product-brief.md">product-brief.md</a>。
  </p>

  <footer>
    全部 10 张 PNG 均为 <code>POST https://open-snapshot.muedsa.com/snapshot</code>
    的服务原始响应字节，未做任何后处理；每张配一份同名的完整
    <code>.snapshot</code> DSL。本页是<b>纯静态 HTML，不含任何 &lt;script&gt;</b>，
    只使用相对链接与内联样式，不依赖任何远程脚本或 CDN。
    <br />
    token / 图像用量 / 费用等平台未提供的计量一律为 <code>null</code>，见
    <a href="task-metrics.json">task-metrics.json</a>。
  </footer>
</div>
</body>
</html>
""".format(css=CSS, cards="\n".join(cards))

with io.open(os.path.join(D, "gallery.html"), "w", encoding="utf-8",
             newline="\n") as fh:
    fh.write(html)

print("gallery.html written: %d bytes, %d static cards, 0 script tags"
      % (len(html.encode("utf-8")), len(cards)))