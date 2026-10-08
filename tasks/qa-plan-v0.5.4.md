# QA 测试计划 — smart-summarize v0.5.4

- **被测版本**：0.5.4（commit `1192bad`，本计划随后入库）
- **本轮主题**：①组件下载改为技能仓库自托管优先（GitHub Release `components-v1` 资产）；②复测上一轮转交的 3 个下载缺陷的修复（v0.5.3）
- **安装方式（任选）**：
  - git：`git clone` 仓库并 checkout `1192bad`，直接用 `scripts/extract.py`；
  - skills CLI：已装环境执行 `npx skills update`（当前安装副本是 v0.5.2，需更新）；
  - npm：0.5.4 尚未 publish，发布后可用 `npm install -g @cdexs/smart-summarize`。
- **冒烟基线（开发自测已过）**：干净环境提取本地 txt 成功；自托管源实测下载 whisper zip 与模型均成功
- **回归范围**：v0.5.3 修复项（whisper.cpp 资产 404 / HF 镜像回退 / pip 镜像回退）、v0.5.2（临时目录）、slice protocol、既有全部提取功能

## 环境准备

| 项 | 要求 |
| --- | --- |
| Python | 3.9+（建议 3.10–3.14 各跑一轮核心用例） |
| 平台矩阵 | **Windows x64（重点**——自托管 whisper 资产即 Windows x64 构建）/ macOS / Linux |
| 干净度 | 测试前清空 `~/.smart-summarize`（或用空 `SMART_SUMMARIZE_HOME`）与 `SMART_SUMMARIZE_*` 环境变量；全新环境不要预装相关 pip 库，以验证确认安装链路 |
| 网络模拟（hosts 修改，测试后恢复） | **场景 B**：huggingface.co → 0.0.0.0（模拟 DNS 劫持）；**场景 C**：github.com / api.github.com / objects.githubusercontent.com → 0.0.0.0 |
| 可选 | NVIDIA 机器（cublas 路径回归）、无 Vulkan 的 Windows 机器（验证回退 CPU） |

> 已知环境事实（本机 QA 可直接利用）：huggingface.co 被 DNS 劫持、hf-mirror.com 可用、pip 默认源极慢——B2 用例在本机无需 hosts 即为真。

## 用例

### A. v0.5.4 自托管源（本轮核心，Windows x64）

| # | 用例 | 步骤 | 预期 |
| --- | --- | --- | --- |
| A1 | 自托管 whisper 安装 | 清空受管目录，正常网络跑 `--file <音频>` 触发缺组件确认（agent 代为确认用 `--download-deps`） | 从 `components-v1` 下载 `whisper-bin-x64.zip`（7.5MB）并自动解压落位；stderr 出现「已安装技能仓库自托管构建（Vulkan + CPU 通用）」；随后自动继续转录成功 |
| A2 | 自托管模型优先 | 同一流程的模型下载 | `ggml-large-v3-turbo.bin` 首选来自 `components-v1`（stderr/下载日志可见）；若发生回退，stderr 须标注实际来源 |
| A3 | 校验和一致 | 下载后比对三个 sha256 | zip / zip 内 whisper-cli.exe / 模型，均与仓库 `models/README.md` 清单一致（`c1fbbeb7…` / `8e725caa…` / `1fc70f77…`） |
| A4 | q5_0 档位跳过自托管 | `--model large-v3-turbo-q5_0` 触发模型下载 | 候选链不含自托管（未托管档位），直接走 HF/镜像，无多余请求 |
| A5 | 场景 C：GitHub 全不可达 | hosts 屏蔽后重跑 A1 | 不再出现晦涩报错：每个来源的失败在 stderr 有摘要，最终给结构化错误或明确指引，不崩溃；模型部分仍经 HF/镜像成功（若 HF 同时不可达则 hf-mirror 成功） |
| A6 | 安装副本的 GPU 自证 | A1 完成后看转录 stderr | 有 Vulkan 设备显示 `🎮 Vulkan: <设备名>`；无则 `🖥 CPU`（自托管构建含两后端，均属正常） |

### B. v0.5.3 修复复测（上一轮转交缺陷的回归）

| # | 用例 | 步骤 | 预期 |
| --- | --- | --- | --- |
| B1 | whisper.cpp 资产 404 不再发生 | 正常网络触发 whisper 安装；观察下载 URL | 首选自托管；自托管失败时依次回退 GitHub API 解析的提交构建（b5454/b5130 等）→ latest → v1.9.2。**不得**再出现对 `latest/download` 的 404 死路 |
| B2 | HF DNS 劫持自动回退 | 清空模型目录后触发下载（本机天然满足劫持场景） | 自动切换 hf-mirror.com 完成下载，stderr 出现「已改用备用来源」类标注；模型体积正确（约 1.62GB） |
| B3 | pip 镜像回退 | 干净 venv（无库）+ 屏蔽 pypi.org 与 files.pythonhosted.org，触发任一 pip 组（如 PDF）安装 | 自动切换清华 TUNA（失败则腾讯云）完成安装，stderr 标注实际来源；全部失败时给出手动命令与 env 用法 |
| B4 | HF 镜像环境变量 | 设 `SMART_SUMMARIZE_HF_MIRROR`（或 `HF_ENDPOINT`）后触发模型下载 | 指定源优先使用 |
| B5 | pip 索引环境变量 | 设 `SMART_SUMMARIZE_PIP_INDEX_URL` 后触发 pip 安装 | 指定源优先使用 |

### C. 行为与回归

| # | 用例 | 预期 |
| --- | --- | --- |
| C1 | 组件清单体积显示 | 缺模型时的清单中 `est_size` 为 1.5GB 量级，不得出现 29B 之类异常值（`_content_length` 状态码修复回归） |
| C2 | 临时目录回归 | 中间文件在 `<技能目录>/temp/`（`ss_*` 前缀），正常退出清理；`SMART_SUMMARIZE_TMPDIR` 覆盖仍优先 |
| C3 | slice protocol 回归 | >256K 文档输出 <2KB 分片清单 + `--slice N` 单片正常 + 校验和一致 |
| C4 | macOS 回归 | 不下载自托管 Windows 包；有 brew 走 brew（Metal）；无 brew 给出源码构建路径 |
| C5 | Linux 回归 | 同上不触碰自托管 whisper 资产；既有 whisper-cli/源码构建路径行为不变 |
| C6 | 常规提取抽测 | txt / PDF / B站 CC 字幕 / 网页 各一，success 且内容正常 |
| C7 | 结构化错误 | 制造失败场景（如 B站无字幕视频），JSON 含 `error`/`success:false`，不崩溃 |

## 通过标准

A 组全过（Windows x64 必测）；B 组全过（v0.5.3 修复为本轮重点回归）；C 组无既有功能回归。hosts 模拟用例结束后恢复系统网络配置。发现缺陷记录到 `tasks/` 并回传开发（附 `error` JSON 与 stderr 关键日志）。
