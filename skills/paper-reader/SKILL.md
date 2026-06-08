---
name: paper-reader
description: |
  Use when user asks to "read paper", "analyze paper", "summarize paper",
  "读论文", "分析文献", "帮我看一下这篇paper", "论文笔记", or provides a PDF file
  that appears to be an academic paper. Specialized for CV/DL papers.

  Also supports Zotero integration: "读一下这篇论文 ...", "快速看一下这篇论文 ...",
  "批判性分析这篇论文 ...", "读一下 Zotero 里的 XXX", "批量读一下 Zotero 里 VLA 分类下的论文"

  **重要触发词**: "读一下 XXX"、"读一下这篇"、"帮我读" → 必须调用此 skill
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch, WebSearch
---

> **开始前**: 先跟用户打个招呼 🐕

# 学术论文阅读助手 (Paper Reader)

专注 CV/DL 领域，支持 Zotero 集成和 Obsidian 笔记保存。

## Step 0: 读取共享配置

先读取 `../_shared/user-config.json`，如果 `../_shared/user-config.local.json` 存在，再用它覆盖默认值。

显式生成并在后续统一使用这些变量：

- `VAULT_PATH`
- `NOTES_PATH`
- `CONCEPTS_PATH`
- `ZOTERO_DB`
- `ZOTERO_STORAGE`
- `AUTO_REFRESH_INDEXES`
- `GIT_COMMIT_ENABLED`
- `GIT_PUSH_ENABLED`

其中：

- `NOTES_PATH = {VAULT_PATH}/{paper_notes_folder}`
- `CONCEPTS_PATH = {NOTES_PATH}/{concepts_folder}`
- `GIT_PUSH_ENABLED` 只有在 `GIT_COMMIT_ENABLED=true` 时才可能为真

后续统一使用上面的变量。

## 1. 接收论文

| 输入方式 | 示例 | 处理方法 |
|----------|------|----------|
| PDF 路径 | `/path/to/paper.pdf` | 直接 Read |
| arXiv 链接 | `https://arxiv.org/abs/xxxx` | WebFetch |
| Zotero 分类 | "VLA 分类的论文" | 查询数据库 → 列出 → 用户选择 |
| Zotero 搜索 | "Zotero 里的 π0.5" | 搜索标题 → 找到 PDF |
| 无 PDF | Zotero 条目无附件 | 从网上获取（见下方） |

### 无 PDF 时的获取流程

1. `python3 assets/zotero_helper.py info {item_id}` 获取论文信息
2. 按优先级获取：arXiv HTML > arXiv PDF > DOI > WebSearch 标题
3. 判断 arXiv ID：从 URL / Zotero extra 字段 / 标题搜索
4. 推荐直接 WebFetch `https://arxiv.org/html/{arxiv_id}`，无需下载
5. 跳过条件：既无 PDF 也无在线来源 / 非论文内容

> Zotero 详细操作见 `references/zotero-guide.md`

## 2. 阅读模式

| 模式 | 触发词 | 输出 |
|------|--------|------|
| **快速摘要 / 检索** | "快速看一下"、"quick"、"review"、"检索" | `quick` 阅读报告 |
| **完整解析 / 深度阅读** | "详细分析"、"深度阅读"、默认 | `deep` 阅读报告 |
| **批判分析** | "批判性分析"、"critique" | `deep` 阅读报告 + 方法论优缺点评估 |
| **知识提取** | "提取公式"、"技术细节" | `deep` 阅读报告，重点补公式 + 算法伪代码 |

## 3. 笔记生成

**模板**:

- `quick` 模式严格遵循 `assets/paper-report-quick-template.md`，只写 `元信息`、`一句话总结`、`核心贡献`、`问题背景`。
- `deep` 模式严格遵循 `assets/paper-report-deep-template.md`，补全模板所有章节。
- 旧模板 `assets/paper-note-template.md` 仅作为深度报告的细节参考，不再作为唯一保存模板。

### 核心质量规则

1. **深度阅读优先**: 保留 `paper-deep.md` 的阅读流，包括核心贡献、问题背景、方法详解、关键公式、关键图表、实验、批判性思考、相关工作和速查卡片
2. **图谱检索增强**: 在深度阅读结构上补充 Dataview 友好的 YAML 字段、增强元信息表、快速索引和知识关系区
3. **中等完整**: 保留关键方法图、1-3 个核心公式、主结果表/实验结论、主要局限证据；不要默认搬运所有 Figure/Table/公式
4. **内联双链**: 正文中首次出现的重要概念、方法、数据集、baseline、任务和机构必须用 `[[概念]]` 链接，不仅仅是结尾
5. **严禁 ASCII 流程图**: 用结构化 Markdown 列表 + `$数学符号$` 描述架构
6. **公式完整性**: 每个关键公式必须有名称（`[[概念|名称]]`）、LaTeX 公式、含义、符号说明
7. **图片外链优先**: arXiv HTML / 项目主页 / GitHub，找不到再本地下载

> 公式/图片/表格的详细质量规范见 `references/quality-standards.md`

### 图片获取流程（多源 fallback）

**目标**: 确保笔记中包含最能支撑知识关系和方法理解的关键图片。默认至少包含 1 张方法总览/系统架构图；如果论文的核心贡献依赖实验可视化，再补充关键结果图。只有用户明确要求“完整图表提取”时，才按 `references/quality-standards.md` 的零遗漏标准处理所有 Figure/Table/公式。

1. **先确定 arXiv ID**：
   - 如果用户输入是 arXiv abs/pdf/html 链接，直接解析 ID
   - 如果只有标题，先 WebSearch `"{论文标题} arxiv"` 获取 arXiv ID
2. **来源 A — arXiv HTML（必须先尝试，不能静默跳过）**：
   - 只要存在 arXiv ID，就必须先 WebFetch `https://arxiv.org/html/{arxiv_id}`
   - 提取 `<figure>` / `<img>` / caption 中的图片 URL、Figure 编号和标题
   - 优先选择 Overview / Architecture / Method / Pipeline / Main Results 等关键图
   - 如果 arXiv HTML 不可访问、无 `<figure>`、图片 URL 为空、图片 URL 无法加载，必须在笔记的“关键图表”或“自检备注”中写明失败原因，例如：`arXiv HTML 图片提取失败：HTML 404` / `未找到可用 figure URL`
   - 只有记录失败原因后，才允许进入项目主页或 PDF 兜底
3. **来源 B — 项目主页**（HTML 失败或图片不全时）：
   - 从摘要/HTML 中查找项目主页 URL（常见模式：`project page`、`github.io`、`our website`）
   - WebFetch 项目主页，提取展示图片（通常包含 teaser / demo 图）
4. **来源 C — PDF 提取 / 裁图**（前两者都失败时）：
   - 优先用 `pdfimages -png` 从 PDF 中提取，筛选 >10KB 的有效图片
   - 如果环境没有 `pdfimages`，使用可用 PDF 库（如 PyMuPDF/fitz）按 Figure 所在页裁出关键图，保存到笔记同目录 `assets/`
   - PDF 兜底产物用 Obsidian wikilink 嵌入：`![[{MethodName}_fig1_overview.png]]`
5. **写入笔记**：
   - 在线图片用 `![Figure X](url)` 外链嵌入
   - 本地图片用 `![[local_image.png]]` 嵌入
   - 不能只写 Figure 标题和说明；至少 1 张关键图必须有实际图片嵌入，除非所有来源都失败且已写明失败原因
6. **验证**：外链可加载 / 本地文件 >10KB
7. **URL 去重**：写入前检查 URL 中是否有重复的 arxiv_id 路径段（如 `2603.05312v1/2603.05312v1/`），有则删除重复段。详见 `references/image-troubleshooting.md`

> ar5iv 编号不一定对应 Figure 编号，排错见 `references/image-troubleshooting.md`

### 图片可靠性保障（生成后自动执行）

笔记保存后，运行图片可达性检查脚本，自动将不可访问的外链图片下载到本地：
```bash
python3 ../daily-papers/download_note_images.py "{笔记完整路径}"
```
- 可达的外链保持不动，不可达的自动下载到 `assets/` 并替换为 Obsidian wikilink
- 如有本地化操作，frontmatter `image_source` 自动更新为 `mixed`

### 公式格式

每个公式必须包含：名称（`[[概念|名称]]`）、LaTeX `$$` 块（前后留空行）、含义、符号列表。
`$$` 块前后**必须有空行**否则 Obsidian 不渲染。超长公式用 `aligned` 拆分。

## 4. Obsidian 保存

### 文件命名

只用**方法名/模型名**：`{方法名}.md`（如 `Pi05.md`，不加年份前缀）。
方法名判断：标题冒号前 / Abstract 中 "We propose XXX" / 希腊字母转 ASCII。
不确定时保存到 `_待整理/`。

### 保存路径

报告与已下载 PDF 统一按年份和来源归档：

```text
{NOTES_PATH}/{YYYY}/{来源}/{basename}.md
{NOTES_PATH}/{YYYY}/{来源}/{basename}.pdf
```

- `YYYY` 来自论文发表年、会议年或 arXiv 版本年。
- `来源` 使用规范化标签：`arxiv`、`NeurIPS`、`ICLR`、`ICML`、`CVPR`、`ICCV`、`ECCV`、`ACL`、`AAAI`、`ACMMM`。
- `basename` 优先使用方法名/模型名；无法判断时用规范化标题 slug。
- 如果下载了 PDF，必须保存为与报告同名的 `.pdf`，与 `.md` 放在同一目录。

### YAML frontmatter

```yaml
---
type: paper
title: "论文标题"
method_name: "MethodName"
authors: [Author1, Author2]
institutions: [Institution1, Institution2]
institution_types: [university, industry]
year: 2025
venue: arXiv
source: arxiv
report_mode: deep
summary_status: complete
status: read
relevance: high
research_line: [robot-learning, world-model]
problem: [long-horizon-manipulation]
method_family: [diffusion-policy]
core_concepts: [Diffusion Policy, Action Chunking]
datasets: [DROID, LIBERO]
baselines: [OpenVLA, Pi0.5]
tasks: [manipulation]
claims: [better-generalization]
limitations: [sim-to-real-gap]
tags: [paper, tag1, tag2]  # 小写连字符，3-8 个
zotero_collection: 3-Robotics/1-VLX/VLA
pdf_path: "论文笔记/2025/arxiv/MethodName.pdf"
image_source: online
arxiv: https://arxiv.org/abs/XXXX
code: https://github.com/...
created: YYYY-MM-DD
---
```

字段规则：
- `institutions` 记录机构级作者单位，例如 `NVIDIA`、`Stanford University`、`Google DeepMind`
- `institution_types` 使用 `university` / `industry` / `institute` / `unknown`
- `research_line`、`problem`、`method_family`、`tasks` 使用稳定英文 slug，便于 Dataview 查询
- `core_concepts`、`datasets`、`baselines`、`institutions` 使用规范实体名，必须能和正文 `[[...]]` 双链对应
- Tags 判断：看 Related Work 小标题 + Abstract 关键词。第一个 tag 是最核心主题

### 保存后自动执行

0. 验证报告路径符合 `{NOTES_PATH}/{YYYY}/{来源}/{basename}.md`；如果存在同名 PDF，确认 `{basename}.pdf` 与报告同目录。
1. 只有在 `AUTO_REFRESH_INDEXES=true` 时才刷新目录页：
   ```bash
   python3 ../_shared/generate_concept_mocs.py
   python3 ../_shared/generate_paper_mocs.py
   ```
2. 只有在 `GIT_COMMIT_ENABLED=true` 时才做 git：
   - 先确认 `VAULT_PATH/.git` 存在
   - `git add {新增文件} {paper_notes_folder}/` 后必须真的有 staged changes
   - 满足条件后再执行：
   ```bash
   cd {VAULT_PATH} && git add {新增文件} {paper_notes_folder}/ && git commit -m "add paper note: {方法名}"
   ```
   - 只有在 `GIT_PUSH_ENABLED=true` 且仓库已配置远端时才 push

## 5. 概念库维护（每篇论文必做）

概念库位置：`{CONCEPTS_PATH}`

### 流程

1. **扫描**论文笔记中所有 `[[概念]]` 链接
2. **区分节点类型**：
   - 技术概念、方法、数据集、benchmark、仿真器、硬件平台 -> 概念库
   - 机构 -> `{NOTES_PATH}/_实体/机构/`
   - 作者个人默认不建节点，除非用户明确要求追踪作者
3. **检查**每个链接对应的笔记是否存在（`ls` + `find`）
4. **创建**不存在的概念或机构节点（不可跳过），自动归类到对应子目录

> 分类规则和模板见 `references/concept-categories.md`

### 自检

- [ ] 笔记中所有 `[[概念]]` 链接的概念笔记都存在？
- [ ] `institutions` 字段中的机构都有对应 `[[机构]]` 双链？
- [ ] 概念笔记包含本论文作为"代表工作"？

## 6. 完成后自检（合并 checklist）

- [ ] YAML frontmatter 包含 `type/status/relevance/institutions/research_line/problem/method_family/core_concepts/datasets/baselines/tasks/claims/limitations`？
- [ ] 正文保留 `paper-deep.md` 的深度阅读主线，而不是只输出索引和关系？
- [ ] `institutions` 是机构级列表，正文“作者与机构”小节使用了机构双链？
- [ ] “知识关系”小节包含解决的问题、使用的方法、前置工作、对比工作、产生的新问题？
- [ ] 至少包含 1 张关键方法图或系统图的实际图片嵌入（`![...](...)` 或 `![[...]]`），不能只有 Figure 标题和说明？
- [ ] 图片来源链路已执行：arXiv HTML 优先；如失败，已记录失败原因并尝试项目主页/PDF 兜底？
- [ ] 图片可用（外链可加载 / 本地 >10KB）？
- [ ] 报告与 PDF 位于 `论文笔记/{年份}/{来源}/`，且同名不同扩展名？
- [ ] frontmatter 中 `report_mode`、`source`、`paper_id`、`summary_status` 已填写？
- [ ] 至少包含 1 个核心公式或明确说明"本文无关键公式/公式不适用"？
- [ ] 至少包含主结果表/关键实验结论，并判断证据强度？
- [ ] 正文中重要技术术语、数据集、baseline、机构有 `[[概念]]` 内联链接？
- [ ] 概念库已更新（缺失的概念已创建）？

## 7. 交互式功能

完成解析后询问：是否需要升级为深度阅读、对比其他论文或补充实验细节。
所有模式都必须保存到 Obsidian；`quick` 可后续升级为 `deep`，升级时覆盖同名 `.md` 并将 `summary_status` 改为 `complete`。

## 8. 批量处理

支持 Zotero 分类批量处理（默认递归子分类）。流程：递归获取论文 → 去重 → 跳过已有笔记 → 依次处理 → 汇总。

## 参考文件（按需查阅）

- **`references/zotero-guide.md`** — Zotero 查询、分类、PDF 路径获取、智能分类判断
- **`references/image-troubleshooting.md`** — ar5iv 图片编号对应、PDF 提取备选
- **`references/concept-categories.md`** — 概念自动归类的 16 个子目录规则 + 模板
- **`references/quality-standards.md`** — 公式/图片/表格的详细质量规范 + 自检清单
