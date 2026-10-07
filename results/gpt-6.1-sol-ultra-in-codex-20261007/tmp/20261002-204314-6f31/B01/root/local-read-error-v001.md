# 实际本地路径读取失败

Get-Content尝试producer-02-04/content-v001.json和producer-05-07/content-v001.json，返回路径不存在，命令exit1。该命令的工具输出已真实观察；随后Get-ChildItem确认生产者按case分别写case-NN-content/metadata文件，实际读取了这些文件。没有删除或覆盖记录。这是本地文件路径错误，不是HTTP失败，也不计Snapshot渲染消耗。
