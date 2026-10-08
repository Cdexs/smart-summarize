# -*- coding: utf-8 -*-
"""v0.5.4（D1 修复）测试：_handle_missing_deps 多轮缺失链式处理。

不触网、不真实安装：打桩 _dep_detail / _install_dep / _run_extraction。
运行：py tasks/test_v054_d1.py
"""
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import extract as ex

# —— 打桩：隔离网络与真实安装 ——
ex._dep_detail = lambda k: {"kind": k, "name": k, "purpose": "p", "source": "s", "est_size": "0B"}

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("PASS" if cond else "FAIL"), "-", name, "" if cond else f"| {detail}")


def run_handle(err_kinds, rerun_seq, download=True):
    """err_kinds: 首轮缺失；rerun_seq: 每次 _run_extraction 的行为
    （MissingDependencyError 实例 = 再抛，dict = 返回结果）"""
    installs = []
    ex._install_dep = lambda kind: installs.append(kind) or f"/fake/{kind}"
    seq = list(rerun_seq)

    def fake_rerun(_args):
        nxt = seq.pop(0) if seq else {"success": True}
        if isinstance(nxt, ex.MissingDependencyError):
            raise nxt
        return nxt

    ex._run_extraction = fake_rerun
    args = SimpleNamespace(download_deps=download)
    r = ex._handle_missing_deps(args, ex.MissingDependencyError(err_kinds))
    return installs, r


# 1. 两轮链式（QA D1 原始场景）：pip:requests → whisper-cli + 模型 → 成功
installs, r = run_handle(
    ["pip:requests"],
    [ex.MissingDependencyError(["whisper-cli", "model:large-v3-turbo"]), {"success": True, "content": "ok"}],
)
check("两轮链式-安装顺序完整", installs == ["pip:requests", "whisper-cli", "model:large-v3-turbo"], installs)
check("两轮链式-最终返回成功结果", r.get("success") is True and r.get("content") == "ok", r)

# 2. 停滞检测：装完仍报同一 kind → 结构化错误，不再重复安装
installs, r = run_handle(
    ["whisper-cli"],
    [ex.MissingDependencyError(["whisper-cli"])],
)
check("停滞-只安装一次不重复", installs == ["whisper-cli"], installs)
check("停滞-返回结构化错误", r.get("success") is False and "仍检测缺失" in r.get("error", ""), r)

# 3. 拒绝/非交互（download=False，本进程 stdin 非 tty）→ 不安装，返回缺失清单
installs, r = run_handle(["pip:requests"], [], download=False)
check("拒绝路径-零安装", installs == [], installs)
check("拒绝路径-返回未下载错误", r.get("success") is False and "未下载" in r.get("error", ""), r)
check("拒绝路径-带 missing 清单", isinstance(r.get("missing"), list) and len(r["missing"]) == 1, r)

# 4. 轮次上限：每轮都有新缺失 → 最多 3 轮后结构化报错
installs, r = run_handle(
    ["k1"],
    [ex.MissingDependencyError(["k2"]), ex.MissingDependencyError(["k3"]), ex.MissingDependencyError(["k4"])],
)
check("轮次上限-恰 3 次安装", installs == ["k1", "k2", "k3"], installs)
check("轮次上限-返回上限错误", r.get("success") is False and "3 轮" in r.get("error", ""), r)

# 5. 混合停滞：第二轮含已装 kind + 新 kind → 仅装新 kind；再停滞时报错
installs, r = run_handle(
    ["k1"],
    [ex.MissingDependencyError(["k1", "k2"]), ex.MissingDependencyError(["k1"])],
)
check("混合停滞-仅安装新 kind", installs == ["k1", "k2"], installs)
check("混合停滞-最终结构化错误", r.get("success") is False and "仍检测缺失" in r.get("error", ""), r)

print()
print(f"结果：{len(PASS)} PASS / {len(FAIL)} FAIL")
sys.exit(1 if FAIL else 0)
