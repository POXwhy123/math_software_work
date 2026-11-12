# 第 01 周成果：工具环境、学习档案与基础对象

本周练习用两个自由点构造线段、中点和圆。成果 v2 已获准发布（2026-11-12）。学习档案、素材索引、环境和问题记录可从 [本周笔记](../../02-每周笔记/第01周.md) 打开。

| 目录 | 内容 | 当前状态 |
| --- | --- | --- |
| [source](source/) | .ggb 和英文构造命令 | 已生成并重新载入验证 |
| [output](output/) | 原始图形、初始界面、拖动与磁盘重开预览 | 已生成 |
| [evidence](evidence/) | 浏览器检查、磁盘重开数据与验收说明 | 已记录实际结果与限制 |

先查看 [验收说明](evidence/验收说明.md)，或打开 [原生 .ggb](source/week01-basic-objects.ggb)。静态预览：[初始状态](output/week01-initial.png)、[拖动 A](output/week01-drag-A.png)、[拖动 B](output/week01-drag-B.png)。

用 GeoGebra 打开 .ggb 后选择移动工具，拖动蓝色 A 或 B，观察橙色中点 M、灰色线段与青色圆随之更新。初始 A=(-2,1)、B=(4,3)、M=(1,2)，圆为 (x−1)²+(y−2)²=10。源文件没有外部素材依赖。

Chrome 里的 GeoGebra Classic（API 版本 5.4.936.0）已完成端点拖动和磁盘文件重开检查。桌面版 GeoGebra 和 Obsidian 界面待核对。

在仓库根目录运行 `python tools/validate_week01.py`，可以检查 .ggb 的对象依赖和运行记录是否与文件对应。浏览器复验命令见验收说明。

[验收模板](../../07-笔记模板/验收记录模板.md) · [成果总索引](../README.md)
