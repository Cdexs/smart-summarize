# v0.5.4 缺陷修复记录：QA D1 多轮缺失组件链式安装

- **来源**：QA 执行报告 v0.5.4（缺陷 D1，P1，阻断干净环境首跑）
- **现象**：全新环境 + `--download-deps` 首跑只处理第一轮缺失（如 pip 的 requests），
  第二轮缺失（whisper-cli + 模型）被 `except MissingDependencyError` 吞成
  「组件安装后仍检测缺失」错误并放弃，与 SKILL.md「同意 → 安装 → 自动继续」直接矛盾。
- **根因**：`_run_extraction` 存在两个独立依赖检查点（入口 pip 库预检 / 音视频组件的
  ffmpeg-whisper-模型检查），`_handle_missing_deps` 只处理传入的那一轮 kinds。

## 修复（版本保持 v0.5.4，不另升）

- [x] `_handle_missing_deps` 改为循环：安装本轮 → 重跑 → 若抛出新 `MissingDependencyError`
      则对新的 kinds 继续走同一「列出清单 → 确认 → 安装」流程；
- [x] 交互模式每轮展示新缺失并再次确认（大下载如 1.6GB 模型会被单独看到）；
      `--download-deps`（已获用户同意）连续处理各轮；
- [x] 停滞保护：已尝试安装却仍报告缺失的 kind 立即返回结构化错误（不重复下载、不死循环）；
- [x] 轮次上限 3，超出返回带轮次说明的结构化错误。

## 测试

`tasks/test_v054_d1.py`（打桩，不触网）：11 项断言全 PASS——
两轮链式安装顺序与最终成功返回、停滞只装一次、拒绝路径零安装+missing 清单、
轮次上限恰 3 次安装、混合停滞仅装新 kind。另：`py_compile` 通过；txt 提取冒烟通过。

## 同步

SKILL.md 更新日志（并入 v0.5.4 条目）+ 运行机制流程图；extract.py 头注释（并入 v0.5.4 行）。
package.json 保持 0.5.4。

## Review

修复完成，待 QA 复测 A1（干净环境 `--download-deps` 一次跑通）。
QA 报告其余建议（自托管模型国内镜像、`_http_download` 停滞熔断、C7 文案、C4/C5 真实平台）
未包含在本批次，按用户指示后续另行安排。
