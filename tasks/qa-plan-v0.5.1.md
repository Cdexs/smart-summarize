# QA 测试计划 — smart-summarize v0.5.1

- **被测版本**：0.5.1（commit `4977f15`）
- **测试产物**：`dist/cdexs-smart-summarize-0.5.1.tgz`（npm 安装包，sha512 见 `npm show`/pack 输出）
- **安装方式**：`npm install <tgz 路径>`，然后 `py node_modules/@cdexs/smart-summarize/scripts/extract.py ...`；或直接用仓库 `scripts/extract.py`
- **冒烟基线（已由开发自测通过）**：干净目录安装 tgz → 提取本地 txt 成功
- **回归范围**：v0.5.0 已有功能不回归（PDF/Word/EPUB/Excel/PPTX/音视频/B站/网页/分片协议）

## 环境准备

| 项 | 要求 |
| --- | --- |
| Python | 3.9+（建议 3.10–3.14 各跑一轮核心用例） |
| 平台矩阵 | Windows（重点）/ macOS（重点，验证 #3 修复）/ Linux |
| 可选 | node（YouTube 字幕）、pandoc（.doc）、NVIDIA GPU 机器一台（验证 #2） |
| 注意 | 本机 `python` 是 Windows Store 占位符时用 `py`；全新环境不要预装任何 pip 库，以验证运行时确认安装链路 |

## 用例

### A. P1 修复项（本轮必测）

| # | 用例 | 步骤 | 预期 |
| --- | --- | --- | --- |
| A1 | ffmpeg 自动安装（#1） | 干净环境（无 ffmpeg、无 `SMART_SUMMARIZE_FFMPEG`）跑 `--file <任意音频>`，确认清单后同意 | 安装成功且自动继续转录，stderr 出现 `✅ 已安装 ffmpeg`；**不得**出现"未知组件类型: ffmpeg" |
| A2 | NVIDIA cublas 安装（#2） | Windows + NVIDIA 机器，删除 `~/.smart-summarize/bin/whisper-cli.exe` 后触发转录确认安装 | 下载 `whisper-cublas-11.8.0-bin-x64.zip`（失败自动试 12.4.0），DLL 随装，转录走 GPU；不得出现 NameError/安装失败 |
| A3 | Windows ARM64 兜底 | Windows ARM64（如有）：删除受管二进制触发安装 | cublas/x64 均失败后给出明确指引，进入源码构建或报告缺失，无崩溃 |
| A4 | macOS ffmpeg 安装（#3） | macOS 无 ffmpeg 环境触发安装 | zip 正确解包（不再报 tarfile.ReadError），`~/.smart-summarize/bin/ffmpeg` 可执行 |
| A5 | EPUB 不再误报（#4） | 已 `pip install ebooklib` 的环境提取 `.epub` | 不出现缺失组件提示，直接提取；未装 ebooklib 时提示一次、确认安装后同一会话不再重复提示 |

### B. P2 修复项

| # | 用例 | 步骤 | 预期 |
| --- | --- | --- | --- |
| B1 | SMART_SUMMARIZE_PROXY（#5） | 设置 `SMART_SUMMARIZE_PROXY=http://127.0.0.1:<可用代理>` 提取 B站 | 请求经该代理（代理侧可见连接）；不设时 Windows 系统代理仍被绕过（v0.4.1 行为回归） |
| B2 | 网页标题（#6） | 提取标题以大写 T/i/e 开头的网页（或含 "iTunes"/"eBay" 字样的标题） | 标题完整无缺字；content 无 `URL Source:` / `Markdown Content:` 行 |
| B3 | YouTube 长字幕分片（#7） | 提取一个字幕超 256K 字符的长视频 | stdout 是 slices 清单 JSON（<2KB）而非全文字幕；`--slice N` 可逐片取回 |
| B4 | Windows 中文乱码（#8） | zh-CN Windows：提取中文标题 YouTube 视频元数据；提取中文 `.doc`（pandoc） | 标题/正文无乱码 |
| B5 | 字幕语言回退（#9） | 提取一个仅有日文（无 zh/en）字幕的视频 | 回退后拿到日文字幕；zh/en 都存在的视频仍优先取 zh/en |

### C. 回归（抽测）

| # | 用例 | 预期 |
| --- | --- | --- |
| C1 | 本地 txt / md 提取 | JSON success，中文正常 |
| C2 | PDF / docx / xlsx / pptx / epub 各一 | 首次使用提示装库→确认→提取成功 |
| C3 | B站 CC 字幕（免登录） | success 与 v0.5.0 一致 |
| C4 | ≤256K 与 >256K 文档 | 前者 stdout 直出；后者 11 类分片清单 + `--slice N` + 校验和一致 |
| C5 | `--output text/srt` | text 正常；srt 仅音频可出字幕 |
| C6 | `--no-gpu` | 强制 CPU 转录 |
| C7 | 缺组件且非交互 | 返回含 `missing` 清单的 JSON，不静默下载 |
| C8 | cookies 隐私 | 技能目录不放 cookies；`~/.smart-summarize/cookies/*.txt` 仅用户手动放置后生效 |

## 通过标准

A 组全过；B 组除依赖外部账号态的条目外全过；C 组无 v0.5.0 功能回归。发现缺陷记录到 `tasks/` 下并回传开发。
