# v0.5.3 组件下载链路网络适配

基于其他 agent 首次安装组件依赖时反馈的三个环境级障碍，目标版本 v0.5.3。

## 缺陷与修复

- [x] P1 whisper.cpp 预编译资产 404：`releases/latest/download/<asset>` 依赖 latest release 携带资产，
      而上游 v1.9.3/v1.9.4/v1.9.5 的版本号 release 资产为空（预编译资产改挂在 commit 构建 release 上），
      自动安装 whisper-cli 必然 404 → 新增 `_whispercpp_asset_urls()`：
      ①GitHub API 定位最新含目标资产的 release（CPU 版解析到 b5454、cublas 版解析到 b5130，自适应未来变化）；
      ②latest/download 兜底（若 latest 恢复携带资产）；③固定版本 v1.9.2 兜底（API 不可用/被限流时）。
      `install_whispercli` 预编译下载循环改为逐候选源尝试。
- [x] P1 ggml 模型下载不可达：huggingface.co 在部分网络被 DNS 劫持（解析到 Meta IP 段）→ 新增
      `_model_url_candidates()`：`SMART_SUMMARIZE_HF_MIRROR`（兼容 huggingface_hub 惯例的 `HF_ENDPOINT`）
      → huggingface.co → 公共镜像 hf-mirror.com 自动回退；`install_model` 逐源尝试、失败清理 .part、
      stderr 标注实际来源；全部失败时返回明确错误（含 DNS 劫持提示与环境变量用法）。
- [x] P1 pip 无镜像回退：默认源（PyPI）在部分网络极慢（simple 索引实测 15s）甚至报
      "No matching distribution found"，换国内镜像后即成功 → 新增 `_pip_index_urls()` /
      `_pip_install_cmd()`：`SMART_SUMMARIZE_PIP_INDEX_URL` 显式指定 → 默认源 → 清华 TUNA → 腾讯云；
      `_install_dep` pip 分支逐源尝试、stderr 标注实际来源与失败摘要，全部失败给出手动命令与 env 用法。
- [x] P3 `_dep_detail` 模型体积探测改走镜像候选（timeout=10，避免劫持网络下列清单卡 30 秒）；
      pip 来源说明同步补充镜像回退语义。

## 版本同步

- [x] package.json → 0.5.3
- [x] SKILL.md 更新日志新增 v0.5.3；ggml/whisper-cli 下载来源说明、"安装依赖"补 pip 镜像语义、故障排除表补充
- [x] README.md / README.en.md 环境变量表新增 `SMART_SUMMARIZE_HF_MIRROR`、`SMART_SUMMARIZE_PIP_INDEX_URL`
- [x] extract.py 头注释补 v0.5.3 变更行

## 验证（2026-10-07，本机 Windows）

- 静态：`py -m py_compile scripts/extract.py` 通过（Python 3.14）。
- 复证缺陷：`latest/download/whisper-bin-x64.zip` → HTTP 404；huggingface.co 解析到 31.13.96.194（Meta 段），
  hf-mirror.com 正常解析。
- API 解析实测：`_whispercpp_asset_urls('whisper-bin-x64.zip')` 首选 b5454；
  `('whisper-cublas-11.8.0-bin-x64.zip')` 首选 b5130；均含 3 个候选。
- 端到端：用修复链路真实下载 b5454 的 whisper-bin-x64.zip（8.5MB），zip 有效（41 条目）且含
  `Release/whisper-cli.exe`；hf-mirror.com 模型 HEAD 返回 574,041,195 字节（与 q5_0 已知体积一致）。
- 候选顺序：`_model_url_candidates` 官方 → 镜像；设 `SMART_SUMMARIZE_HF_MIRROR` 或 `HF_ENDPOINT` 后自定义源优先。
- pip：`_pip_index_urls` 默认顺序为 默认源 → 清华 → 腾讯，env 置顶；`_pip_install_cmd` 仅在非默认源时加
  `--index-url`；腾讯镜像 `pip install --dry-run requests` 实测解析成功。

## Review

**全部完成，验证通过。** 注意：上游若恢复在版本号 release 携带资产，API 解析会自动跟随，无需改代码；
`WHISPERCPP_PINNED_RELEASE`（v1.9.2）仅在 GitHub API 整体不可用时兜底，若未来该版本资产被上游删除需手动更新此常量。

