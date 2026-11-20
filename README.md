# experiment-explainer

面向非专业读者，把已有实验材料整理成**可独立阅读的完整项目解说**，并按需要提供有用的现场讲解备注。这是一个用于 Codex 的指令型 Skill，入口为 [`SKILL.md`](SKILL.md)，无需安装额外依赖。

## 解决什么问题

实验完成后，记录、代码和图表通常回答了“做了什么”，却未必能让外行理解“为什么这样做、结果说明什么”。本 Skill 引导 Codex：

- 按项目类型核对研究对象、关键选择、实际实施和结果来源；
- 区分观察、解释、假设、失败和未核实内容；
- 在首次使用术语或结果前补足读者需要的前提；
- 解释对照、基线、数值和图表各自代表什么；
- 按证据支持的范围说明结论，并写出不重复正文的讲解提示。

适用于计算实验、实验室实验、田野研究、用户研究及其他有可核查材料的实证项目。不同项目只核对与其结论相关的材料；不会要求所有项目具备代码、模型权重、数值基线或图表。

## 安装

将本仓库作为 `experiment-explainer` 文件夹放入 Codex 的个人 skills 目录，使路径形如：

```text
~/.codex/skills/experiment-explainer/SKILL.md
```

例如，已安装 Git 时：

```bash
git clone https://github.com/ojstar-web/experiment-explainer-skill.git ~/.codex/skills/experiment-explainer
```

Windows PowerShell 可用：

```powershell
git clone https://github.com/ojstar-web/experiment-explainer-skill.git "$HOME/.codex/skills/experiment-explainer"
```

也可以下载仓库并手动复制文件夹。目录中必须保留 `SKILL.md`；README 和 LICENSE 可一并保留。重新开启 Codex 会话后，检查 Skill 是否出现在可用 skills 列表中。

## 调用

在 Codex 中直接说“用 `$experiment-explainer`，根据这些实验记录写一份给非专业读者的完整项目解说”，并给出项目材料位置、时间范围、听众背景和期望格式。也可以让 Codex 在适合的任务中自行选择本 Skill。一个较具体的请求：

> 用 `$experiment-explainer` 梳理 10 月的实验。先核对记录、配置与结果；正文要让我没有专业背景的同事读懂为什么做、怎样做、实际发现了什么。把未核实的结论标出来，并附少量真正有助于现场讲述的备注。

如果只有部分材料，可要求它交付**范围明确**的解说，并列出会改变结论的缺口；不要让它填造未做的实验。

## 工作方式与边界

Skill 的核心检查是：**读者前提、主张与证据、表图语义、叙事依赖**。它负责把已经存在的证据转为清楚的说明，不会自动执行实验、统计推断、论文审稿、训练或发布。需要这些工作时应另行授权并使用相应方法。对远程或受限项目，还须遵守项目自身的访问规则。

项目中的具体案例只用于检验 Skill 是否漏掉通用问题，不能作为其他领域的固定模板。即使 Skill 的格式检查通过，也不能据此声称它在每个领域都能稳定产出高质量文稿；实际使用仍需核对事实与读者可理解性。

## 验证与维护

本仓库的 `SKILL.md` 已使用 Codex `skill-creator` 的 `quick_validate.py` 做格式检查。我们还用一个计算科研文稿作了迭代样例，并由独立模型审查规则覆盖与一致性。**尚未完成跨领域、盲测式的生成质量评估**；欢迎提交具有可核查输入、预期读者问题和实际输出的 issue 或 PR。

关于 Skill 的通用结构和发现方式，可参阅 [OpenAI Skills 文档](https://developers.openai.com/api/docs/guides/tools-skills)。

## 通用对话 Skill

仓库另含 [`reader-first-dialogue/SKILL.md`](reader-first-dialogue/SKILL.md)。它把“先回答当前疑问、术语就地解释、事实与推断分开”的表达方式用于日常中文对话和学习答疑，不要求普通聊天套用实验报告结构。可单独安装到 `~/.codex/skills/reader-first-dialogue/`。需要论文读稿或完整实验报告时，仍使用相应的专项 Skill。

## 许可

MIT，见 [LICENSE](LICENSE)。

## 可选制作脚本

仓库的 `scripts/` 包含两种按需使用的工具：

- `render_markdown_pdf.cjs`：从一份 Markdown 导出 A4 PDF，并可用 `--preview-dir` 生成首、中、末页预览。依赖 Node.js、`marked`、`playwright`、可用的 Chromium/Edge；预览还需 Poppler 的 `pdfinfo` 和 `pdftoppm`。默认从 jsDelivr 加载 MathJax；离线使用时用 `--mathjax` 指定本地脚本。
- `plot_series.py`：从明确指定的 CSV 数值列生成 PNG/SVG 折线图或散点图，支持误差列。依赖 Python 和 Matplotlib；不插值、不补造缺失值。

示例：

```bash
npm install marked playwright
node scripts/render_markdown_pdf.cjs report.md report.pdf --preview-dir preview
python scripts/plot_series.py --csv results.csv --x time --y value --output result.png --xlabel "Time (ps)" --ylabel "Value"
```

这些脚本不是运行 Skill 的前提。PDF 的预览仍须人工检查，图的来源和单位仍须按原始材料核对。

`reader-first-dialogue/` 是独立的日常对话 Skill：需要时单独复制到个人 skills 目录。它要求遇到陌生词时就地用括号解释，用户听不懂时补齐前提，并把必要的不确定性说具体，避免堆叠保留语。

## 从实验资料写论文

[evidence-to-manuscript/](evidence-to-manuscript/SKILL.md) 是独立的论文写作 Skill。它把实验记录、图表与真实文献组织成引言、方法、结果、讨论等论文正文；证据核查留在写作底稿，正文采用直接、具体的论文语言。该 Skill 与实验解说和日常对话 Skill 分别使用，需要时可单独复制到个人或项目 skills 目录。
