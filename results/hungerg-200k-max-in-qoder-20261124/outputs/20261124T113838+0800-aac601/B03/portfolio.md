# B03 作品集策展

十件作品把Snapshot当作可精确控制的信息材料：剪切、变换、两种模糊、混合、富文本、程序纹样、渐变、约束和透明度分别解决票券、导览、海报、宣传册、市集、日程与活动视觉中的真实问题。统一原则是让技术决定视觉机制，而让文字、数据和使用任务决定信息边界。

## case-01 · Night Ferry cut-out ticket

- 受众：Passengers on a fictional evening river ferry
- 场景：Small perforated-style admission card held at the gangway and kept as a souvenir; read at 20-40 cm
- 目标：Confirm departure, boarding side, cabin and demo booking reference before joining the queue
- 视觉：The ticket's central porthole and wave edge are actual EVEN_ODD cut-outs revealing a contrasting backing; the silhouette carries the ferry identity while a strict information grid remains uncut.
- 内容：FICTIONAL_DEMO：Invented Night Ferry service, fictional sailing time, pier, cabin, booking reference and terms; no real transport operator or ticket is represented.
- [查看作品](case-01/final.png) · [完整DSL](case-01/final.snapshot) · [用例说明](case-01/case.md)

## case-02 · Crosswind cycling route poster

- 受众：Occasional urban cyclists planning a fictional low-traffic route
- 场景：Portrait poster at a fictional bike cooperative and community noticeboard; viewed first at 2 metres then approached for turns
- 目标：Follow the demo route in order, recognise key turn types and find the start, finish and caution point
- 视觉：Route arrows are separate transformed DSL modules rotated and translated around explicit origins, forming a diagonal path through a strict typographic grid; the geometry reads as motion without becoming an unreadable map.
- 内容：FICTIONAL_DEMO：Invented Crosswind route through invented streets, five fictional turns, demo distance and caution note; not a navigable map or safety-certified route.
- [查看作品](case-02/final.png) · [完整DSL](case-02/final.snapshot) · [用例说明](case-02/case.md)

## case-03 · Glasshouse visitor information panel

- 受众：Visitors entering a fictional botanical glasshouse, including people who need calm, clear orientation
- 场景：Landscape information panel mounted beside the entrance; read at 0.5-1.5 metres with a planted background represented in DSL
- 目标：Understand opening route, three demo climate zones, photography rule and where to ask for help
- 视觉：A translucent information card sits over a DSL-built layered foliage background; BackdropFilter softens only the already-painted background while the route and typography remain sharp.
- 内容：FICTIONAL_DEMO：Invented Lumen Glasshouse with three fictional climate rooms, demo route and visitor rules; no real facility or botanical guidance is asserted.
- [查看作品](case-03/final.png) · [完整DSL](case-03/final.snapshot) · [用例说明](case-03/case.md)

## case-04 · Low Tide Observatory depth poster

- 受众：Families and students attending a fictional coastal-observatory open evening
- 场景：Portrait poster at a fictional visitor centre; viewed at 1-4 metres and approached for the demonstration schedule
- 目标：Understand the shallow-to-deep visual theme, identify the three demo activities and find start time and meeting point
- 视觉：Three DSL-built wave layers move from crisp foreground to deliberately blurred distant layers using ImageFiltered; sharp type and activity cards sit above the depth field to preserve utility.
- 内容：FICTIONAL_DEMO：Invented Low Tide Observatory event, fictional activity names, times and meeting point; abstract depth bands are illustrative, not measured ocean data.
- [查看作品](case-04/final.png) · [完整DSL](case-04/final.snapshot) · [用例说明](case-04/case.md)

## case-05 · Two Lantern Theatre cast billboard

- 受众：Potential audience members choosing a fictional community-theatre production
- 场景：Landscape billboard at a fictional arts venue; viewed from across a piazza before approaching for cast and dates
- 目标：Identify the play, sense its two-sided conflict, see performance dates and find the fictional venue
- 视觉：Two monochrome DSL portrait silhouettes overlap in the centre; ColorFiltered blend modes create controlled cobalt/coral duotone regions while the title and dates remain outside the blend zone.
- 内容：FICTIONAL_DEMO：Invented Two Lantern Theatre production 'The Other Side of Noon', invented cast names, fictional dates and venue; all portrait geometry is original DSL construction.
- [查看作品](case-05/final.png) · [完整DSL](case-05/final.snapshot) · [用例说明](case-05/case.md)

## case-06 · Fix-It Club inline workshop leaflet

- 受众：Adults attending a fictional community repair workshop for the first time
- 场景：A5 portrait leaflet handed out at sign-in and read seated at a workbench
- 目标：Bring the right items, follow safety steps in order and understand what help is available at each demo station
- 视觉：Short instructions are genuine mixed text flows: DSL-built icons inside WidgetSpan stay inline with wrapped sentences, while station rows and a tools checklist provide separate reading structures.
- 内容：FICTIONAL_DEMO：Invented Fix-It Club with three fictional repair stations, demo tools list and beginner safety steps; no real safety certification or repair instruction is claimed.
- [查看作品](case-06/final.png) · [完整DSL](case-06/final.snapshot) · [用例说明](case-06/case.md)

## case-07 · Hand & Vessel fair pattern wrap

- 受众：Visitors and makers at a fictional ceramics fair
- 场景：Wide entrance banner above a fictional craft-market counter; read at 2-6 metres with the pattern functioning as recognition rather than fine detail
- 目标：Recognise the fair, find demo opening hours and locate the fictional maker hall
- 视觉：A repeating original tile creates a continuous ceramic-pattern field, explicitly fitted and scaled; large DSL title panels and a location block interrupt the field so it never competes with essential information.
- 内容：FICTIONAL_DEMO：Invented Hand & Vessel fair, fictional date, hours and hall location. A small original abstract vessel/arc tile is planned as a supporting asset; the banner structure, motifs, typography and information remain DSL-led.
- [查看作品](case-07/final.png) · [完整DSL](case-07/final.snapshot) · [用例说明](case-07/case.md)

## case-08 · Blue Hour sky-orientation dial

- 受众：First-time visitors at a fictional community observatory open night
- 场景：Square printed orientation card handed out at a fictional telescope queue; read outdoors at dusk with a small torch
- 目标：Read the demo event timeline, find the three activity zones and understand the dial's direction labels
- 视觉：A radial twilight field and a sweep-gradient outer dial surround a clear central schedule; aligned stops and angular bounds create the visual transition while labels and zone keys stay outside the gradient.
- 内容：FICTIONAL_DEMO：Invented Blue Hour open night with fictional 18:30-21:00 schedule and zones. The dial is an orientation graphic, not a real star chart, weather forecast or astronomical prediction.
- [查看作品](case-08/final.png) · [完整DSL](case-08/final.snapshot) · [用例说明](case-08/case.md)

## case-09 · Repair Commons modular timetable board

- 受众：Residents checking a fictional neighbourhood repair-café programme
- 场景：A3 landscape board at a fictional community hall; three equal programme columns must remain readable when printed or reduced for a noticeboard photo
- 目标：Choose a demo workshop by day and time, find the room and understand whether advance sign-up is needed
- 视觉：Proportional day bands and aspect-ratio-locked icons sit above three finite Flexible columns; the layout derives order from constraints rather than hundreds of absolute positions and remains balanced at different reductions.
- 内容：FICTIONAL_DEMO：Invented Repair Commons with six demo sessions, fictional rooms, times and sign-up rules; no real community service is represented.
- [查看作品](case-09/final.png) · [完整DSL](case-09/final.snapshot) · [用例说明](case-09/case.md)

## case-10 · Shadow Lab eclipse-night poster

- 受众：Curious teenagers and adults considering a fictional community astronomy evening
- 场景：Portrait poster at a fictional library and school noticeboard; viewed at 1-4 metres and approached for the demonstration programme
- 目标：Recognise the eclipse theme, understand that activities are demonstrations, and find fictional start time and meeting place
- 视觉：Translucent orbital discs overlap in a Stack; Opacity groups and ClipOval masks create a luminous eclipse-like focal form while a sharp programme column keeps the poster useful.
- 内容：FICTIONAL_DEMO：Invented Shadow Lab evening with fictional light-and-shadow demonstrations, time and location. The orbital graphic is conceptual and does not depict a predicted eclipse or real celestial positions.
- [查看作品](case-10/final.png) · [完整DSL](case-10/final.snapshot) · [用例说明](case-10/case.md)
