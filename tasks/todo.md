# v0.5.1 Bug 修复与优化

基于 2026-09-11 代码审查结论，目标版本 v0.5.1。

## 修复项

- [ ] P1 `_install_dep` 缺 `ffmpeg` 分支，`install_ffmpeg()` 为不可达死代码 → 自动装 ffmpeg 必报"未知组件类型"
- [ ] P1 `WHISPERCPP_CUBLAS_ASSETS` 未定义（Windows+NVIDIA NameError）→ 按官方资产名补定义；顺带移除不存在的 `whisper-bin-arm64.zip` 资产
- [ ] P1 macOS ffmpeg 下载文件名丢失 `.zip` 后缀（evermeet.cx URL 末段为 "zip"）→ 被当 tar 解包必败
- [ ] P1 `PIP_LIB_GROUPS["epub"]` 缺 `"import": "ebooklib"` → 已装也永远误报缺失
- [ ] P2 `SMART_SUMMARIZE_PROXY` 从未传入 requests → 实现之
- [ ] P2 `extract_web` 标题 `lstrip('Title: ')` 按字符集剥离啃坏标题 → 改前缀剥离
- [ ] P2 slice protocol 不覆盖 YouTube/B站 `transcript` 键 → main 中补齐
- [ ] P2 yt-dlp/pandoc/ffmpeg 子进程未指定 utf-8 → Windows 中文 locale 乱码
- [ ] P2 YouTube 字幕语言白名单过窄 → 首选 zh/en 失败后回退全量拉取并优选 zh/en
- [ ] P3 `write_slices` manifest 文件句柄未关闭
- [ ] P3 `extract_youtube` 异常路径不清理 tmpdir（补 finally）
- [ ] P3 cookieHint 判定子串 "age" 过宽（message/package 误命中）
- [ ] P3 `--output srt` help 文案与实际不符（视频不产 SRT）
- [ ] P3 `make_chunks` cur_len 计数与 add 判定不一致
- [ ] P3 `_handle_missing_deps` 安装后重跑若仍缺组件会抛未捕获异常 → 兜底结构化错误

## 版本同步

- [ ] package.json → 0.5.1
- [ ] SKILL.md 更新日志新增 v0.5.1
- [ ] extract.py 头注释补 v0.5.1 变更行

## 验证

- [ ] python 编译检查 + 纯函数单测（分片/检测/cookies 解析/字幕清洗）
- [ ] 端到端冒烟：本地 txt 提取

## Review

**全部完成，验证通过。**

- 静态：`py -m py_compile scripts/extract.py` 通过（Python 3.14）。
- 单测：`tasks/test_v051.py` 24 项断言全部 PASS，覆盖全部修复点（ffmpeg 安装路由、cublas 资产、macOS 包名、epub 检测、PROXY 生效、标题剥离、cookieHint 收窄、分片重叠/覆盖/无损、cookies 解析、类型检测）。
- 端到端：CLI 实测小文件 JSON 直出；425K 字符大文件输出 11 片清单（manifest 仅 1.5KB）且 chunk_dir 落盘；`--slice 3` 正确返回单片；`--output text` 正常；monkeypatch 模拟 300K YouTube transcript 确认走分片（8 片清单）。
- 测试脚本自身曾有一处断言错误（6000 字符切 8 片却断言 >10 片），已修正——非产品代码问题。

版本同步：package.json 0.5.1、SKILL.md 更新日志、extract.py 头注释，三处一致。
