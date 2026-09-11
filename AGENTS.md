# AGENTS.md — smart-summarize

## 项目定位

Agent 技能包（npm: `@cdexs/smart-summarize`）：提取 YouTube/B站字幕、网页正文、本地文件（PDF/Word/Excel/PowerPoint/EPUB/文本）与音视频转录（whisper.cpp）。**只提取，永不调用 LLM**，提取结果交给宿主 agent 总结。

## 代码结构

- `scripts/extract.py` — **全部逻辑都在这一个文件**（约 1400 行），按区块组织：类型检测 → YouTube/B站/网页提取 → 本地文件解析（PDF/Word/EPUB/Excel/PPTX）→ 大文档分片（slice protocol）→ 运行时依赖检测与安装 → whisper.cpp 转录 → CLI main。
- `SKILL.md` — agent 侧使用文档（含 frontmatter 与更新日志），**改代码必须同步更新此文件**，尤其是新参数、新错误字段、行为变化。
- `README.md` / `README.en.md` — 用户文档，中英双份，发布相关改动需两份同步。
- `package.json` — 仅 npm 发布元数据（`files` 白名单），**没有 build/test/lint 脚本，无 node 依赖**。

## 验证方式（无自动化测试）

只能手动验证，用真实输入跑入口脚本并检查 JSON 输出：

```bash
python scripts/extract.py --file <样例.pdf>            # 本地文件
python scripts/extract.py --url "https://www.bilibili.com/video/BVxxxx"  # B站
python scripts/extract.py --file <样例.mp3> --output srt  # 转录（需组件就绪）
```

依赖库（requests/pdfplumber/python-docx/ebooklib/yt-dlp 等）首次使用时脚本会运行时检测并提示确认安装，无需预装。

## 设计硬规则（改代码前必读）

1. **零硬编码路径**：所有组件按「环境变量（`SMART_SUMMARIZE_*`）→ PATH → 受管目录 `~/.smart-summarize`」顺序发现。
2. **组件只经用户确认后才下载**，且只装进 `~/.smart-summarize`，绝不写系统目录；非交互重试用 `--download-deps`（仅代表用户已同意时加）。
3. **永不携带/读取技能目录内的 cookies**；cookies 只从用户手动放置的路径读取（默认 `~/.smart-summarize/cookies/`）。`.gitignore` 已屏蔽 `*.cookies.txt`，勿移除。
4. **失败输出结构化 JSON**（`error` / `missing` / `cookieHint`），不要只靠 stderr 文本。
5. **slice protocol**：提取内容 >256K 字符时全文分片落盘临时目录（`ss_slice_<hash>/chunk-NNN.md`），stdout 只输出 <1KB 清单 JSON，防上下文溢出；`--slice N` 输出单片。≤256K 行为不变（stdout 直出）。
6. **临时目录**：每次运行用 `ss_*` prefix 子目录，正常退出必须清理；遗留目录 72 小时后被清扫。
7. **B站请求默认绕过 Windows 系统代理直连**（系统代理转发国内站会 SSL EOF）；用户显式设 `SMART_SUMMARIZE_PROXY` 或 `HTTPS_PROXY` 时尊重代理。改网络逻辑时勿破坏此行为。
8. **跨平台**：Windows / macOS / Linux / WSL，Python 3.9+；文件路径、子进程调用、编码注意平台差异。

## 约定

- 文档、注释、commit message 均用中文；commit 用 conventional 前缀（`feat:` / `fix:` / `docs:` / `chore:`）。
- 版本号改动需三处同步：`package.json` 的 `version`、`SKILL.md` 更新日志新增条目、（如涉及用户可见行为）README 两份。
- npm `files` 白名单决定发布内容，新增源文件需加入该列表。
