# Root 完成脚本加强

沿用运行20261002-204314-6f31。按 root 授权修改 `root-review-close.cjs`，原脚本已备份 `root-review-close-before-hardening-000001.cjs`。

实际视觉查看仍完全来自 root 的真实 view_image 操作及显式声明，脚本不推断视觉。新增 preflight 在登记新查看事件前读取声明图片的实际 SHA-256，核验覆盖本题全部已登记最终图片的实际字节；允许 root 实际打开原服务响应或最终 PNG，二者通过原始字节哈希对应。未覆盖任何最终图即失败，没有最终图也不能关闭。

新增 postclose 审查失败分支：先以 taskEnd partial 保存失败项、真实 postclose 审查路径与恢复说明，再抛错；不让 current state 留在 completed。既有报告、API与审查文件序号规则保留。

只执行 `node --check`，语法检查通过。未执行此真实完成脚本，未登记看图、未改真实状态、指标、报告或请求日志。

另一个独立只读检查记录 `resume-integrity-000001.json` 对 A01–A05 共6张最终 PNG 的必需文件、实际尺寸、原始字节、DSL配对、请求与查看元数据、指标、总画廊图片/DSL链接以及本地报告链接完成核验：passed=true、issues=[]，当时当前状态 artifact 指针无重复/缺失警告。该检查不提供任何视觉或内容合格声明。
