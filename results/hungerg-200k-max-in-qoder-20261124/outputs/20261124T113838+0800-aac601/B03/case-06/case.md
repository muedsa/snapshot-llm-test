# case-06 · Fix-It Club inline workshop leaflet

- 状态：completed
- 品牌与数据：FICTIONAL_DEMO：Invented Fix-It Club with three fictional repair stations, demo tools list and beginner safety steps; no real safety certification or repair instruction is claimed.
- 受众：Adults attending a fictional community repair workshop for the first time
- 使用环境：A5 portrait leaflet handed out at sign-in and read seated at a workbench
- 用户目标：Bring the right items, follow safety steps in order and understand what help is available at each demo station
- 尺寸：1240×1754

## 场景与视觉选择

Short instructions are genuine mixed text flows: DSL-built icons inside WidgetSpan stay inline with wrapped sentences, while station rows and a tools checklist provide separate reading structures.

## 实际自检

把坏了的东西带到工作台来包含欢迎语、四项准备、三工位、六项工具、安全步骤和非认证声明；WidgetSpan跟随句子段落，四步完整。

查看时间：2026-11-24T16:53:14.653+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `ee55bd2cd11f2da4d5561f4361cd5648de616c31a481b49717206f40e0ae738d`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- C01：Demo welcome, three station descriptions, tools checklist and four ordered safety steps are complete and readable.；检查方法：Copy inventory and A5-scale review.；结果：通过。
- C02：Inline icons stay within the sentence flow, remain aligned to text and do not become detached at wraps.；检查方法：Inspect every multi-line instruction at 200%.；结果：通过。
- C03：Raw spacing between mixed-script fragments is preserved without accidental formatting newlines or trim.；检查方法：Compare intended strings with rendered line breaks and spacing.；结果：通过。
- C04：The leaflet labels its guidance as fictional demo content and avoids certified-safety claims.；检查方法：Read safety heading and footer.；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
