---
type: paper
title: "{Title}"
method_name: "{MethodName}"
aliases: ["{MethodName}"]
authors: ["{Authors}"]
institutions: ["{Institutions}"]
institution_types: ["{InstitutionTypes}"]
year: "{Year}"
venue: "{Venue}"
conference: "{Conference}"
source: "{Source}"
paper_id: "{PaperId}"
report_mode: deep
summary_status: complete
status: read
relevance: "{high|medium|low}"
research_line: ["{ResearchLines}"]
problem: ["{Problems}"]
method_family: ["{MethodFamilies}"]
core_concepts: ["{CoreConcepts}"]
datasets: ["{Datasets}"]
baselines: ["{Baselines}"]
tasks: ["{Tasks}"]
claims: ["{Claims}"]
limitations: ["{Limitations}"]
tags: [paper, "{tags}"]
zotero_collection: "{zotero_path}"
pdf_path: "{PdfPath}"
image_source: online
arxiv: "{arxiv_url}"
arxiv_html: "{arxiv_html_url}"
code: "{code_url}"
project_page: "{project_page_url}"
created: "{date}"
---

# {MethodName}

## 元信息

| 项目 | 内容 |
|------|------|
| 标题 | {Title} |
| 方法/模型 | {MethodName} |
| 作者 | {Authors} |
| 作者单位 | [[{Institution1}]] · [[{Institution2}]] |
| 机构类型 | {university / industry / institute / unknown} |
| 发表 | {VenueOrConference} |
| 年份 | {Year} |
| 项目主页 | {project_page_url} |
| 来源 | {Source} |
| 链接 | [Paper]({paper_url}) / [PDF]({pdf_url}) / [Code]({code_url}) |
| 相关方向 | [[{ResearchLine1}]] · [[{ResearchLine2}]] |
| 关注度 | {high / medium / low}: {一句话理由} |
---

## 快速索引

| 维度 | 内容 |
|------|------|
| 解决问题 | [[{ProblemConcept1}]] · [[{ProblemConcept2}]] |
| 方法族 | [[{MethodFamily1}]] · [[{MethodFamily2}]] |
| 核心概念 | [[{CoreConcept1}]] · [[{CoreConcept2}]] |
| 数据集/Benchmark | [[{Dataset1}]] · [[{Dataset2}]] |
| 对比 Baseline | [[{Baseline1}]] · [[{Baseline2}]] |
| 任务/场景 | [[{Task1}]] · [[{Task2}]] |
| 关键 claim | {claim1}；{claim2} |
| 主要局限 | [[{LimitationConcept1}]] · [[{LimitationConcept2}]] |

---

## 知识关系

### 解决的问题

- [[{ProblemConcept1}]]: {本文具体解决该问题的哪个方面}
- [[{ProblemConcept2}]]: {如果有第二个核心问题，写清楚关系}

### 使用的方法

- [[{CoreMethodConcept}]]: {作为核心框架 / 表征 / 训练目标 / 推理机制}
- [[{SupportingConcept}]]: {作为辅助模块或实现技巧}

### 依赖的前置工作

- [[{PriorWorkOrConcept}]]: {本文继承、初始化、借鉴或扩展了什么}

### 对比的工作

- [[{Baseline1}]]: {为什么对比，本文相对它解决了什么}
- [[{Baseline2}]]: {对比关系}

### 产生的新问题

- [[{LimitationConcept}]]: {本文结果暴露出的限制或后续问题}

---

---

## 一句话总结

> {用一句话概括这篇论文的核心贡献，不超过50字}

---

## 核心贡献

1. **{贡献1标题}**: {简要说明}
2. **{贡献2标题}**: {简要说明}
3. **{贡献3标题}**: {简要说明}

---

## 问题背景

### 要解决的问题
{这篇论文要解决什么问题？首次出现的问题类型用 [[概念]] 链接。}

### 现有方法的局限
{之前的方法有什么不足？指出具体 baseline 或方法族，并使用 [[概念]] 链接。}

### 本文的动机
{为什么作者认为他们的方法能解决这个问题？}


## 方法详解

### 整体框架
{说明输入、核心模块、输出和训练/推理流程。首次出现的技术术语使用 [[概念]] 链接。}

### 输入输出

- 输入: {语言 / 图像 / 视频 / 音频 / 动作 / 状态等}
- 输出: {预测目标或生成对象}
- 训练信号: {监督信号、损失、偏好数据、轨迹数据等}

### 核心模块
{逐模块解释设计动机、实现方式和与现有方法的差异。}

1. **{模块1}**: {模块作用、输入输出、为什么必要}
2. **{模块2}**: {模块作用、输入输出、为什么必要}
3. **{模块3}**: {模块作用、输入输出、为什么必要}

### 损失函数 / 训练目标

$$
{核心损失或目标函数}
$$

**作用**: {说明该目标约束了什么行为。}

---

## 关键公式

### 公式1: [[{概念名}|{公式用途}]]

$$
{公式内容}
$$

**含义**: {一句话解释公式的作用}

**符号说明**:
- ${符号1}$: {含义}
- ${符号2}$: {含义}

### 公式2: [[{概念名}|{公式用途}]]

$$
{公式内容}
$$

**含义**: {一句话解释公式的作用}

**符号说明**:
- ${符号1}$: {含义}
- ${符号2}$: {含义}

---

## 关键图表

### Figure 1: {图题}

![Figure 1]({figure_url})

**说明**: {解释图片内容和关键信息}

### Table 1: {表格标题}

| Method | Metric1 | Metric2 |
|--------|---------|---------|
| [[{Baseline}]] | x.xx | x.xx |
| **[[{MethodName}]]** | **x.xx** | **x.xx** |

**说明**: {表格的关键发现}

---

## 实验

### 数据集

| 数据集 | 规模 | 特点 | 用途 |
|--------|------|------|------|
| [[{Dataset1}]] | {size} | {特点} | 训练/测试 |

### 主要结果
{总结主要定量结果、对比基线和统计显著性。}

### 消融实验
{总结关键消融和结论。}

### 证据强度
{strong / moderate / weak}: {说明样本范围、benchmark 可信度、是否真实实验、是否依赖人工标注等。}

---

## 批判性思考

### 优点
1. {优点1}
2. {优点2}

### 局限性
1. [[{LimitationConcept1}]]: {局限1}
2. [[{LimitationConcept2}]]: {局限2}

### 潜在改进
{结合用户研究方向提出可借鉴或可扩展点。}

### 可复现性

- [ ] 代码开源
- [ ] 权重开源
- [ ] 数据集可获取
- [ ] 训练细节充分
- [ ] 评测脚本或 benchmark 可用

---

## 相关工作

| 论文 | 关系 | 说明 |
|------|------|------|
| [[{相关论文1}]] | 基于/对比/同类 | {说明} |

---

## 可复用知识

### 可以借鉴

- {可以迁移到自己项目、实验设计或系统架构中的点}

### 不适合直接复用

- {由于数据、算力、硬件、任务假设或许可证导致的限制}

### 适合连接到的研究线

- [[{ResearchLine1}]]
- [[{ResearchLine2}]]

---

## 后续阅读

- [ ] [[{后续论文或概念}]]

---

## 速查卡片

> [!summary] {Title}
> - **核心**: {一句话核心}
> - **方法**: {关键方法}
> - **结果**: {主要结果}
> - **代码**: {GitHub链接}
