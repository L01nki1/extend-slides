# extend-slides

把课程原始资料（PPT/PPTX、讲义、教材、课堂录音转写、Word、Markdown、扫描件与截图）转成**可脱离原资料独立复习**的中文扩展讲解文档。

特点：**只增不删、保留原脉络**。

对于不同学科类型提供四种讲解模式（计算与证明 / 例题 / 理论与推理 / 应用），只调整侧重，不降低覆盖度要求。

本项目更适配理工科学生学习，其他学科暂未测试，欢迎各学科专业同学尝试。如果需要联系我，请email至loinkii@foxmail.com

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
    ├── render_pdf_images.py          # PDF 逐页转图片
    └── sync.ps1                      # 同步安装到个人级 / 项目级
```

---

## 安装

### 方式一：用同步脚本（推荐）

```powershell
# 安装到个人级 skills 目录（自动探测 .copilot / .workbuddy / .agents / .claude）
powershell -ExecutionPolicy Bypass -File .\scripts\sync.ps1 -Scope personal

# 安装到某个项目的 .github\skills
powershell -ExecutionPolicy Bypass -File .\scripts\sync.ps1 -Scope project -ProjectPath D:\MyCourse

# 两处都装
powershell -ExecutionPolicy Bypass -File .\scripts\sync.ps1 -Scope both -ProjectPath D:\MyCourse

# 手动指定个人级 skills 根目录
powershell -ExecutionPolicy Bypass -File .\scripts\sync.ps1 -Scope personal -PersonalRoot "$env:USERPROFILE\.workbuddy\skills"
```

> **为什么要加 `-ExecutionPolicy Bypass`**：Windows PowerShell 5.1 默认禁止运行 `.ps1` 脚本。这种方式只对本次进程生效，**不需要修改系统策略、也不需要管理员权限**。
>
> **为什么脚本里是英文提示**：Windows PowerShell 5.1 在没有 UTF-8 BOM 时按系统 ANSI 代码页读取 `.ps1`，中文会乱码并**直接导致语法解析失败**。因此 `sync.ps1` 刻意保持纯 ASCII，请勿在其中加入中文。

脚本会做三件事：

1. 校验文件夹名与 `SKILL.md` 中的 `name` 是否一致（不一致会导致 skill 无法被发现）。
2. 用 `robocopy /MIR` 镜像同步（排除 `.git`、`.venv`、`venv`、`.vscode`、`node_modules`、`__pycache__`、各类缓存目录、`*.log`、`*.pyc`）。
3. 打印目标路径，并提示重载 VS Code。

> 目标目录已存在但不是有效 skill 目录时，脚本会跳过并警告；确认要覆盖时加 `-Force`。

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

---

## 依赖

全部可选，缺失时不阻断流程。其中 **OCR 是唯一会在流程开始时主动询问的能力** —— 若未检测到，技能会先告知你「纯图片素材可能被跳过」，并给出安装指令，由你选择现在装还是继续；其余能力缺失时降级为「提示你人工导出」。

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

在 Copilot Chat 中输入 `/extend-slides`，或直接描述需求（如「帮我把这份 PPT 扩展成复习笔记」）触发。

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
- **跨会话记忆**：skill 本身不记忆，靠课程目录下的 `_课程档案.md` 落盘。
- **格式优先级**：Markdown 原生写法优先（段落、列表、表格、行内代码）。公式**默认不用 LaTeX**，只有分式、根式、矩阵这类确实无法原生表达时才用 `$...$`；图表用 Mermaid。
- **原文与讲解的区分**：原文直接呈现、**不加引用块**（引用块会破坏表格渲染）；AI 生成的讲解统一用 `==...==` 包裹。
- **关于 `==` 高亮**：Obsidian 会正常渲染成高亮，VS Code 与 GitHub 的 Markdown 预览不会。本 skill 面向 Obsidian 使用，故采用该标记。

---

## 许可证

[MIT](./LICENSE)
