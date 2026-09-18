#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""extend-slides 环境能力探测。

用法：
    python scripts/probe_env.py            # 人类可读表格
    python scripts/probe_env.py --json     # 机器可读 JSON

退出码始终为 0：能力缺失不是错误，只是需要走降级路径。
"""

from __future__ import annotations

import importlib.util
import json
import platform
import shutil
import subprocess
import sys


def _first_line(text: str) -> str:
    for line in (text or "").splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def _run(cmd: list[str], timeout: int = 20) -> tuple[bool, str]:
    """执行外部命令，返回 (是否可用, 说明)。"""
    if shutil.which(cmd[0]) is None:
        return False, "未在 PATH 中找到"
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.TimeoutExpired:
        return False, f"执行超时（>{timeout}s）"
    except OSError as exc:
        return False, f"执行失败：{exc}"
    if proc.returncode != 0:
        detail = _first_line(proc.stderr) or _first_line(proc.stdout)
        return False, f"退出码 {proc.returncode}：{detail or '无输出'}"
    return True, _first_line(proc.stdout) or _first_line(proc.stderr) or "可用"


def _check_python_module(module: str) -> tuple[bool, str]:
    spec = importlib.util.find_spec(module)
    if spec is None:
        return False, "未安装"
    try:
        mod = __import__(module)
        version = getattr(mod, "__version__", "")
    except Exception as exc:  # noqa: BLE001 - 探测脚本需要容忍任意导入错误
        return False, f"导入失败：{exc}"
    return True, f"已安装 {version}".strip()


def probe() -> list[dict]:
    checks: list[dict] = []

    ok, detail = _check_python_module("pptx")
    checks.append(
        {
            "capability": "python-pptx",
            "available": ok,
            "detail": detail,
            "provides": "直接抽取 PPTX 每页文字、备注与图片",
            "fallback": "请用户在 PowerPoint 中「文件 → 导出 → 创建 PDF」，或逐页截图",
        }
    )

    ok, detail = _check_python_module("pymupdf")
    if not ok:
        # 旧版 PyMuPDF 只有 fitz 这个导入名
        ok, detail = _check_python_module("fitz")
    checks.append(
        {
            "capability": "PyMuPDF",
            "available": ok,
            "detail": detail,
            "provides": "PDF 逐页转图片的备用方案（无需 poppler）",
            "fallback": "安装：pip install pymupdf；或改用 poppler",
        }
    )

    for command, args, capability, provides, fallback in (
        (
            "soffice",
            ["--version"],
            "LibreOffice",
            "把 PPT / Word 转成 PDF",
            "请用户用 Office 手动另存为 PDF",
        ),
        (
            "pdftoppm",
            ["-v"],
            "poppler",
            "PDF 逐页转图片",
            "安装 poppler 并加入 PATH；或 pip install pymupdf",
        ),
        (
            "tesseract",
            ["--version"],
            "OCR",
            "扫描件文字识别（仅在多模态直读不可靠时使用）",
            "改用多模态直读图片；无法辨识处如实标注「无法辨识」",
        ),
    ):
        ok, detail = _run([command, *args])
        checks.append(
            {
                "capability": capability,
                "available": ok,
                "detail": detail,
                "provides": provides,
                "fallback": fallback,
            }
        )

    return checks


def _print_table(checks: list[dict]) -> None:
    print("extend-slides 环境能力探测")
    print("=" * 72)
    print(f"Python {platform.python_version()}  |  {platform.system()} {platform.release()}")
    print("-" * 72)
    for item in checks:
        mark = "[可用]" if item["available"] else "[缺失]"
        print(f"{mark} {item['capability']}: {item['detail']}")
        if not item["available"]:
            print(f"        降级路径：{item['fallback']}")
    print("-" * 72)

    available = [c["capability"] for c in checks if c["available"]]
    missing = [c["capability"] for c in checks if not c["available"]]
    print(f"可用能力：{'、'.join(available) if available else '无'}")
    print(f"缺失能力：{'、'.join(missing) if missing else '无'}")
    if missing:
        print()
        print("提示：缺失能力不阻断流程，按上表的降级路径请用户人工导出即可。")


def main(argv: list[str]) -> int:
    checks = probe()
    if "--json" in argv:
        print(json.dumps(checks, ensure_ascii=False, indent=2))
    else:
        _print_table(checks)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
