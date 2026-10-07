# A23 实际文档引文定位

## guide-formats

D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000001-response.txt，L3–L3；UTF-16字符串offset[25,154)；源SHA256=2b94151bdfa47e485de3d2412222f5b7fae5bf8b93592aeec586c5dcc1e813aa

使用此服务将 Snapshot DSL 文本渲染为 PNG、JPEG 或 WebP 图片。接口为 `POST /snapshot`，请求体是 UTF-8 纯文本，不是 JSON；成功时响应体是图片二进制。完整接口定义见同源的 `/openapi.yaml`。

## guide-type

D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000001-response.txt，L27–L27；UTF-16字符串offset[700,769)；源SHA256=2b94151bdfa47e485de3d2412222f5b7fae5bf8b93592aeec586c5dcc1e813aa

- 根节点是 `<Snapshot>`；`type` 可为 `png`（默认）、`jpg`、`webp`。输出文件扩展名应与实际格式一致。

## guide-css-alpha

D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000001-response.txt，L29–L29；UTF-16字符串offset[840,946)；源SHA256=2b94151bdfa47e485de3d2412222f5b7fae5bf8b93592aeec586c5dcc1e813aa

- 颜色使用 CSS 语法，包括 `#RGB`、`#RGBA`、`#RRGGBB`、`#RRGGBBAA`；8 位格式的透明度在最后两位。例如不透明红色为 `#FF0000FF`，也可简写为 `#FF0000`。

## openapi-one-binary-result

D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000006-response.txt，L105–L106；UTF-16字符串offset[3104,3156)；源SHA256=492f5144b343076fe816373e4db104c14623985d1f7ae235224ca5e551553435

        "200":
          description: 渲染成功，响应体为图片字节。

## openapi-response-mime

D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000006-response.txt，L116–L128；UTF-16字符串offset[3523,3858)；源SHA256=492f5144b343076fe816373e4db104c14623985d1f7ae235224ca5e551553435

          content:
            image/png:
              schema:
                type: string
                format: binary
            image/jpeg:
              schema:
                type: string
                format: binary
            image/webp:
              schema:
                type: string
                format: binary

## parser-snapshot-contract

D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt，L1–L1；UTF-16字符串offset[3009,3202)；源SHA256=821a9b55b3a2d1498faff3468ef45178a62fff2a2c11f422b7e872975706832c

Snapshot Section titled “Snapshot” 属性 类型 默认值 说明 background color transparent 透明画布背景；白底需显式设置 debug bool false 是否绘制调试信息 type string png png 、 jpg 或 webp 必须是文档第一个开始标签，只能出现一次，并且最终必须有一个根 Widget 子节点。

## parser-transparent-color

D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt，L1–L1；UTF-16字符串offset[1394,1425)；源SHA256=821a9b55b3a2d1498faff3468ef45178a62fff2a2c11f422b7e872975706832c

命名颜色不区分大小写， transparent 表示完全透明。

## parser-rgb-and-supported-color-syntax

D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt，L1–L1；UTF-16字符串offset[1426,1596)；源SHA256=821a9b55b3a2d1498faff3468ef45178a62fff2a2c11f422b7e872975706832c

rgb() 、 rgba() 、 hsl() 、 hsla() 支持逗号分隔或空格加 / 的透明度写法；RGB 通道可用数字或百分比，HSL 色相可用 deg 、 rad 、 grad 、 turn ，饱和度和亮度需写百分比。此处只支持上述常用 CSS 颜色，不支持 currentColor 、 lab() 、 color() 等表达式。

## parser-registered-tags

D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt，L1–L1；UTF-16字符串offset[0,55)；源SHA256=821a9b55b3a2d1498faff3468ef45178a62fff2a2c11f422b7e872975706832c

解析器默认注册 38 个标签。标签名和属性名区分大小写，未知属性会被忽略；除根标签外，属性通常在建树阶段校验。

## parser-single-static-encoding

D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000003-readable.txt，L1–L1；UTF-16字符串offset[831,863)；源SHA256=a9f94fa732898c34591b711e1a97cf13ba208d29ca5c15c268ff90ad475e2b9f

snapshot() 根据根标签的 type 返回编码后的字节。

## parser-not-all-kotlin-paths

D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000003-readable.txt，L1–L1；UTF-16字符串offset[3364,3546)；源SHA256=a9f94fa732898c34591b711e1a97cf13ba208d29ca5c15c268ff90ad475e2b9f

Parser 能力与 Kotlin DSL 不完全相同 Parser 已覆盖常用布局、Flex、约束、变换、裁剪与基础滤镜能力，但仍不是全部 Kotlin DSL 的一一映射。 Stack / IndexedStack 现支持 fit 和 clipBehavior ；任意路径的 ClipPath 、复杂滤镜等仍需 Kotlin DSL。模板设计应以标签参考为准。

## parser-text-source-editable

D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-doc-000004-readable.txt，L1–L1；UTF-16字符串offset[10971,11084)；源SHA256=821a9b55b3a2d1498faff3468ef45178a62fff2a2c11f422b7e872975706832c

Text Section titled “Text” 属性 默认值 说明 text 未设置 属性形式的文本内容 color 未设置 文本颜色 fontSize 未设置 字号 fontFamily 未设置 多个字体用英文逗号分隔

## fonts-inter

D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-fonts-000001-readable.txt，L1–L1；UTF-16字符串offset[0,5)；源SHA256=cfa8a284dd8fe8e93167fdb9c8f1b10591571e5a9ae09538942dfc4b7e368569

Inter

## fonts-noto-sans-cjk-sc

D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/_suite/shared-fonts-000001-readable.txt，L11–L11；UTF-16字符串offset[139,155)；源SHA256=cfa8a284dd8fe8e93167fdb9c8f1b10591571e5a9ae09538942dfc4b7e368569

Noto Sans CJK SC
