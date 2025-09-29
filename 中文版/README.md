# Tutor 课程记录与财务系统

一个用于私人家教/培训老师记录每节课信息并自动汇总财务数据的命令行小工具。数据保存在本地 `teaching_records.csv`，开箱即用，无需数据库。若安装了 `rich` 库，会以美观的表格显示；否则自动回退为对齐良好的纯文本表格（内置 CJK 宽字符感知对齐）。

## 功能特性
- 添加新课程记录（自动计算本节收入）
- 查询课程记录（按学生姓名、学生ID、课程主题、月份 YYYY-MM 组合筛选）
- 查看所有学生（统计每位学生的课程数量）
- 查看财务摘要（总课程数、总时长、总收入）
- 查看月度汇总（每月课程数、总时长、总收入）
- 首次运行或旧数据自动补齐 `month` 字段（一次性无损迁移）

## 目录结构
- `main.py`: 命令行入口与交互逻辑
- `database_manager.py`: 读写 CSV、数据查询与聚合、字段迁移
- `models.py`: 数据模型 `TeachingRecord`
- `teaching_records.csv`: 运行后自动生成的数据文件

## 环境要求
- Python 3.8+
- 可选：`rich`（用于彩色表格与更佳的终端展示）

安装可选依赖：
```bash
pip install rich
```

## 快速开始
1) 将项目下载到本地（或直接将三份 `.py` 文件放在同一目录）
2) 可选：创建虚拟环境并激活
```bash
python -m venv .venv
# Windows PowerShell
. .venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate
```
3) 运行程序
```bash
python main.py
```
首次运行会自动在当前目录生成/修复 `teaching_records.csv`。

## 使用指南
启动后，主菜单包含以下操作：
1. 添加新课程记录
2. 查询课程记录
3. 查看所有学生
4. 查看财务摘要
5. 查看月度汇总
6. 退出系统

### 1. 添加新课程记录
- 自动提示已存在的学生名单，便于复用学生ID
- 输入：学生姓名、学生ID、日期(默认今日)、课程时长(分钟)、每小时价格、课程主题、作业、学生表现(1-10)、备注、下节课计划
- 系统会自动计算本节 `total_income`

### 2. 查询课程记录
- 支持按学生姓名、学生ID、课程主题、月份(YYYY-MM)任意组合筛选
- 结果逐条展示，并显示学生表现的表情提示（如 🌟/👍/😐/💪）

### 3. 查看所有学生
- 显示所有学生的姓名、ID 与课程数量
- 若安装 `rich`：以彩色表格显示
- 未安装 `rich`：使用中日韩宽字符感知的对齐算法，纯文本也整齐

### 4. 查看财务摘要
- 汇总总课程数、总授课时长(小时)与总收入(元)

### 5. 查看月度汇总
- 按 `YYYY-MM` 分组，统计每月课程数、总时长与总收入
- 支持表格美观展示或纯文本对齐展示

## 数据文件与字段
数据文件默认为当前目录下的 `teaching_records.csv`，字段如下：
- `student_name`：学生姓名 (str)
- `student_id`：学生ID (str)
- `date`：上课日期 (YYYY-MM-DD)
- `month`：月份 (YYYY-MM)，由系统从 `date` 自动推导
- `duration_minutes`：课程时长(分钟) (int)
- `hourly_rate`：小时费率(元) (float)
- `total_income`：本节课收入(元) (float，系统自动计算)
- `topic_covered`：课程主题 (str)
- `homework_assigned`：布置的作业 (str)
- `student_performance`：学生表现评分 1-10 (int)
- `notes`：备注/笔记 (str)
- `next_plan`：下节课计划 (str)

说明：程序会在初始化时检查并迁移旧 CSV，补写缺失的 `month` 字段，原数据不丢失。

## 常见问题 (FAQ)
- Q: 没安装 `rich`，显示会很丑吗？
  - A: 不会。程序内置了 CJK 宽字符感知的文本对齐，纯文本也整齐可读。
- Q: CSV 已存在但缺少 `month` 字段怎么办？
  - A: 程序会自动进行一次性迁移，从 `date` 推导出 `YYYY-MM` 并补齐。
- Q: 输入了非数字的时长或价格会怎样？
  - A: 程序会进行校验并提示重新输入，不会写入非法数据。
- Q: 我可以把数据拿去做别的统计吗？
  - A: 可以，`teaching_records.csv` 是通用 CSV，可直接用表格软件或 Python 处理。

## 备份与同步
- 直接复制备份 `teaching_records.csv` 即可；建议定期备份
- 若使用云盘或版本控制，请确保 CSV 不被并发同时写入

## 贡献与改进
欢迎提出建议或提交改进：如新的筛选条件、更详尽的报表、导出为 Excel 等。

## 许可证
MIT License
