---
name: daily-papers-fetch
description: |
  论文抓取（3 步流水线的第 1 步）。抓取 arXiv + HuggingFace 最新论文 + AI 顶会官方论文，打分筛选，富化信息，
  输出到 /tmp/daily_papers_enriched.json 供后续 skill 使用。

  触发词："论文抓取"、"跑一下论文抓取"、"顶会论文推荐"、"抓取 NeurIPS 2025"、"看看 ICLR 2025 有什么"
  支持多天模式："过去3天论文推荐"、"过去一周论文推荐"、"过去一周的论文"、"抓 3 天的论文"、"最近5天"
---

> **开始前**: 先说一声 "开始抓取论文 🐕" 并告知今天日期。如果是多天模式，告知抓取范围。

# 论文抓取 (Fetch + Score + Enrich)

你是 用户的论文抓取系统（3 步流水线的第 1 步）。抓取最新论文 → 打分筛选 → 富化信息 → 保存到临时文件。

## Step 0: 读取共享配置

先读取 `../_shared/user-config.json`，如果 `../_shared/user-config.local.json` 存在，再用它覆盖默认值。

显式生成并在后续统一使用这些变量：

- `VAULT_PATH`
- `DAILY_PAPERS_PATH`
- `KEYWORDS`
- `NEGATIVE_KEYWORDS`
- `DOMAIN_BOOST_KEYWORDS`
- `ARXIV_CATEGORIES`
- `MIN_SCORE`
- `TOP_N`
- `CONFERENCE_ENABLED`
- `CONFERENCE_VENUES`
- `CONFERENCE_YEARS`
- `MAX_PER_VENUE`

其中：

- `DAILY_PAPERS_PATH = {VAULT_PATH}/{daily_papers_folder}`
- 所有关键词、分类、阈值都以共享配置为准
- 顶会抓取配置来自 `conference_papers`，默认官方来源优先

后续统一以共享配置和上面的变量为准。

## 解析天数

从用户输入中解析 `--days N` 参数。匹配规则：
- "过去一周"、"最近7天"、"一周的论文" → `--days 7`
- "过去3天"、"最近三天"、"抓3天" → `--days 3`
- "过去两周" → `--days 14`
- 无特殊指定 / "跑一下论文抓取" → 不加 `--days`（默认当天）

将解析出的天数存为变量 `DAYS_ARG`，在后续脚本调用中使用。

## 解析顶会参数

当用户提到顶会、会议名或年份时，生成会议参数：

- "顶会论文推荐" -> 使用 `conference_papers.venues` 和 `conference_papers.years`
- "抓取 NeurIPS 2025" -> `--include-conferences --venue NeurIPS --conference-year 2025`
- "看看 ICLR 2025 有什么" -> `--include-conferences --venue ICLR --conference-year 2025`
- 支持会议名：NeurIPS、AAAI、ACM MM、ICLR、ICML、CVPR、ACL、ICCV、ECCV

如果用户没有显式会议参数，但 `conference_papers.enabled=true`，脚本会按配置自动纳入会议来源。

## 配置来源

- 默认配置在 `../_shared/user-config.json`
- 个人覆盖配置放在 `../_shared/user-config.local.json`
- 如果两者都存在，以 `local` 为准

## 工作流程

### Phase 1+2: 抓取 + 打分 + 合并去重（纯 Python 脚本）

用 `fetch_and_score.py` 一步完成 HF + arXiv + 顶会官方来源抓取、打分、合并去重、历史去重、选 Top 30。**零 token 消耗。**

```bash
# 默认：当天
python3 ../daily-papers/fetch_and_score.py > /tmp/daily_papers_top30.json

# 多天模式（将 N 替换为解析出的天数）
python3 ../daily-papers/fetch_and_score.py --days N > /tmp/daily_papers_top30.json

# 顶会模式
python3 ../daily-papers/fetch_and_score.py --include-conferences --venue NeurIPS --conference-year 2025 > /tmp/daily_papers_top30.json
```

根据前面解析的 `DAYS_ARG` 和会议参数组装命令；如果用户指定了天数就加 `--days N`，如果用户指定会议就加 `--include-conferences --venue ... --conference-year ...`。

脚本自动完成：
- 并行抓取 HuggingFace Daily + Trending API 和 arXiv API
- 从官方来源抓取 AI 顶会论文：OpenReview（NeurIPS/ICLR/ICML）、CVF（CVPR/ICCV）、ACL Anthology、AAAI/OJS、SIGMM Open TOC（ACM MM）
- 关键词打分（正向/负向/领域加分/trending 加分）
- 按 arXiv ID、DOI、OpenReview forum、ACL Anthology ID、CVF paper path、标题 hash 合并去重
- 读取 `.history.json` 跨天去重（含周末模式放宽规则）
- 不足 20 篇时从历史回填
- 按 score 降序取 Top 30

进度日志输出到 stderr，JSON 结果输出到 stdout。

**检查输出**：确认 `/tmp/daily_papers_top30.json` 存在且包含有效 JSON 数组。如果为空数组或文件不存在，检查 stderr 诊断问题。

### Phase 3: 批量富化（enrich_papers.py 脚本）

用 `enrich_papers.py` 脚本一次性富化所有论文。脚本使用 `asyncio` + `curl` 子进程并发请求，纯 regex 解析 HTML，无需 WebFetch。

**先把 Phase 2 的 Top 30 结果保存到临时文件**，然后运行：

```bash
cat /tmp/daily_papers_top30.json | python3 ../daily-papers/enrich_papers.py /tmp/daily_papers_enriched.json
```

注意：使用**文件路径参数**（而非 stdout 重定向），避免 sandbox 环境下 stdout/stderr 混淆。

脚本自动完成以下工作（Semaphore(10) 限制并发，单篇超时 30 秒）：
- 并行抓取 HTML 页面 + PDF 页面
- 从 HTML 提取：figure_url、authors、affiliations、section_headers、captions、has_real_world、method_names、method_summary
- 从 PDF 提取：affiliations（通过 `pdftotext | extract_affiliations.py`）
- 如果 HTML authors 为空，fallback 到 abs 页面 `<meta>` 标签提取 authors/affiliations
- 合并优先级（脚本内部处理）：
  - figure_url: HTML curl
  - affiliations: PDF > HTML > abs fallback > Phase 1 data
  - authors: HTML > abs fallback > Phase 1 data
  - 其他字段: HTML regex 提取

**输出格式**：与输入相同的 JSON 数组，每篇论文增加以下字段：
- `figure_url` (string): 首图 URL
- `affiliations` (string): 机构列表，逗号分隔
- `authors` (string): 作者列表（可能被更完整的来源覆盖）
- `section_headers` (array): 章节标题
- `captions` (array): 图表标题
- `has_real_world` (bool): 是否包含真实实验
- `method_names` (array): 方法名列表
- `method_summary` (string): 方法描述（300-500 字）

## 输出

完成后检查 `/tmp/daily_papers_enriched.json` 存在且包含有效 JSON 数组。告知用户：
- 抓取了多少篇论文
- 富化成功多少篇
- 提示运行下一步：`跑一下论文点评`

## 注意事项

- Phase 1+2 使用 `fetch_and_score.py` 脚本，**不启动 Task Agent**，零 token 消耗
- Phase 3 使用 `enrich_papers.py` 脚本，同样不启动 Task Agent
- 如果脚本执行失败，检查 stderr 输出诊断问题
- 如果 arXiv API 抓取失败，脚本自动 fallback 到仅 HuggingFace 源
- 如果某个顶会官方来源抓取失败，脚本记录 warning 并继续其他来源，不中断整个流程
- 如果总论文数不足 20 篇，有多少处理多少
- **周末策略**：arXiv 周末不更新，HF daily 周末基本为空，但 HF trending 持续更新。周末主要依赖 trending 来源
- **不做 git 操作**，不生成推荐文件，只输出临时 JSON
