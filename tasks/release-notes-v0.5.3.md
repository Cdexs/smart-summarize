# v0.5.3 组件下载链路网络适配

本版本修复首次安装组件依赖时在受限网络下（上游资产变动、DNS 劫持、源不可达）必然失败的三处下载障碍。建议所有用户升级。

## 🐛 严重修复（全新环境必现）

- **whisper.cpp 预编译资产 404**：上游 v1.9.3 起版本号 release 不再携带预编译资产（资产改挂在 commit 构建 release 上），`releases/latest/download/<asset>` 恒 404，导致全新环境自动安装 whisper-cli 必然失败。现已改为：先经 GitHub API 定位最新含目标资产的 release（自适应上游变化），`latest/download` 次之，最近可用版本 `v1.9.2` 兜底（API 不可用/被限流时）。CPU 版与 NVIDIA cublas 版均适用。
- **ggml 模型下载无镜像回退**：huggingface.co 在部分网络被 DNS 劫持/屏蔽时模型下载必然失败。现按序尝试 `SMART_SUMMARIZE_HF_MIRROR`（兼容 huggingface_hub 惯例的 `HF_ENDPOINT`）→ huggingface.co → 公共镜像 hf-mirror.com，自动切换并在 stderr 标注实际来源；全部失败时给出明确错误与配置提示。
- **pip 安装无镜像回退**：默认源（PyPI）极慢/不可达时报 "No matching distribution found"。现按序尝试 `SMART_SUMMARIZE_PIP_INDEX_URL` → 默认源 → 清华 TUNA → 腾讯云镜像，自动切换并在 stderr 标注实际来源，全部失败时给出手动命令。

## 🔧 其他

- 组件清单中的模型体积探测同样走镜像候选（短超时），避免劫持网络下列清单长时间卡顿；
- 依赖来源说明同步更新（镜像回退语义）。新增环境变量：`SMART_SUMMARIZE_HF_MIRROR`、`SMART_SUMMARIZE_PIP_INDEX_URL`。

**Full Changelog**: https://github.com/Cdexs/smart-summarize/compare/v0.5.2...v0.5.3
