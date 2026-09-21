#!/usr/bin/env python3
"""extract_epub.py — 抽取凡人修仙传 epub 全量文本

输入: D:/Manual/凡人修仙传 (忘语) (z-library.sk, 1lib.sk, z-lib.sk).epub
输出: references/full_text.txt（UTF-8 纯文本，章节间用换行分隔）
"""
import io
import os
import re
import sys
from pathlib import Path

# Windows GBK 编码修正
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import ebooklib
from ebooklib.epub import read_epub
from bs4 import BeautifulSoup


EPUB_PATH = r"D:\Manual\凡人修仙传 (忘语) (z-library.sk, 1lib.sk, z-lib.sk).epub"
OUTPUT_TXT = Path(__file__).parent.parent / "references" / "full_text.txt"


def extract(epub_path: str = None, output_path: Path = None):
    """抽取 epub 全量文本

    Args:
        epub_path: epub 文件路径（默认 = hanli1999 本地路径）
        output_path: 输出文本路径（默认 = references/full_text.txt）
    """
    src = Path(epub_path) if epub_path else Path(EPUB_PATH)
    dst = output_path if output_path else OUTPUT_TXT

    if not src.exists():
        print(f"❌ epub 文件不存在: {src}")
        print(f"   用法: python3 extract_epub.py --epub <你的 epub 路径>")
        return None

    print(f"正在打开: {src}")
    book = read_epub(str(src))

    # metadata
    title = book.get_metadata("DC", "title")
    creator = book.get_metadata("DC", "creator")
    print(f"  标题: {title[0][0] if title else '(无)'}")
    print(f"  作者: {creator[0][0] if creator else '(无)'}")

    chapters = []
    chapter_count = 0
    total_chars = 0

    # 遍历所有文档项
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        content = item.get_content().decode("utf-8", errors="ignore")
        soup = BeautifulSoup(content, "lxml")

        # 提取纯文本
        text = soup.get_text(separator="\n", strip=True)

        # 过滤掉太短的非正文（< 50 字可能是目录、版权页）
        if len(text) < 50:
            continue

        # 跳过纯目录页（含大量"第N章"但正文极少）
        if re.match(r"^(目录|序章|前言|后记|番外)", text[:50]):
            if len(text) < 500:
                continue

        # 用章节标题开头（如果检测到）
        first_line = text.split("\n")[0][:80]
        chapter_count += 1
        chapters.append(f"\n\n===== {first_line} =====\n\n{text}")
        total_chars += len(text)

    print(f"  抽取章节数: {chapter_count}")
    print(f"  总字符数: {total_chars:,}")

    # 写入文件
    dst.parent.mkdir(parents=True, exist_ok=True)
    full_text = "".join(chapters)
    dst.write_text(full_text, encoding="utf-8")
    print(f"  写入: {dst}")
    print(f"  文件大小: {dst.stat().st_size:,} bytes")

    return total_chars, chapter_count


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="抽取凡人修仙传 epub → 全量文本")
    parser.add_argument("--epub", help="epub 文件路径（默认 = hanli1999 本地路径）")
    parser.add_argument("--output", "-o", help="输出文本路径（默认 = references/full_text.txt）")
    args = parser.parse_args()

    try:
        output = Path(args.output) if args.output else None
        result = extract(args.epub, output)
        if result:
            chars, n = result
            print(f"\n✅ 抽取完成: {n} 章节 / {chars:,} 字符")
    except Exception as e:
        print(f"\n❌ 抽取失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
