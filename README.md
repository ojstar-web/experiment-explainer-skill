# 面向读者的科研与对话 Skills

本仓库包含四个可分别安装的 Codex Skill。Skill 规定如何判断、核查和解释；脚本只负责需要时的绘图与 Markdown/PDF 制作。正文结构由任务和材料决定，不把所有回答塞进同一张填空表。

| Skill | 入口 | 用途 |
| --- | --- | --- |
| 实验讲解 | [SKILL.md](SKILL.md) | 根据已有实验材料，写供非专业读者独立阅读的项目解说 |
| 论文讲解 | [paper-reading-talk/SKILL.md](paper-reading-talk/SKILL.md) | 跟着论文讲清引言、方法、结果和图表，按需交付 Markdown/PDF |
| 从证据写论文 | [evidence-to-manuscript/SKILL.md](evidence-to-manuscript/SKILL.md) | 根据实验记录、图表、方法和文献写论文正文 |
| 读者优先的日常对话 | [reader-first-dialogue/SKILL.md](reader-first-dialogue/SKILL.md) | 解释陌生概念，回答日常问题，写清 Codex CLI 阶段汇报和最终交付 |

论文**解读**与论文**写作**是不同任务：前者跟着原文解释引言、方法、结果和图表；后者根据自己的证据形成论文论证。两者分别安装和使用；论文讲解 Skill 不替代论文正文写作。

## 三层使用方式

1. **始终适用的表达原则**放在个人或项目的 `AGENTS.md`：先回答当前问题；陌生词首次出现时用短括号解释；阶段汇报说清已完成什么、正在做什么、接下来检查什么；删套话和不影响判断的保留语。
2. **任务方法**留在各自的 Skill 中。实验讲解负责项目证据与读者理解；论文讲解负责原文覆盖与方法流向；论文写作负责论证、引用和论文语言；日常对话负责普通回答及进度表达。每个 Skill 的核心规则应独立可读，不要求先加载另一个 Skill。
3. **制作资源**只在需要相应成品时使用。根目录 `scripts/` 中的 PDF 导出和数值绘图脚本服务于实验讲解；其他 Skill 不依赖这些脚本。真正有两个以上 Skill 共用、且必须同步维护的资源，才考虑抽到公共位置。

可放进个人 `AGENTS.md` 的简短规则：

> 面向用户先说答案或实际进度。陌生词首次出现时用短括号解释。阶段汇报说清已发现或完成什么、正在做什么、接下来检查什么。删套话、假想反驳和重复保留语；影响判断的条件在相关结论处说清。专项任务仍按相应 Skill 核查事实与完成工作。

这段是安装示例，不会因克隆仓库自动生效。个人规则不要上传含本机路径、账号或项目私有信息的完整 `AGENTS.md`。

## 安装

把要使用的 Skill 分别放到 Codex 的个人 skills 目录，保证每个目录顶层有自己的 `SKILL.md`。例如：

```text
~/.codex/skills/
├── experiment-explainer/
│   ├── SKILL.md
│   └── scripts/
├── paper-reading-talk/
│   └── SKILL.md
├── evidence-to-manuscript/
│   └── SKILL.md
└── reader-first-dialogue/
    └── SKILL.md
```

可以先下载仓库，再按上述结构复制所需目录。实验讲解 Skill 对应仓库根目录的 `SKILL.md` 和 `scripts/`；另外三个 Skill 对应仓库中的同名子目录。只复制仓库根目录时，不要假设 Codex 会自动发现内部的两个 Skill。安装后重新开启会话，检查可用 Skill 列表。

## 如何调用

- “用 `$experiment-explainer`，根据这些记录和图表，写给没有参与实验的人看。”
- “用 `$paper-reading-talk`，跟着这篇论文讲，方法围绕图 1 把输入、处理和流向说清。”
- “用 `$evidence-to-manuscript`，根据这些实际结果写方法和结果章节。”
- “用 `$reader-first-dialogue`，从我不懂的前提讲起；首次出现的缩写给全称和中文解释。”

日常对话 Skill 也可通过个人 `AGENTS.md` 中的表达原则成为默认写法。用户尚未要求测试时，先解释知识，不主动改成提问练习。

## 可选制作脚本

- [scripts/render_markdown_pdf.cjs](scripts/render_markdown_pdf.cjs)：从 Markdown 导出 A4 PDF，可生成抽样页面预览。依赖 Node.js、`marked`、`playwright` 和可用的 Chromium/Edge；预览还需 Poppler。默认在线加载 MathJax，离线时用 `--mathjax` 指定本地脚本。
- [scripts/plot_series.py](scripts/plot_series.py)：从明确指定的 CSV 列生成 PNG/SVG 折线图或散点图，支持误差列。依赖 Python 和 Matplotlib；不插值、不补造缺失值。

脚本不是运行 Skill 的前提。PDF 需要查看实际页面；图的数值、单位和来源仍要核对原始材料。

## 借鉴与出处

日常对话 Skill 的写法参考了 [Anti-Defensive Writing](https://github.com/Kiterlin/anti-defensive-writing) 对必要限定语和正面陈述的处理，以及 [Stop Slop](https://github.com/hardikpandya/stop-slop) 对套话与机械句式的检查。两个来源项目均采用 MIT 许可。仓库中的中文规则按本项目的任务和读者需求编写；引用来源是为了说明借鉴关系，不代表来源项目认可本仓库。

## 维护原则

用具体材料检验 Skill 是否漏掉关键事实、解释步骤或必要格式。不要把一篇文章的章节和参数变成所有任务的固定模板。修改共用表达规则时，检查四个 Skill 中是否存在冲突；修改专项方法时，只检查受影响的任务。

本仓库采用 [MIT 许可](LICENSE)。
