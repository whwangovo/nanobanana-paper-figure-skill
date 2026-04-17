[English](README.md) | [中文](README_zh.md)

# Nanobanana 论文绘图 Skill

一个 Claude Code skill，用于生成投稿级 CS 论文图表，支持 Gemini 和 OpenAI GPT-Image 双后端。

基于 [muxi-tk/nanobanana-image-generation](https://github.com/muxi-tk/nanobanana-image-generation) 开发——原始 skill 提供通用 Gemini 图像生成和材料科学绘图支持，本 fork 在此基础上增加了 CS 论文图层和多后端支持。

## 新增功能（相比上游）

- **双后端支持** — `--backend gemini|openai`，可选 Gemini 或 OpenAI GPT-Image（`gpt-image-1.5`）
- **CS 论文图模板** — `--cs-paper-figure` 支持 6 种图类型：`method-overview`（方法总览）、`pipeline`（流程图）、`architecture`（架构图）、`mechanism`（机制图）、`teaser`（首图）、`comparison-schematic`（对比图）
- **会议风格适配** — `--venue` 支持 NeurIPS、ICML、ICLR、CVPR、ICCV、ECCV、ACL、EMNLP、SIGGRAPH
- **本地 Prompt 构建器** — `scripts/build_cs_paper_figure_prompt.py` 无需 API 调用即可生成结构化 prompt
- **CS 绘图工作流指南** — `references/cs-paper-figure-workflow.md` 涵盖模式选择、prompt 模式和审查清单

## 继承功能（来自上游）

- **图像模式** — 通过 Gemini `generateContent` API 生成和编辑图像
- **绘图模式** — 从数值数据精确渲染柱状图、趋势曲线、热力图、散点图
- **参考图支持** — `--input-image`（可重复）用于风格匹配生成或编辑（仅 Gemini）
- **材料科学快捷方式** — 图形摘要、机制图、器件结构图、工艺流程图

## 快速开始

### Gemini 后端（默认）

```bash
export NANOBANANA_API_KEY="你的 Gemini API Key"
export NANOBANANA_BASE_URL="https://generativelanguage.googleapis.com"

python3 scripts/generate_image.py \
  --cs-paper-figure method-overview \
  --venue neurips \
  "两阶段流程：编码器提取特征，解码器生成预测。"
```

### OpenAI 后端

```bash
export OPENAI_API_KEY="你的 OpenAI API Key"

python3 scripts/generate_image.py --backend openai \
  --cs-paper-figure architecture \
  --venue cvpr \
  --quality high \
  "ViT 架构：patch embedding、transformer encoder layers、classification head。"
```

### 其他示例

```bash
# 本地构建 prompt（无需 API 调用）
python3 scripts/build_cs_paper_figure_prompt.py \
  --cs-paper-figure architecture --venue cvpr --lang zh \
  "Backbone 提取特征，FPN 对齐尺度，head 输出 mask。"

# 从 JSON spec 渲染精确图表
python3 scripts/plot_publication_figure.py spec.json

# 用 Gemini 编辑图像
python3 scripts/generate_image.py \
  --input-image ref_style.png \
  "将图中英文标签替换为中文，其他保持不变。"
```

## 后端对比

| 功能 | Gemini | OpenAI GPT-Image |
|---|---|---|
| 生成 | 支持 | 支持 |
| 编辑（`--input-image`） | 支持 | 暂不支持 |
| 质量控制 | `--image-size` | `--quality low/medium/high` |
| 透明背景 | 不支持 | `--background transparent` |
| 输出格式 | PNG（默认） | `--output-format png/jpeg/webp` |
| 图像附带文本输出 | 支持 | 仅 `revised_prompt` |

## 目录结构

```
SKILL.md                                        # Skill 入口和工作流
scripts/
  generate_image.py                             # 主图像 CLI（Gemini + OpenAI）
  generate_image.js                             # Node.js 对等 CLI
  build_cs_paper_figure_prompt.py               # CS prompt 构建器
  build_materials_figure_prompt.py              # 材料科学 prompt 构建器
  build_plot_spec.py                            # 简洁请求 → 完整 plot spec
  plot_publication_figure.py                    # 精确绘图渲染器
references/
  api-reference.md                              # Gemini API 合约
  openai-api-reference.md                       # OpenAI API 合约
  cs-paper-figure-templates.json                # CS prompt 模板
  cs-paper-figure-workflow.md                   # CS 绘图工作流指南
  materials-science-figure-templates.json       # 材料科学模板
  publication-chart-patterns.md                 # 图表和多面板布局模式
  publication-plot-api.md                       # 绘图 API 参考
  natural-language-plot-workflow.md              # 自然语言 → plot spec 工作流
agents/                                         # Skill 侧 agent 配置
```

## 分支

- `main` — 核心图像生成 + CS 论文图支持 + 双后端（稳定）
- `dev` — 实验性栅格转 SVG 矢量化流水线

## 致谢

基于 [muxi-tk/nanobanana-image-generation](https://github.com/muxi-tk/nanobanana-image-generation) 开发。

## 许可证

MIT
