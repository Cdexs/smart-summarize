# v0.5.4 组件自托管下载源

用户需求：把本机在用的转录组件（whisper-cli Vulkan 构建 + large-v3-turbo 模型）托管到仓库侧，脚本改从本仓库下载，避免外部源变动导致下载失败。

## 方案与约束

- GitHub git 仓库单文件硬限 100MB（模型 1.6GB 无法入库），采用 **GitHub Release 资产通道**（单文件上限 2GB，无带宽配额）：
  tag `components-v1`（指向 v0.5.3 发布 commit，`--latest=false` 不抢占 Latest），资产 2 个；
- 仓库 `models/` 子目录存放资产清单（`models/README.md`：SHA256、来源、许可、更新指引）。

## 改动

- [x] 资产上传：`whisper-bin-x64.zip`（whisper-cli Vulkan+CPU 静态构建，7.5MB，zip 内 exe 与本地 sha256 一致）+ `ggml-large-v3-turbo.bin`（1,624,555,275B，与本地转录用文件一致）；下载通道实测 206；
- [x] extract.py 新增 `SELF_HOSTED_*` 常量与候选链改造：whisper 资产候选 = **自托管**（win-x64 zip）→ API 解析 → latest → v1.9.2 兜底；cublas 不自托管维持 API 优先；模型候选顺序见下方「调整」（最终为官方优先）；
- [x] 自托管 Vulkan 构建安装后 stderr 标注 GPU 语义（不再误报「已安装 CPU 版」）；
- [x] 修复 `_content_length` 将 404 响应误当资产大小（状态码 ≥400 归零）；`_dep_detail` 模型体积补回 KNOWN_MODEL_SIZES 兜底。

## 版本同步

- [x] package.json → 0.5.4；SKILL.md 更新日志与下载来源说明；extract.py 头注释；README 两份无需改（来源表述为通用措辞）

## 验证（2026-10-08，本机 Windows）

- 编译通过；单测：模型/资产候选链顺序、env 置顶、q5_0 跳过自托管、cublas 维持 API 优先，均符合预期；
- 真实下载自托管 whisper zip：zip 内 whisper-cli.exe sha256 与本地逐字节一致（`8e725caa…`）；
- 自托管模型 URL 实测：资产 1,624,555,275 字节（与本地一致）、范围 GET 206；`_dep_detail` 体积探测返回 1.5 GB（自托管源命中，探测 bug 修复前曾误报 29B）；
- 上游回退链完整保留：b5454/b5130（API 解析）、latest、v1.9.2 兜底未删除。

## Review

完成。注意：`whisper-bin-x64.zip` 与官方同名资产语义不同（本仓库版为 Vulkan+CPU 通用构建），安装逻辑兼容（zip 内 whisper-cli.exe 由 rglob 定位）；更新组件时开 `components-v2` 并同步 `SELF_HOSTED_COMPONENTS_TAG`。

## 调整（2026-10-08，QA 反馈：GitHub 下载慢）

QA 实测 GitHub 资产 CDN 在受限网络带宽差（约 54KB/s，1.6GB 模型约 8.5 小时）。据此调整：

- [x] **模型候选链改为官方优先**：显式镜像 → huggingface.co → hf-mirror.com → **自托管兜底**
      （原先自托管置前会让模型走慢速 GitHub 通道；官方/镜像 3.25MB/s 级别）；
- [x] **whisper 资产维持自托管优先**：与官方同走 GitHub 资产 CDN，速度一致；自托管版为
      Vulkan 构建（AMD/Intel 开箱 GPU）且资产稳定（规避上游 latest 资产为空问题）；
- [x] 文档同步：SKILL.md（更新日志 + 来源说明）、`models/README.md`、extract.py 注释与头注释。
- 验证：候选链单测（顺序/env 置顶/q5_0 无自托管）+ 降级模拟（首源失败 → 后源成功标注）+ 编译。
