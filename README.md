# extend-slides

把课程原始资料（PPT/PPTX、讲义、教材、课堂录音转写、Word、Markdown、扫描件与截图）转成**可脱离原资料独立复习**的中文扩展讲解文档。

特点：**只增不删、保留原脉络**。

对于不同学科类型提供四种讲解模式（计算与证明 / 例题 / 理论与推理 / 应用），只调整侧重，不降低覆盖度要求。

本项目更适配理工科学生学习，其他学科暂未测试，欢迎各学科专业同学尝试。如果需要联系我，请email至loinkii@foxmail.com

---

本项目已收录至CityUHub
[![CityU Hub](https://cityu-hub.bond/badge/l01nki1-extend-slides.svg)](https://cityu-hub.bond/project/l01nki1-extend-slides)

---
## 目录结构

本仓库根目录就是 skill 本体

```text
extend-slides/
├── SKILL.md                          # 主文件：何时用、流程、模式判定、硬性约束、检查清单
├── README.md                         # 本文件
├── LICENSE                           # MIT
├── references/                       # 按需加载的规则细节
│   ├── modes.md                      # 四种模式的写法、侧重与追加小节
│   ├── inputs.md                     # 输入格式白名单、能力探测、降级与导出指引
│   └── output-format.md              # 原文与讲解标记、Markdown 原生格式、Mermaid、来源表、图片、语言处理
├── assets/                           # 直接套用的模板
│   ├── chapter-template.md           # 单章输出骨架
│   ├── course-profile-template.md    # 课程档案（跨会话记忆）
│   └── overview-template.md          # 课程总览
└── scripts/
    ├── probe_env.py                  # 环境能力探测
    ├── extract_pptx.py               # PPTX 文字与图片抽取
    └── render_pdf_images.py          # PDF 逐页转图片
```

---

## 安装

### 方式一：让AI帮助你
告诉AI：为我安装https://github.com/L01nki1/extend-slides 这个skill

### 方式二：手动复制

把整个 `extend-slides` 文件夹复制到下列任一位置：

| 范围 | 路径 |
| --- | --- |
| 个人级 | `~/.copilot/skills/`、`~/.agents/skills/`、`~/.claude/skills/`（或你本机实际使用的 skills 根目录） |
| 项目级 | `<项目根>/.github/skills/`、`<项目根>/.agents/skills/`、`<项目根>/.claude/skills/` |

**文件夹名必须是 `extend-slides`**，否则不会被加载。

### 方式三：从 GitHub 获取

**推荐：`git clone`**，克隆出来的文件夹名天然正确。

```powershell
git clone https://github.com/<你的用户名>/extend-slides.git "$env:USERPROFILE\.copilot\skills\extend-slides"
```

**注意：不要直接解压 GitHub 网页上的 "Download ZIP"。** 那个包解压出来的文件夹名会带分支后缀（如 `extend-slides-main`），而 skill 加载要求文件夹名与 `SKILL.md` 中的 `name` 严格一致，**必须先重命名为 `extend-slides`** 再放入 skills 目录。

（当然如果你想自己改也可以）


---

## 依赖

全部可选，缺失时不阻断流程。其中 **OCR 是唯一会在流程开始时主动询问的能力** —— 若未检测到，技能会先告知你「纯图片素材可能被跳过」，并给出安装指令，由你选择现在装还是继续；其余能力缺失时会提示你人工导出。

```powershell
pip install python-pptx     # 抽取 PPTX 文字与图片
pip install pymupdf         # PDF 转图片（poppler 的替代方案）
```

外部命令（可选）：`soffice`（LibreOffice）、`pdftoppm`（poppler）、`tesseract`（OCR）。

先探测本机能力：

```powershell
python scripts/probe_env.py
python scripts/probe_env.py --json   # 机器可读
```

---

## 使用

在你的agent中输入 `/extend-slides`，或直接描述需求（如「使用/extend-slides 这个skill，为我生成这个课程讲义扩展讲解。输出到D:/your_project_name这个文件夹中」）触发。

首次使用会问三件事：**课程名、输出位置、模式偏好**。之后的回答写入课程目录的 `_课程档案.md`，同一门课后续章节自动沿用模式，不再重复询问。

产出：

```text
<课程输出目录>/
├── _课程档案.md                 # 课程名、模式、材料清单、进度
├── 00-课程总览.md               # 章节索引 + 术语总表 + 学习顺序 + 覆盖度报告
├── 01-<章节名>-课件扩展讲解.md
├── 02-<章节名>-课件扩展讲解.md
└── assets/                      # 从原资料提取的图片与图表
```

---

## 脚本用法

```powershell
# 抽取 PPTX（默认只抽文字与备注，不导出图片）
python scripts/extract_pptx.py .\03-神经网络.pptx .\神经网络课程\

# 确需保留某张图时才加 --images
python scripts/extract_pptx.py .\03-神经网络.pptx .\神经网络课程\ --images

# PDF 转图片（默认 150 dpi）
python scripts/render_pdf_images.py .\lecture03.pdf .\神经网络课程\ --dpi 200
```

`extract_pptx.py` 会在抽取结果里显式标注**纯图片页**（无可提取文字），并列出页码，方便按约定跳过、并计入交付报告的存疑条目。

---

## 安装后验证

1. 执行 `Developer: Reload Window`。
2. 在 Chat 输入 `/`，确认列表中出现 `extend-slides`。
3. 在对话中用中文说「帮我把这份 PPT 扩展成复习笔记」，确认能自动触发。
4. 运行 `python scripts/probe_env.py`，确认探测结果符合预期。
5. 拿一份真实课件跑一遍完整流程，检查：文件命名、`_课程档案.md` 生成、材料来源表、中英术语表、覆盖度报告。
6. 预览输出文件，确认图表（Mermaid）正常渲染，AI 讲解已用 `==...==` 包裹，且正文里没有 `>` 引用块包裹原文。

---

## 设计要点

- **只增不删**：原资料每个标题、每个知识点都要在输出中有落点，交付前用检查清单逐项核对。唯一例外是无 OCR 时的纯图片页。
- **章级可溯**：正文不逐段标注来源；每章用「材料来源」表统一记录「小节 → 文件 / 页码」。
- **不臆造考点**：没有往年题或教师说明时，只能写「基于本页内容的考点推断」。
- **跨会话记忆**：skill 本身不记忆，靠课程目录下的 `_课程档案.md` 实现跨项目记忆。
- **格式优先级**：Markdown 原生写法优先（段落、列表、表格、行内代码）。公式**默认不用 LaTeX**，只有分式、根式、矩阵这类确实无法原生表达时才用 `$...$`；图表用 Mermaid。
- **原文与讲解的区分**：原文直接呈现、**不加引用块**（引用块会破坏表格渲染）；AI 生成的讲解统一用 `==...==` 包裹。
- **关于 `==` 高亮**：Obsidian 会正常渲染成高亮，VS Code 与 GitHub 的 Markdown 预览不会。是否能够正常渲染就看你使用什么把markdown转成PDF了。

---
## 碎碎念和Q&A
- *为什么做这个*：在CS6480的课上被老师纯AI生成的PPT和难绷的口音气晕过去了，一气之下做此skill。
- *最适合什么学生*：在境外读理科和新工科的同学，尤其是来自**CityUHK的计算学院**的master同学。
- *觉得不好用还不会改的话怎么办*：通过最上面的邮件联系我，用最直白最不绕弯子的语言说出你的改进建议或者需求。
- *README好难看*：对不起这个写的时候用了一下AI，，
- *token消耗的多吗*：看你喂进去什么文件了，越接近纯文本token消耗的越少，不过总体的话可以接受，可以去workbuddy使用免费额度，如果课程内容适中的话100credits可以完整生成一个12周的课程。如果全是图片需要OCR的话会很慢。速度参考CS5351三周课件六七百页且有大量图片，共花费90分钟左右，最后生成PDF800页，deepseekv4.1flash消耗125.97credits。
---

## 许可证

[MIT](./LICENSE)
