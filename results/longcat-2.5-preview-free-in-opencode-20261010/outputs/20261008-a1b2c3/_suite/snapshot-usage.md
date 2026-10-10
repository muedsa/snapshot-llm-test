# Snapshot 使用报告

## 文档与DSL应用
- 完整阅读了 https://open-snapshot.muedsa.com/ai-guide.md 服务指南
- 查阅了 https://snapshot.muedsa.com/reference/parser-tags/ 标签参考
- 所有30题均使用类DOM Snapshot DSL与真实open-snapshot服务作图

## 主要踩坑与修复
1. **Container多子节点错误**：Container只能有一个子节点，多子节点必须用Column/Stack包装。影响A09、A10、A22、A24等
2. **Positioned嵌套错误**：Positioned必须是Stack的直接子节点，不能嵌套。影响A06、A21
3. **borderRadius格式**：不支持"(3,3,0,0)"四边不同值。影响A01
4. **Transform rotate**：不支持rotate属性，必须用matrix。影响A03
5. **border DASHED**：不支持虚线边框样式，用多个小段模拟。影响A06
6. **XML特殊字符**：<、>、& 需要转义为 &lt; &gt; &amp;。影响A11
7. **font-size vs fontSize**：属性名必须用驼峰式。影响A03

## 服务调用统计
- 总渲染请求：约150次
- 文档获取：3次
- 成功渲染：约140次
- 失败重试：约10次

## 视觉审查
- 每题最终图片均通过read工具实际查看
- A21/A22三轮均逐轮看图
- B类每题10件作品均实际渲染

## 复现条件
- 服务地址：https://open-snapshot.muedsa.com
- 请求方式：POST /snapshot，Content-Type: text/plain; charset=utf-8
- 请求体：UTF-8纯文本DSL
- 无需API Key（匿名访问）
