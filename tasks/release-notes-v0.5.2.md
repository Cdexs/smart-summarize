# v0.5.2 默认临时目录收敛到技能目录

本版本将技能的默认临时根目录从系统临时目录改为技能目录内的自管 `temp/`，运行中间文件不再散落到系统临时目录。

## 🔧 行为变化

- **默认临时根目录改为技能目录下的 `temp/`**（自动创建，与 SKILL.md、`scripts/` 同级）：YouTube 字幕下载、whisper 转录 WAV/SRT、slice protocol 分片（`ss_slice_<hash>/chunk-NNN.md`）等中间文件统一落在该目录；
- `SMART_SUMMARIZE_TMPDIR` 显式配置优先级不变；
- 技能目录只读不可写时（如受限安装环境）自动回退系统临时目录，不影响使用；
- `ss_*` 目录前缀与 72 小时遗留清扫机制不变。

## 📦 升级说明

- 无破坏性变更：显式设置 `SMART_SUMMARIZE_TMPDIR` 的用户行为完全不变；
- 未设置该变量的用户，中间文件位置从系统临时目录变为 `<技能目录>/temp/`；需要释放空间时可直接删除该目录，下次运行自动重建。

**Full Changelog**: https://github.com/Cdexs/smart-summarize/compare/v0.5.1...v0.5.2
