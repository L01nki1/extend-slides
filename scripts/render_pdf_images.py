#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 PDF 逐页渲染成图片，供 extend-slides 处理扫描版 PDF。

用法：
    python scripts/render_pdf_images.py <input.pdf> <课程输出目录> [--dpi 150]

产出：
    <课程输出目录>/assets/<页号>.png

实现顺序：
    1. poppler 的 pdftoppm（外部命令）
    2. PyMuPDF / fitz（Python 库）
两者都不可用时，给出人工导出指引并以非零码退出。
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_DPI = 150


def render_with_pdftoppm(pdf: Path, assets: Path, dpi: int) -> int | None:
    """用 pdftoppm 渲染，成功返回页数，不可用返回 None。"""
    exe = shutil.which("pdftoppm")
    if exe is None:
        return None

    prefix = assets / "page"
    proc = subprocess.run(
        [exe, "-r", str(dpi), "-png", str(pdf), str(prefix)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        print(f"pdftoppm 执行失败：{(proc.stderr or proc.stdout or '').strip()}")
        return None

    produced = sorted(assets.glob("page-*.png"))
    for path in produced:
        suffix = path.stem.split("-")[-1]
        try:
            target = assets / f"{int(suffix):03d}.png"
        except ValueError:
            continue
        path.replace(target)
    return len(produced)


def render_with_fitz(pdf: Path, assets: Path, dpi: int) -> int | None:
    """用 PyMuPDF 渲染，成功返回页数，不可用返回 None。"""
    try:
        import pymupdf as fitz  # type: ignore[import-not-found]
    except ImportError:
        try:
            import fitz  # type: ignore[import-not-found]
        except ImportError:
            return None

    document = fitz.open(str(pdf))
    count = 0
    try:
        for page_no, page in enumerate(document, start=1):
            try:
                pixmap = page.get_pixmap(dpi=dpi)
            except TypeError:
                # 旧版 PyMuPDF 不支持 dpi 参数
                zoom = dpi / 72.0
                pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            pixmap.save(str(assets / f"{page_no:03d}.png"))
            count += 1
    finally:
        document.close()
    return count


def main(argv: list[str]) -> int:
    dpi = DEFAULT_DPI
    paths: list[str] = []
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg == "--dpi":
            index += 1
            if index >= len(argv):
                print("--dpi 后面需要跟一个数字")
                return 2
            try:
                dpi = int(argv[index])
            except ValueError:
                print(f"--dpi 需要是整数，收到：{argv[index]}")
                return 2
        else:
            paths.append(arg)
        index += 1

    if len(paths) != 2:
        print(__doc__)
        return 2

    pdf = Path(paths[0]).expanduser()
    out_dir = Path(paths[1]).expanduser()

    if not pdf.is_file():
        print(f"找不到文件：{pdf}")
        return 1
    if pdf.suffix.lower() != ".pdf":
        print(f"仅支持 .pdf，收到：{pdf.suffix}")
        return 1

    assets = out_dir / "assets"
    out_dir.mkdir(parents=True, exist_ok=True)
    assets.mkdir(parents=True, exist_ok=True)

    count = render_with_pdftoppm(pdf, assets, dpi)
    tool = "pdftoppm"
    if count is None:
        count = render_with_fitz(pdf, assets, dpi)
        tool = "PyMuPDF"

    if count is None:
        print("未能渲染 PDF：本机既没有 pdftoppm，也没有 PyMuPDF。")
        print("可选方案：")
        print("  1) 安装 poppler 并把 bin 目录加入 PATH")
        print("  2) 运行 pip install pymupdf")
        print("  3) 请用户用 PDF 阅读器逐页截图，作为图片输入")
        return 1

    print(f"渲染工具：{tool}（{dpi} dpi）")
    print(f"导出页数：{count} 页 → {assets}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
