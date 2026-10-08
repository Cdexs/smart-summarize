# models/ — 自托管组件清单

本目录登记 smart-summarize 技能运行所需的**自托管组件**。

受 git 仓库单文件 100MB 硬限制，大文件不直接入库；实际文件托管在本仓库的 **GitHub Release 资产通道**（单文件上限 2GB），由技能脚本自动下载：

- 发布页：https://github.com/Cdexs/smart-summarize/releases/tag/components-v1
- 下载 URL 模式：`https://github.com/Cdexs/smart-summarize/releases/download/components-v1/<文件名>`

技能的下载候选链以**自托管源为第一来源**，官方源与镜像保留为回退（见 `scripts/extract.py` 中 `SELF_HOSTED_*` 常量）——外部源的资产变动（如上游 release 改挂 commit 构建）不再直接导致下载失败。

## 资产清单（components-v1）

| 文件 | 说明 | 大小 | SHA256 |
| --- | --- | --- | --- |
| `whisper-bin-x64.zip` | whisper-cli（Windows x64，Vulkan + CPU 后端；静态构建，无 DLL 依赖） | 7.5 MB | zip：`c1fbbeb7c027278b70501ce8edcf7e96ade39a211999d5a44f0e13d013c28dd6`；内含 whisper-cli.exe：`8e725caaa3975ee91e7eb8470db9b378ca955c58ae4738bb4932ea396ed962d3` |
| `ggml-large-v3-turbo.bin` | Whisper large-v3-turbo ggml 模型 | ~1.62 GB | `1fc70f774d38eb169993ac391eea357ef47c88757ef72ee5943879b7e8e2bc69` |

## 来源与许可

- **whisper.cpp**（MIT License）：https://github.com/ggml-org/whisper.cpp —— 本 zip 为其源码构建产物（Vulkan + CPU 后端，2026-09-01 构建；AMD/Intel GPU 经 Vulkan 加速，无 Vulkan 环境自动回退 CPU）；
- **模型**为 openai/whisper-large-v3-turbo 权重的 ggml 转换版（OpenAI Whisper 权重与转换脚本均为 MIT License）；转换来源 https://huggingface.co/ggerganov/whisper.cpp ；
- 更新组件时开新 tag（`components-v2` …）并同步 `scripts/extract.py` 的 `SELF_HOSTED_COMPONENTS_TAG`；下载后请核对上表 SHA256。
