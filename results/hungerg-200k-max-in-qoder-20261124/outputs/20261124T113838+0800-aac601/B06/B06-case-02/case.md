# B06-case-02 · Can I Still Get There?

- 状态：completed
- 品牌与数据：{'problem_evidence': 'A line diagram shows geography but not service state; a disruption list shows state but not journey consequence. Design hypothesis only.', 'type': 'fictional demonstration', 'demo_values': {'line': 'Blue Line', 'closed_segment': 'Harbor–Market', 'origin': 'Harbor', 'destination': 'Museum', 'replacement_bus': 'Harbor–Market', 'remaining_train': 'Market–Museum', 'extra_minutes': 12}, 'limitations': 'All stations, service states, times, and the replacement bus are fictional. This is not live transit information.'}
- 受众：A commuter facing a partial train-line disruption
- 使用环境：Landscape station display and mobile companion view
- 用户目标：Determine whether the destination is still reachable, which stations are affected, and where to change or wait.
- 尺寸：1600×1000

## 场景与视觉选择

A service-state graph where the closed segment becomes a broken rail bridged by a bus ribbon; the user's origin/destination remain anchored while unaffected service recedes.

## 实际自检

YES答案先于细节；Harbor–Market闭合、替代巴士、Market换乘和Market–Museum列车形成完整路径；+12分钟明确为虚构估计，站点标签不被线路穿过。

查看时间：2026-11-24T18:23:16.075+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `365cab259bc812275088df0d2318afe28a90316cd890b12b91a61e8649781138`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- B06-02-C1：The closed Harbor–Market rail segment, replacement bus, and continuing Market–Museum train are unambiguous.；检查方法：Trace the full Harbor-to-Museum path and read every service-state label.；结果：通过。
- B06-02-C2：The answer to 'Can I still get there?' is visible before detailed disruption information.；检查方法：Inspect the top-level journey answer and visual hierarchy.；结果：通过。
- B06-02-C3：The 12-minute extra time is marked demo and is not presented as a live estimate.；检查方法：Inspect the time badge and fictional-demo notice.；结果：通过。
- B06-02-C4：Station labels remain readable at display distance and no route line crosses text.；检查方法：Review full PNG at target distance and crops around the interchange.；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
