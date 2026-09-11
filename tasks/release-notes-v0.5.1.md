# v0.5.1 组件安装链路修复与提取质量优化

本版本修复 v0.5.0 中"运行时确认下载"机制在多个常见场景下失效的缺陷，并优化提取质量。建议所有用户升级。

## 🐛 严重修复（功能失效）

- **ffmpeg 自动安装恢复可用**：`_install_dep` 缺失 `ffmpeg` 分支（`install_ffmpeg()` 为不可达死代码），导致缺 ffmpeg 时用户确认安装反而报"未知组件类型： ffmpeg"。现已修复。
- **Windows + NVIDIA 安装崩溃修复**：`WHISPERCPP_CUBLAS_ASSETS` 未定义导致 NameError，N 卡用户的 cublas GPU 版 whisper-cli 自动安装完全失效。已按官方 release 资产名补上 11.8.0 / 12.4.0 双版本按序尝试；同时移除官方已不存在的 `whisper-bin-arm64.zip` 资产（Windows ARM64 走源码构建兜底）。
- **macOS ffmpeg 安装修复**：evermeet.cx 下载 URL 末段无后缀，zip 包被误当 tar 解包必败。已修复包名后缀判定。
- **EPUB 依赖误报修复**：ebooklib 已安装仍每次提示安装（import 名误用组名 `epub`）。已补 import 映射。

## 🔧 提取质量优化

- `SMART_SUMMARIZE_PROXY` 真正生效（此前仅读取不使用，B站请求会忽略该配置）。
- 网页提取标题改用前缀剥离：原 `lstrip` 按字符集剥离会啃坏以 T/i/t/l/e 等字母开头的标题（如 "iTunes…" → "unes…"）；同时清理 Jina 输出的 `URL Source:` / `Markdown Content:` 元信息行。
- **slice protocol 扩展覆盖**：YouTube/B站的超长字幕（`transcript` 键）同样走分片落盘，stdout 只输出清单，不再直灌上下文。
- **YouTube 字幕语言回退**：首选 zh/en 无字幕时自动全量拉取并优选 zh/en，日/韩等其它语言视频可正常提取。
- yt-dlp / pandoc / ffmpeg 子进程显式 UTF-8 解码，修复 Windows 中文 locale 下视频标题与 `.doc` 正文乱码。

## 🧹 其它

- 异常路径临时目录补 `finally` 清理，不再遗留 `ss_yt_*` 目录。
- cookieHint 误报收窄（移除过宽的裸 `"age"` 子串，"message"/"package" 不再误判为登录墙）。
- 组件安装后仍缺失时返回结构化 JSON 错误而非裸 traceback。
- `--output srt` 帮助文案与实际行为对齐（仅音频转录支持）。

## ✅ 验证

- 24 项单元断言覆盖全部修复点全部通过（Python 3.14）。
- CLI 端到端冒烟：小文件直出、425K 字符大文件分片清单（manifest <2KB）、`--slice N` 取片、`--output text`、模拟 300K YouTube 字幕走分片。
- npm 包产物在干净环境安装并冒烟通过。

**Full Changelog**: https://github.com/Cdexs/smart-summarize/compare/v0.5.0...v0.5.1
