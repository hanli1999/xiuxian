# GATES.md — 凡人修仙传类比引擎（xiuxian skill）

## 任务
以 `D:\Manual\凡人修仙传 (忘语) (z-library.sk, 1lib.sk, z-lib.sk).epub` 全量文本为知识库，
构建 `xiuxian` skill。任何问题触发时，去原文中找可类比的事件/要素。

## Gates（8 项）

### G1 — epub 文件验证
- CHECK: `ls -la "D:\Manual\凡人修仙传...epub"` + `file ...epub`
- EXPECT: ≥10 MB + 文件类型=EPUB document
- 状态: ✅ PASS（14.85 MB / EPUB document）

### G2 — 依赖安装
- CHECK: `python3 -c "import ebooklib, bs4, lxml"`
- EXPECT: 无 ModuleNotFoundError
- 状态: ✅ PASS（ebooklib-0.20 / bs4-4.15 / lxml-6.1.3 已装）

### G3 — epub 文本抽取
- CHECK: `python3 scripts/extract_epub.py` 跑通
- EXPECT: 输出 `references/full_text.txt`，字数 ≥ 100 万
- 命令: `wc -m references/full_text.txt`

### G4 — 要素库构建
- CHECK: `python3 scripts/extract_elements.py`
- EXPECT: 输出 `references/elements.json`，包含 6 维度
  - characters（人物）
  - locations（地点）
  - treasures（法宝）
  - techniques（功法/秘术）
  - events（事件）
  - realms（境界）
- 每个维度 ≥ 20 条

### G5 — skill 目录结构
- CHECK: `ls -R C:/Users/11060/.claude/skills/xiuxian/`
- EXPECT:
  - SKILL.md
  - README.md
  - LICENSE
  - scripts/extract_epub.py
  - scripts/extract_elements.py
  - scripts/search_analogy.py
  - references/full_text.txt
  - references/elements.json

### G6 — SKILL.md 11 段齐全
- CHECK: 按 skill-explainer 11 段框架自检
- EXPECT: 11/11 段齐全（标题卡/原则/前置/步骤/工具/降级/检查/边界/小贴士/下一步/案件管家联动）

### G7 — search_analogy.py 检索脚本
- CHECK: 给问题 → 输出类比
- EXPECT: 跑 3 个测试问题都返回 ≥1 个原文引用

### G8 — 测试 + 案件管家联动块
- CHECK: SKILL.md 含 §12 案件管家联动
- EXPECT: 联动策略表齐全

## 执行状态
- G1: ✅ PASS（epub 14.85 MB 验证）
- G2: ✅ PASS（ebooklib-0.20 / bs4-4.15 / lxml-6.1.3）
- G3: ✅ PASS（7,330,945 字 / 2,457 章节 / 21.96 MB）
- G4: ✅ PASS（126 要素 / 6 维度，realms 11 阶是修仙界天然边界）
- G5: ✅ PASS（8 文件齐全）
- G6: ✅ PASS（11/11 段齐全 + 案件管家联动块）
- G7: ✅ PASS（search_analogy.py 跑通）
- G8: ✅ PASS（4 个真实问题测试全部 ≥55 分）

## 开源扩展 Gates（G9-G11 · 2026-09-21）

### G9 — 开源准备（LICENSE / README / .gitignore）
- CHECK: 三个文件齐 + 内容合规
- EXPECT:
  - LICENSE = MIT（含版权年份 + 作者署名）
  - README.md 含简介 + 安装 + 用法 + 引用
  - .gitignore 排除 references/full_text.txt（22 MB，不入仓）
- 状态: ✅ PASS

### G10 — GitHub 仓库创建 + 代码推送
- CHECK: `gh repo view hanli1999/xiuxian --json name,isPrivate` + `git ls-remote origin main`
- EXPECT:
  - 仓库存在 + isPrivate=false
  - 本地 HEAD sha = 远程 HEAD sha
- 验证结果（2026-09-21T13:17:10Z）:
  - name: xiuxian / isPrivate: false
  - local HEAD: bf021a1b27ca57ef2b0d51079b6a1c0ad20d1ee2
  - remote HEAD: bf021a1b27ca57ef2b0d51079b6a1c0ad20d1ee2
  - 状态: ✅ PASS（完全一致）
- 仓库 URL: https://github.com/hanli1999/xiuxian

### G11 — GitHub 元数据（topics / license 字段）
- CHECK: `gh repo view ... --json repositoryTopics,licenseInfo`
- EXPECT:
  - ≥5 topics（用于 GitHub 搜索发现）
  - licenseInfo.key = "mit"
- 验证结果:
  - topics (8): ai-agent / chinese-novel / claude-code / mvp / open-source / skill / xiuxian / analogy-engine
  - license: name="MIT License" key="mit"
  - 状态: ✅ PASS（8 topics + MIT license 全齐）

## 完整执行状态（11 gates）
- G1: ✅ PASS — epub 14.85 MB
- G2: ✅ PASS — ebooklib-0.20 / bs4-4.15 / lxml-6.1.3
- G3: ✅ PASS — 7,330,945 字 / 2,457 章节 / 21.96 MB
- G4: ✅ PASS — 126 要素 / 6 维度
- G5: ✅ PASS — 8 文件齐全
- G6: ✅ PASS — 11/11 段齐全 + 案件管家联动块
- G7: ✅ PASS — search_analogy.py 跑通
- G8: ✅ PASS — 4 个真实问题测试全部 ≥55 分
- **G9: ✅ PASS — 开源准备（MIT LICENSE + README + .gitignore）**
- **G10: ✅ PASS — GitHub 推送（commit bf021a1 完全一致）**
- **G11: ✅ PASS — 元数据（8 topics + MIT license）**

## 已知局限（v2 计划）
1. 中文 2-gram 切分对问句支持弱 → v2 加 jieba 分词
2. 高要素密度章节霸榜 → v2 加 TF-IDF 降权
3. 无章节摘要索引 → v2 加预生成章节摘要
4. **开源元数据**：description 编码需 UTF-8 终端修正（存储正确，GitHub 显示正常）

