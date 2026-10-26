# B04 研究笔记 · 「抬头读天——国际云图集十属」

> 建立时间：2026-10-23 13:20（首件渲染之前）
> 主题：世界气象组织（WMO）《国际云图集》十云属系统——公众如何识别云、云如何预告天气
> 原则：区分「已证实事实（WMO/NOAA/HKO 定义与数据）/ 来源结论 / 自行解释 / 演示内容」；
>      所有数值可追到 sources.json 的 source_id + 定位。

## 一、来源清单（实际访问）

| sid | 来源 | 访问方式 | 用途 |
|---|---|---|---|
| S1 | WMO International Cloud Atlas — Levels（含表 6 各纬度层面高度）cloudatlas.wmo.int/en/some-useful-concepts-levels.html | WebFetch/WebSearch | 三层高度（极地/温带/热带）、十属分层 |
| S2 | WMO International Cloud Atlas — Cirrus (Ci) (Howard 1803) cloudatlas.wmo.int/en/cirrus-ci.html | WebSearch | 卷云定义原文 |
| S3 | WMO《Classifying clouds》（世界气象日 2017）wmo.int/world-meteorological-day-2017/classifying-clouds | WebFetch | 十属体系、拉丁词根、1803 霍华德、约 100 种/变种组合、特殊云 |
| S4 | WMO CIMO Guide 第 15 章（2018 预印）PDF：old.wmo.int/.../8_I_15_en_MR_clean.pdf | curl 下载 + pymupdf 提取表 15-1 | 十属云底高度「常用范围/更宽范围」（温带，台站 ≤150 m） |
| S5 | NOAA JetStream《Ten Basic Clouds》noaa.gov/jetstream/clouds/ten-basic-clouds | WebFetch | 十属 WMO 定义英原文、高中低分组、成分、天气意义、视宽 |
| S6 | 香港天文台《云》电子书 kids.weather.gov.hk/eBook/ebook_cloud/（m_ebook_cloud04/05/06/07_e） | WebFetch | 各属种/变种/附属特征清单（引自 WMO ICA）、30° 判别规则、1 cm 指宽≈1° |
| S7 | NWS（weather.gov）Stormbuster Winter 2005-06：halos/sun dogs | WebFetch | 22° 晕、六角冰晶、晕与锋面气旋关联 |
| S8 | Wikipedia《22° halo》（Wikiwand 镜像） | WebSearch 摘录 | 最小偏向角 21.76°–22.37°；红 21.54°/蓝 22.37°；内红边 |
| S9 | Meteo.es Meteopedia《Solar halo》meteo.es/en/meteopedia/solar-halo | WebFetch | 22° 晕描述、民谚气象基础、雨 12–36 h |

## 二、核心数据（逐条可溯源）

### 2.1 三层高度（WMO ICA 表 6，S1）
- 高云族：极地 3–8 km｜温带 5–13 km｜热带 6–18 km
- 中云族：极地 2–4 km｜温带 2–7 km｜热带 2–8 km
- 低云族：三纬度均为 地表–2 km
- 例外：Altostratus 常延伸更高；Nimbostratus 通常贯穿三层；Cumulus/Cumulonimbus 云底在低层但顶部可达中高层

### 2.2 十属云底高度（WMO CIMO Guide 表，温带，S4）
| 属 | 常用范围 (m) | 常用 (ft) | 更宽 (m) | 更宽 (ft) |
|---|---|---|---|---|
| Stratus | 地表–600 | 地表–2 000 | 地表–1 200 | 地表–4 000 |
| Stratocumulus | 300–1 350 | 1 000–4 500 | 300–2 000 | 1 000–6 500 |
| Cumulus | 300–1 500 | 1 000–5 000 | 300–2 000 | 1 000–6 500 |
| Cumulonimbus | 600–1 500 | 2 000–5 000 | 300–2 000 | 1 000–6 500 |
| Nimbostratus | 地表–3 000 | 地表–10 000 | —（备注：天气图上视为中云，可延伸至其他层） |
| Altostratus | 2 000–6 000 | 6 500–20 000 | —（备注：增厚伴云底降低可成雨层云） |
| Altocumulus | （与 Altostratus 共用合并单元格）2 000–6 000 | 6 500–20 000 | — |
| Cirrus / Cirrostratus / Cirrocumulus | 6 000–12 000 | 20 000–40 000 | —（备注：积雨云消散的卷云冬季可远低于 6 km） |
- 脚注 a：台站高于 150 m 时，低云云底常低于表中值

### 2.3 视宽判别（S5/S6）
- Cirrocumulus 元素视宽 <1°（小指）
- Altocumulus 1–5°（小指与三指之间）
- Stratocumulus >5°（三指）；且多在高于地平 30° 处（与高积云判别）
- 1 cm 尺子臂长处一指宽 ≈ 1°（S6）

### 2.4 光学现象判别
- Cirrostratus：几乎必有晕（22° 晕；最小偏向角 21.76°–22.37°，红 21.54° 内边、蓝 22.37° 外边；S7/S8/S9）
- Altocumulus/Stratocumulus 薄处：华（corona，红外蓝内，几度内；S5）
- Altostratus：无晕、地面物影不可见；太阳如毛玻璃（S5/S6）
- Stratus：太阳轮廓清晰可辨；极低温偶有晕（S5）

### 2.5 拉丁词根（S3）
- Stratus/strato = 平展层状；Cumulus/cumulo = 堆积/蓬松；Cirrus/cirro = 羽毛/丝缕；
  Nimbus/nimbo = 降雨；Alto = 中层（拉丁原意"高"）

### 2.6 历史与体系（S3）
- 1803 年 Luke Howard《论云的变形》建立拉丁命名体系
- 十属 → 种（形状/结构）→ 变种（透明度/排列），约 100 种组合
- 新特殊云：Homogenitus（人为云，如 contrails 航迹云）、 supplementary feature Asperitas（糙面云）、新种 Volutus（滚云）

## 三、十件作品编辑路线（垂直阅读）

总览（case-01）→ 方法（case-02）→ 高云三属（03–05）→ 中云三属（06–08）→ 低云二属（09–10）→ 对流塔（11）
读者动线：从地面向上登顶，再随积雨云俯瞰「云的工厂」。

## 四、演示与解释的边界

- 云图插画为 DSL 绘制的**风格化示意图**，非照片；标注「示意图」
- 「天气意义」仅引用来源结论（S3/S5/S9），不作额外外推
- 高度范围为「常用/更宽」两栏并列，不用单值冒充精度
- 民谚（日晕三更雨/鱼鳞天）标注为民谚并附其气象基础（S9 明确说明有基础但非必然）

## 五、高云三属详单（S6 香港天文台电子书 m_ebook_cloud06_e，逐字摘录）

### Cirrus (Ci) 卷云
- 定义：Detached cloud in the form of white delicate filament, mostly appearing as a white patch or a narrow band. These clouds have a fibrous appearance, or a silky sheen, or a mixture of both.（分离云，白色纤细丝缕状，常呈白片或窄带；纤维状光泽、丝绢光泽或两者兼有）
- 辨识：whiter than any other genera in its vicinity（比邻近任何属更白）；日落时最先染色、黎明最先显色；与 Cc 之别=纤维/丝绢 vs 颗粒/波纹；与 Cs 之别=仅 Ci 为不连续结构、水平范围有限
- 种（species）：fibratus, uncinus, spissatus, castellanus
- 变种（varieties）：intortus, radiatus, vertebratus, duplicatus
- 附属/从属：mamma

### Cirrostratus (Cs) 卷层云
- 定义：Transparent whitish cloud veil with fibrous or smooth appearance, partially or totally covering the sky often in an irregular manner; 不全覆盖时边缘清晰，否则多毛边；外观与厚度随时间变化很小，似慢行
- 成分：薄层几乎全由冰晶组成；halo occurrence is a clear evidence of the presence of cirrostratus（出现晕是卷层云在场的明确证据）；霾可貌似卷层云，但其独特的黄/褐色可区分
- 日高角 >30° 时地面可见物体投影
- 种：fibratus, nebulosus；变种：undulatus, duplicatus；附属：无

### Cirrocumulus (Cc) 卷积云
- 定义：White patch or thin sheet cloud without shading, composed almost exclusively of ice crystals; often forms from transformation of cirrus or cirrostratus; rippled and subdivided into very small cloudlets in the form of grains or ripples, most of which have an optical width of less than 1 degree（波纹状、分割为极小云粒，光学视宽多 <1°）
- 易混：勿与边缘带极小云粒的消散中高积云混淆
- 种：stratiformis, lenticularis, castellanus, floccus；变种：undulatus, lacunosus；附属：mamma, virga

（中文属名为通行译名；种/变种中文为编译者试译，英文为 WMO ICA 原名——本特辑统一口径）

## 六、NOAA JetStream 十属定义逐字摘录（S5，2026-10-23 复核）

**Cirrus (Ci)**：Detached clouds in the form of white, delicate filaments, mostly in patches or narrow bands. They may have a fibrous (hair-like) and/or silky sheen appearance. / always composed of ice crystals; transparent character depends upon the degree of separation of the crystals; when these clouds cross the sun's disk, they hardly diminish its brightness; exceptionally thick may veil its light and obscure its contour. / Before sunrise and after sunset, cirrus are often colored bright yellow or red; lit up long before other clouds and fade out much later; some time after sunset they become gray. / At all hours of the day, cirrus near the horizon are often of a yellowish color (long light path at low angle).

**Cirrocumulus (Cc)**：Thin and white, patchy sheet or layer arranged somewhat-regularly into grains or ripples without shading; most elements have an apparent width of less than one degree (little finger at arm's length). / predominantly ice crystals; often form in connection with cirrus or cirrostratus or from a degraded state of these; short-lived.

**Cirrostratus (Cs)**：Transparent, whitish veil-like clouds with fibrous or smooth appearance; a sheet is very extensive and can cover the whole sky. / when the sun is sufficiently high, the sheet is never thick enough to prevent shadows of objects on the ground. / may look like milky veil of fog (or thin stratus), but distinguished by a halo phenomena nearly always produced around the Sun or Moon shining through a layer of cirrostratus.

**Altocumulus (Ac)**：White and/or gray patchy, sheet, or layered clouds generally composed of laminae, rounded masses, or rolls; may be partly fibrous or diffuse, may or may not be merged. / most regularly arranged small elements have apparent width of one to five degrees (between little finger and three fingers). / when edge or thin semitransparent patch passes in front of sun or moon, a corona appears: red on the outside, blue inside, within a few degrees. / most common mid-level cloud; multiple layers often at different levels; often appears with other types.

**Altostratus (As)**：Gray or bluish sheets/layers of striated or fibrous clouds that totally or partially cover the sky; thin enough to regularly reveal the sun as if seen through ground glass. / do not produce a halo phenomenon nor are shadows of objects on the ground visible. / sometimes virga hangs from altostratus, at times reaching the ground causing very light precipitation.

**Nimbostratus (Ns)**：Resulting from thickening altostratus; dark gray cloud layer diffused by falling rain or snow; thick enough throughout to blot out the sun. / Low, ragged clouds frequently occur beneath and sometimes merge with its base. / cloud base lowers as precipitation continues; often erroneously called a low-level cloud; both As and Ns can extend into the high level.

**Cumulus (Cu)**：Detached, generally dense clouds with sharp outlines that develop vertically in the form of rising mounds, domes, or towers with bulging upper parts often resembling a cauliflower. / sunlit parts mostly brilliant white, bases relatively dark and horizontal. / over land develops on days of clear skies due to diurnal convection; appears in the morning, grows, then more or less dissolves toward evening.

**Cumulonimbus (Cb)**：The thunderstorm cloud; heavy and dense in the form of a mountain or huge tower; upper portion usually smoothed, fibrous, or striated and nearly always flattened in the shape of an anvil or vast plume. / base often very dark; low ragged clouds commonly beneath, may or may not merge; produce precipitation, sometimes virga; also hail and tornadoes.

**Stratocumulus (Sc)**：Gray or whitish patchy, sheet, or layered clouds that almost always have dark tessellations (honeycomb appearance), rounded masses, or rolls; except for virga non-fibrous, may or may not be merged. / regularly arranged small elements with apparent width of more than five degrees (three fingers at arm's length).

**Stratus (St)**：Generally gray cloud layer with a uniform base which may, if thick enough, produce drizzle, ice prisms, or snow grains. / when the sun is visible through this cloud, its outline is clearly discernible. / when a layer breaks up and dissipates, blue sky is seen. / sometimes appearing as ragged sheets; do not produce a halo except occasionally at very low temperatures.

**高云族总述**：Cirrus (Ci), cirrocumulus (Cc), cirrostratus (Cs) are high level clouds; typically thin and white, but can appear in a magnificent array of colors when the sun is low on the horizon.

## 七、中云三属详单（S6 香港天文台电子书 m_ebook_cloud05_e，逐字摘录）

**中云族总述**：云底约 2 000–6 000 m；较低处主要为水滴，较高处为过冷水滴与冰晶；热带中云顶可达 8 000 m。

### Altocumulus (Ac) 高积云
- 定义：white, grey, or both white and grey cloud block or cloud layer; usually has shading in some parts; composed of laminae, rounded masses or rolls; sometimes looks fibrous or dispersing; most regularly arranged small cloud blocks have an apparent width of between 1 and 5 degrees
- 易混：cirrocumulus 与 stratocumulus；有时下垂纤维状 virga；薄处常见 coronae（华）与 irisation（彩云）
- 种：stratiformis, lenticularis, castellanus, floccus
- 变种：undulatus, radiatus, lacunosus, duplicatus, translucidus, perlucidus, opacus
- 附属/从属：mamma, virga
- 脚注：1 cm 尺臂长处一指宽 ≈ 视宽 1°

### Altostratus (As) 高层云
- 定义：greyish or bluish, sheet or striated/fibrous/uniform layer, totally or partly covering the sky, parts thin enough to reveal the Sun vaguely, as if viewing through ground glass
- 无晕；地面无物影；若日月轮廓可辨 → 是高层云而非雨层云；云底较不均；厚薄不均可致亮度差异
- 夜间 As/Ns 难辨时，惯例：无雨雪则记为高层云
- 种：无；变种：translucidus, opacus, duplicatus, undulatus, radiatus
- 附属/从属：mamma, virga, praecipitatio, pannus

### Nimbostratus (Ns) 雨层云
- 定义：grey and dark cloud layer, often brings continuously falling rain or snow, blocks out the Sun; low ragged clouds frequently at the bottom
- 形成：由增厚的高层云发展而来，或发展盛的积雨云铺展增厚而成
- 与层云之别：以是否产生降水区分
- 种：无；变种：无；附属/从属：virga, praecipitatio, pannus

## 八、低云四属详单（S6 香港天文台电子书 m_ebook_cloud04_e，逐字摘录）

**低云族总述**：云底地表–2 000 m（热带如香港约至 6 500 ft）。

### Stratus (St) 层云
- 定义：generally grey with a fairly uniform base, may give drizzle, snow or snow grains; usually small water droplets; sometimes ragged patches
- 形成：层积云云底降低或失去地形抬升支撑时可发展而来；雾层因升温或风速增大被抬升亦可形成
- 种：nebulosus, fractus；变种：opacus, translucidus, undulatus；附属：praecipitatio

### Stratocumulus (Sc) 层积云
- 定义：grey or whitish, block/sheet/layer normally with some dark parts; tessellations, rounded mass or roll shaped clouds (except virga); most regularly arranged small cloud blocks have apparent width of more than 5 degrees
- 30° 规则：若多数规则云块位于地平线上 >30° 且视宽 >5° → 层积云（与高积云判别）
- 一般由水滴组成；层不厚时有时可见 corona 或 irisation
- 种：cumulogenitus, castellanus, lenticularis, stratiformis；变种：translucidus, perlucidus, undulatus, opacus, radiatus, lacunosus, duplicatus；附属：mamma, virga, praecipitatio

### Cumulus (Cu) 积云
- 定义：usually occurs in fine weather; puffy, cotton-like or fluffy, generally dense and sharp outlines; develops vertically as rising mound, dome or tower, bulging upper part often resembles cauliflower; sunlit part mostly white, base relatively dark and flat; sometimes patchy
- 远看可似合并；垂直伸展大可铺展为 Sc/Ac cumulogenitus 或穿入既有层；保持分离仍记为积云；降水性积云在头顶时特征难辨，易与 As/Ns 混淆
- 种：fractus, humilis, mediocris, congestus；变种：radiatus；附属：pileus

### Cumulonimbus (Cb) 积雨云
- 定义：heavy and dense, considerable vertical extent, mountain or huge tower; upper portion partly smooth, small part fibrous, striated or flat; often spreads out as anvil or vast plume; base often dark with scattered clouds, sometimes virga
- 发展：多由大积云发展；亦可由 Sc castellanus 或 Ac castellanus 发展；广布时云底可貌似雨层云
- 降水识别：阵性降水，常较强但不持久；见冰雹/雷/闪电 → 必为积雨云
- 演化标志：穹顶清晰轮廓（水滴）→ 顶部柔软纤维轮廓（冰晶）即 Cu→Cb
- 「云的工厂」：顶部可产出密卷云、高积云、高层云、层积云；砧顶常见，高空风增大时砧向下风方铺展成半砧或巨羽
- 种：calvus（秃）, capillatus（毛发状）；变种：无；附属：incus, mamma, virga, praecipitatio, arcus, tuba, pileus, velum, pannus
