# case-09 · Repair Commons modular timetable board

- 状态：completed
- 品牌与数据：FICTIONAL_DEMO：Invented Repair Commons with six demo sessions, fictional rooms, times and sign-up rules; no real community service is represented.
- 受众：Residents checking a fictional neighbourhood repair-café programme
- 使用环境：A3 landscape board at a fictional community hall; three equal programme columns must remain readable when printed or reduced for a noticeboard photo
- 用户目标：Choose a demo workshop by day and time, find the room and understand whether advance sign-up is needed
- 尺寸：1754×1240

## 场景与视觉选择

Proportional day bands and aspect-ratio-locked icons sit above three finite Flexible columns; the layout derives order from constraints rather than hundreds of absolute positions and remains balanced at different reductions.

## 实际自检

修理共享站包含SAT 11.07/11/11三日共六场，时间、标题、房间、报名状态一一对应；缩减探针无裁切，图标与进度条比例稳定。

查看时间：2026-11-24T16:53:14.703+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `f7a1926657ff318f499c84943061909d78281a3c91cb58e64f1ce19fe7c6fdd5`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- C01：Six demo sessions show matching day, time, title, room and sign-up rule with no swapped values.；检查方法：Session-table reconciliation and full-size review.；结果：通过。
- C02：Three day columns remain aligned and balanced, with all six sessions in the correct column.；检查方法：Inspect shared column edges and row order.；结果：通过。
- C03：A reduced-width test shows stable proportions, undistorted icons and wrapped text without overlap or clipping.；检查方法：Generate a temp-only reduced constraint probe after authorization and compare geometry.；结果：通过。
- C04：The board clearly identifies the programme and sign-up rules as fictional demo information.；检查方法：Inspect header and footer.；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
