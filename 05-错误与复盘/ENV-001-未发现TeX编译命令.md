# ENV-001：未发现本地 TeX 编译命令

- 发现日期：2026-11-12。
- 状态：待确认安装位置，尚未复验编译。
- 关联：[环境报告](../01-课程计划/本地环境检查.md)、[LaTeX 专题](../03-专题知识/LaTeX.md)。

## 触发与现象

在仓库 PowerShell 执行 `Get-Command xelatex,pdflatex,lualatex,latexmk,biber,bibtex -ErrorAction SilentlyContinue`，未返回上述命令。随后检查卸载注册表、常见安装目录及 C、D、E 盘根目录，未发现 TeX Live 或 MiKTeX。

## 原因判断

TeX 可能还没装，也可能装在自定义目录里，当前 PowerShell 的 PATH 找不到它。

## 处理与复验

先查有没有自定义安装目录。找到后在新开的 PowerShell 里重跑命令检查。编译复验用一份最小中文文档和一份带参考文献的 SWUThesis 示例，保留源码、PDF 和日志。
