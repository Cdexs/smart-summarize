# v0.5.4 组件自托管下载源 + 多轮缺失链式安装修复

本版本新增技能仓库自托管组件源（提升下载可靠性与受限网络下的下载速度适配），并修复全新环境首次安装无法一次跑通的缺陷。

## ✨ 新特性

- **组件自托管源（GitHub Release `components-v1`）**：
  - **whisper-cli（Windows x64，Vulkan + CPU 通用构建，静态链接）**：Windows x64 的安装候选链以自托管为首——与官方同走 GitHub 资产 CDN、速度一致，且为 Vulkan 构建（AMD/Intel GPU 开箱加速，无 Vulkan 环境自动回退 CPU），同时规避上游 release 资产变动风险（上游 v1.9.3+ 版本 release 资产为空、`latest/download` 恒 404）；
  - **ggml-large-v3-turbo 模型**：候选链**官方优先**（huggingface.co → hf-mirror.com → 自托管兜底）——GitHub 资产通道在受限网络下带宽差（QA 实测约 54KB/s），不作模型首选；
  - 资产清单、SHA256 与 MIT 许可说明见仓库 `models/README.md`。

## 🐛 严重修复

- **全新环境首跑修复（QA D1）**：依赖检查存在两个独立检查点（入口 pip 库预检、音视频组件检查），此前安装完第一轮（如 requests）后，第二轮缺失（whisper-cli + 模型）被直接报「组件安装后仍检测缺失」而放弃，`--download-deps` 无法一次跑通。现 `_handle_missing_deps` 改为**链式循环**：装完一轮自动重跑，暴露的新缺失继续走同一「列出清单 → 确认 → 安装」流程（交互模式每轮再次确认），最多 3 轮；某组件安装后仍缺失时立即返回结构化错误（停滞保护，不重复下载、不死循环）。
- **组件清单体积误报修复**：体积探测曾把 404 响应页的 Content-Length 当作资产大小（显示 29B 之类异常值），现校验 HTTP 状态码后归零并回退已知体积。

**Full Changelog**: https://github.com/Cdexs/smart-summarize/compare/v0.5.3...v0.5.4
