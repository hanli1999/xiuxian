#!/usr/bin/env python3
"""search_analogy.py — 凡人修仙传类比检索引擎

输入: 用户问题（一段文本）
处理:
    1. 加载要素库 references/elements.json（126 要素 / 6 维度）
    2. 加载全量文本 references/full_text.txt（730 万字 / 2457 章节）
    3. 提取问题关键词 + 要素名做联合匹配
    4. 章节级评分排序
输出: Top N 最相关章节片段 + 命中的要素 + 原文引用

用法:
    python3 search_analogy.py --question "如何面对强大敌人"
    python3 search_analogy.py --question "资源争夺" --top 3
    python3 search_analogy.py --question "如何在弱小阶段活下来" --format json
"""
import argparse
import io
import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


BASE_DIR = Path(__file__).parent.parent
ELEMENTS_PATH = BASE_DIR / "references" / "elements.json"
FULL_TEXT_PATH = BASE_DIR / "references" / "full_text.txt"


def load_elements() -> dict:
    """加载要素库"""
    data = json.loads(ELEMENTS_PATH.read_text(encoding="utf-8"))
    return data["elements"]


def load_chapters() -> list:
    """加载全量文本并按章节切分"""
    text = FULL_TEXT_PATH.read_text(encoding="utf-8")
    # 章节分隔符: ===== 第一章 =====
    parts = re.split(r"\n\n=====\s*(.*?)\s*=====\n\n", text)
    # parts[0] 是空（开头），之后是 (title, body) 交替
    chapters = []
    for i in range(1, len(parts), 2):
        title = parts[i].strip()[:80]
        body = parts[i + 1] if i + 1 < len(parts) else ""
        chapters.append({"title": title, "body": body, "length": len(body)})
    return chapters


def extract_keywords(question: str) -> list:
    """简单关键词提取（中文 2-gram + 要素名匹配）"""
    keywords = set()
    # 2-gram 切分
    question_clean = re.sub(r"[^\w一-鿿]", " ", question)
    for i in range(len(question_clean) - 1):
        w = question_clean[i:i + 2].strip()
        if w and not w.isspace():
            keywords.add(w)
    # 单词也保留
    for w in question_clean.split():
        if len(w) >= 2:
            keywords.add(w)
    return list(keywords)


def score_chapter(chapter: dict, keywords: list, element_names: list) -> dict:
    """对单章节评分"""
    body = chapter["body"]
    title = chapter["title"]

    # 关键词密度（每千字命中数）
    kw_hits = sum(body.count(kw) for kw in keywords)
    kw_score = kw_hits / max(1, len(body) / 1000)

    # 要素命中（按要素名）
    elem_hits = []
    for elem in element_names:
        if elem in body:
            elem_hits.append(elem)

    # 综合分
    total = kw_score * 1.0 + len(elem_hits) * 5.0  # 要素命中权重更高

    return {
        "title": title,
        "length": chapter["length"],
        "kw_hits": kw_hits,
        "kw_score": round(kw_score, 2),
        "elem_hits": elem_hits,
        "elem_count": len(elem_hits),
        "total_score": round(total, 2),
    }


def find_relevant_excerpt(body: str, keywords: list, max_chars: int = 400) -> str:
    """找最相关的片段（含最多关键词的窗口）"""
    if not keywords:
        return body[:max_chars]

    # 滑窗找关键词密度最高的片段
    best_count = -1
    best_start = 0
    window = max_chars
    step = 100

    for start in range(0, max(1, len(body) - window), step):
        chunk = body[start:start + window]
        count = sum(chunk.count(kw) for kw in keywords)
        if count > best_count:
            best_count = count
            best_start = start

    excerpt = body[best_start:best_start + window].strip()
    return excerpt


def search(question: str, top_n: int = 5) -> list:
    """主入口"""
    elements = load_elements()
    chapters = load_chapters()

    # 加载所有要素名
    all_elements = []
    for dim, items in elements.items():
        for item in items:
            all_elements.append(item["name"])

    # 关键词提取
    keywords = extract_keywords(question)

    # 评分
    scored = []
    for ch in chapters:
        score = score_chapter(ch, keywords, all_elements)
        if score["total_score"] > 0:
            scored.append(score)

    # 排序
    scored.sort(key=lambda x: x["total_score"], reverse=True)

    # 提取相关片段
    for s in scored[:top_n]:
        # 重新加载 body
        for ch in chapters:
            if ch["title"] == s["title"]:
                s["excerpt"] = find_relevant_excerpt(ch["body"], keywords)
                break

    return scored[:top_n]


def format_markdown(question: str, results: list) -> str:
    """格式化为 Markdown 输出"""
    lines = [
        f"# 🔮 凡人修仙传·类比检索",
        "",
        f"**问题**: {question}",
        f"**找到 {len(results)} 个相关章节**",
        "",
        "---",
        "",
    ]

    for i, r in enumerate(results, 1):
        lines.extend([
            f"## #{i} {r['title']}",
            "",
            f"- 关键词命中: {r['kw_hits']} 次（密度 {r['kw_score']}/千字）",
            f"- 要素命中: {r['elem_count']} 个 ({', '.join(r['elem_hits'][:8])}{'...' if len(r['elem_hits']) > 8 else ''})",
            f"- 综合评分: {r['total_score']}",
            f"- 章节长度: {r['length']:,} 字",
            "",
            "### 原文片段",
            "",
            f"> {r.get('excerpt', '(无片段)')}",
            "",
            "---",
            "",
        ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="凡人修仙传·类比检索引擎")
    parser.add_argument("--question", "-q", required=True, help="用户问题")
    parser.add_argument("--top", "-n", type=int, default=5, help="返回 Top N（默认 5）")
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    print(f"🔍 检索: {args.question}", file=sys.stderr)
    results = search(args.question, args.top)
    print(f"📚 找到 {len(results)} 个相关章节", file=sys.stderr)

    if args.format == "json":
        print(json.dumps({"question": args.question, "results": results}, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(args.question, results))


if __name__ == "__main__":
    main()
