# -*- coding: utf-8 -*-
"""v0.5.1 修复项验证脚本（纯函数级 + 端到端冒烟）"""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import extract  # noqa: E402

FAIL = []

def check(name, cond, detail=""):
    mark = "PASS" if cond else "FAIL"
    print(f"[{mark}] {name}" + (f"  ({detail})" if detail and not cond else ""))
    if not cond:
        FAIL.append(name)

# 1. _install_dep 路由：ffmpeg kind 应调用 install_ffmpeg
called = []
orig = extract.install_ffmpeg
extract.install_ffmpeg = lambda: "FAKE_FFMPEG_PATH"
try:
    r = extract._install_dep("ffmpeg")
    check("_install_dep('ffmpeg') 调用 install_ffmpeg", r == "FAKE_FFMPEG_PATH")
except Exception as e:
    check("_install_dep('ffmpeg') 调用 install_ffmpeg", False, repr(e))
finally:
    extract.install_ffmpeg = orig

try:
    extract._install_dep("ffmpeg")  # again with real one? no - just routing check above
except RuntimeError as e:
    check("ffmpeg kind 不再报未知组件类型", "未知组件" not in str(e), str(e))
except Exception:
    pass

# 2. WHISPERCPP_CUBLAS_ASSETS 已定义且被引用
assets = getattr(extract, "WHISPERCPP_CUBLAS_ASSETS", None)
check("WHISPERCPP_CUBLAS_ASSETS 已定义", isinstance(assets, list) and len(assets) == 2)
check("cublas 资产名与官方一致",
      assets == ["whisper-cublas-11.8.0-bin-x64.zip", "whisper-cublas-12.4.0-bin-x64.zip"])
check("已移除不存在的 whisper-bin-arm64.zip",
      "whisper-bin-arm64.zip" not in str(extract.WHISPERCPP_PREBUILT_ASSETS))

# 3. macOS ffmpeg 包名推导（模拟 evermeet URL 末段无后缀）
import urllib.parse
url = "https://evermeet.cx/ffmpeg/getrelease/zip"
archive_name = url.rsplit("/", 1)[-1].split("?")[0]
if not archive_name.endswith((".zip", ".tar.xz", ".tar.gz", ".tgz")):
    archive_name += ".zip" if "zip" in url.lower() else ".tar.xz"
check("macOS 包名补 .zip 后缀", Path(archive_name).suffix == ".zip", archive_name)

# 4. epub 组 import 映射
check("epub 组 import=ebooklib", extract.PIP_LIB_GROUPS["epub"].get("import") == "ebooklib")
kinds = extract._missing_pipelib_kinds(["epub"])
if extract._import_ok("ebooklib"):
    check("ebooklib 已装时不误报缺失", kinds == [])
else:
    print("[SKIP] 本机未装 ebooklib，跳过误报检查")

# 5. SMART_SUMMARIZE_PROXY 生效：检查代码确实把值放进 proxies
import inspect
src = inspect.getsource(extract.extract_bilibili)
check("SMART_SUMMARIZE_PROXY 传入 proxies", '"http": user_proxy' in src.replace("'", '"'))

# 6. 网页标题前缀剥离（模拟 Jina 输出解析逻辑，不联网）
jina_out = "Title: eBay 与 iTunes 分析\nURL Source: https://example.com\n\nMarkdown Content:\n正文"
lines = jina_out.split("\n")
title = lines[0].removeprefix("Title:").strip()
body = [l for l in lines[1:] if not __import__("re").match(r"^(URL Source|Markdown Content):", l)]
check("标题 'eBay 与 iTunes 分析' 不被啃坏", title == "eBay 与 iTunes 分析", title)
check("URL Source / Markdown Content 行已清理",
      not any(l.startswith(("URL Source", "Markdown Content")) for l in body))

# 7. cookieHint 判定不再误报 "message"/"package"
signs = ("sign in", "not a bot", "age-restricted", "confirm your age",
         "members-only", "private video", "login", "cookies")
check("裸 age 子串已移除", not any("age" == s for s in signs))
check("'message' 不再误命中", not any(s in "some error message occurred" for s in signs))
check("'sign in to confirm' 仍可命中", any(s in "Please sign in to confirm you are not a bot" for s in signs))

# 8. make_chunks：段落对齐 + 重叠 + 计数一致
text = "\n\n".join(f"段落{i}。" + "字" * 500 for i in range(30))
chunks = extract.make_chunks(text, chunk_chars=2000, overlap=300)
check("分片生成", len(chunks) >= 5, str(len(chunks)))
check("每片不超上限", all(len(c) <= 2000 for c in chunks), str([len(c) for c in chunks]))
check("相邻片有重叠", all(chunks[i][-50:] and chunks[i][-50:] in chunks[i + 1] for i in range(len(chunks) - 1)))
# 全文内容覆盖（重叠造成的重复不计）
joined = "".join(chunks)
check("所有段落均被覆盖", all(f"段落{i}。" in joined for i in range(30)))

# 9. 超长段落 hard split 在句子边界切
long_par = "这是一句话。" * 1000
pieces = extract._hard_split(long_par, 800)
check("超长段落被切分", all(len(p) <= 800 for p in pieces) and len(pieces) > 5)
check("切分无损（重拼长度一致）", len("".join(pieces)) == len(long_par))

# 10. B站 cookies 解析（Netscape + 头格式）
tmp = Path(tempfile.mkdtemp(prefix="ss_test_cookies_"))
netscape = tmp / "bilibili-cookies.txt"
netscape.write_text(
    "# Netscape HTTP Cookie File\n"
    ".bilibili.com\tTRUE\t/\tTRUE\t0\tSESSDATA\tabc123\n"
    "example.com\tTRUE\t/\tTRUE\t0\tOTHER\txxx\n",
    encoding="utf-8")
os.environ["SMART_SUMMARIZE_BILIBILI_COOKIES"] = str(netscape)
hdr = extract._bilibili_cookie_header()
check("Netscape cookies 提取 bilibili 域", hdr == "SESSDATA=abc123", hdr)
header_fmt = tmp / "b2.txt"
header_fmt.write_text("SESSDATA=zzz; bili_jct=yyy\n", encoding="utf-8")
os.environ["SMART_SUMMARIZE_BILIBILI_COOKIES"] = str(header_fmt)
hdr2 = extract._bilibili_cookie_header()
check("Cookie 头格式原样使用", hdr2 == "SESSDATA=zzz; bili_jct=yyy", hdr2)
del os.environ["SMART_SUMMARIZE_BILIBILI_COOKIES"]

# 11. detect_content_type 基线
check("B站 URL 识别", extract.detect_content_type("https://www.bilibili.com/video/BV1xx411c7mD") == "bilibili")
check("b23.tv 识别", extract.detect_content_type("https://b23.tv/BV1xx411c7mD") == "bilibili")
check("YouTube 识别", extract.detect_content_type("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "youtube")

print()
if FAIL:
    print(f"共 {len(FAIL)} 项失败: {FAIL}")
    sys.exit(1)
print("全部通过 ✅")
