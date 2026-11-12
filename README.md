# 数学软件课程学习档案

这里存放第 1–11 周的数学软件课程笔记和作业。[第 1 周成果 v2](06-课程成果/第01周/evidence/验收说明.md) 已获准发布，其余周尚未开始。课程范围见 [总任务 Issue #1](https://github.com/POXwhy123/math_software_work/issues/1)，截止日期以教师安排为准。

在 Obsidian 中选择“打开本地仓库”，打开**包含本 README 和 .git 的内层 math_software_work 文件夹**。进入 [课程主页](00-首页.md)，按链接查看周笔记与成果。Obsidian 与 Git 共用这一套文件，无需复制笔记。

| 路径 | 用途 |
| --- | --- |
| [课程主页](00-首页.md) | 周次进度与入口 |
| [课程计划](01-课程计划/第01-11周任务与验收清单.md) | 每周最低提交物及验收条件 |
| [个人学习档案](01-课程计划/个人学习档案.md) | 个人资料、暂定选题、素材索引 |
| [环境检查](01-课程计划/本地环境检查.md) | 已发现的软件、缺口及复验步骤 |
| 02-每周笔记/ | 11 周笔记，含过程、数学解释及验收状态 |
| 03-专题知识/ | GeoGebra、Mathematica、LaTeX 专题入口 |
| [案例索引](04-案例卡/README.md) | 实验案例卡 |
| [问题索引](05-错误与复盘/README.md) | 真实环境问题及后续错误记录 |
| [成果索引](06-课程成果/README.md) | 按周组织 source、output、evidence |
| [笔记模板](07-笔记模板/README.md) | 每周笔记、案例卡、错误、验收模板 |
| tools/ | Python 标准库自检脚本及环境探针 |

在本目录的 PowerShell 中运行：

```powershell
python tools/check_structure.py
python tools/check_environment.py --network
```

第一条检查目录、Obsidian 配置及本地文件链接；第二条记录软件和网络状态，结果写入忽略上传的 `.local/checks/`。环境脚本返回 2 表示核心命令缺失，详情见报告；返回 0 也仅表示命令已发现，不代表 GUI、许可或作业运行通过。不需要额外安装 Python 包。

实际作业放入对应周的 `source/`，导出的 PDF、图像或表格放入 `output/`，运行命令、版本、日志和验收记录放入 `evidence/`。各周 README 记录实际运行方式。第 1 周 .ggb 已在 GeoGebra Classic 网页版完成构造、拖动、导出与磁盘重载检查；桌面版及 Obsidian GUI 仍待人工验证。

GeoGebra 须打开 `.ggb` 并做拖动检查；Mathematica 须打开 `.nb` 并在新内核运行；第 10 周须保留 TeXbrain 的源码、PDF 与真实编译记录；第 11 周按固定版本 SWUThesis 的说明验证编译链。具体入口见 [环境检查](01-课程计划/本地环境检查.md)。

每周先在本地交付源文件、输出、笔记、预览、文件清单、自检结果和未解决问题。只有本人明确批准该周该版本后才能上传、push、创建包含成果的远程 PR 或发布。自检不代替本人验收。第 1 周 v2 的发布记录见验收说明。
