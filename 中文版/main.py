# main.py
from datetime import datetime
from database_manager import DatabaseManager
from models import TeachingRecord
import unicodedata

try:
    from rich.console import Console
    from rich.table import Table
    RICH_AVAILABLE = True
except Exception:
    RICH_AVAILABLE = False

def _visual_len(s: str) -> int:
    l = 0
    for ch in str(s):
        l += 2 if unicodedata.east_asian_width(ch) in ('W', 'F') else 1
    return l

def _pad_right(s: str, width: int) -> str:
    s = str(s)
    vlen = _visual_len(s)
    return s + ' ' * max(0, width - vlen)

def _print_students_plain_table(students_data: dict, student_lesson_count: dict):
    rows = []
    for i, (name, sid) in enumerate(students_data.items(), 1):
        rows.append((str(i), name, sid, f"{student_lesson_count.get(name, 0)}节"))

    headers = ("序号", "学生姓名", "学生ID", "课程数量")
    widths = [0, 0, 0, 0]
    for idx, h in enumerate(headers):
        widths[idx] = max(widths[idx], _visual_len(h))
    for r in rows:
        for idx, cell in enumerate(r):
            widths[idx] = max(widths[idx], _visual_len(cell))

    header_line = "  ".join(_pad_right(h, widths[i]) for i, h in enumerate(headers))
    print("\n--- 所有学生列表 ---")
    print(header_line)
    print("-" * max(45, len(header_line)))
    for r in rows:
        print("  ".join(_pad_right(r[i], widths[i]) for i in range(4)))

def _print_monthly_plain_table(summary: dict):
    headers = ("月份", "课程数", "总时长(小时)", "总收入(¥)")
    rows = []
    for m, stats in summary.items():
        rows.append((str(m), str(stats.get('lessons', 0)), f"{stats.get('hours', 0.0):.2f}", f"{stats.get('income', 0.0):.2f}"))

    widths = [0, 0, 0, 0]
    for idx, h in enumerate(headers):
        widths[idx] = max(widths[idx], _visual_len(h))
    for r in rows:
        for idx, cell in enumerate(r):
            widths[idx] = max(widths[idx], _visual_len(cell))

    header_line = "  ".join(_pad_right(h, widths[i]) for i, h in enumerate(headers))
    print("\n--- 月度汇总 ---")
    print(header_line)
    print("-" * max(45, len(header_line)))
    for r in rows:
        print("  ".join(_pad_right(r[i], widths[i]) for i in range(4)))

def get_performance_emoji(score: int) -> str:
    """根据评分返回对应的表情符号"""
    if score >= 9:
        return "🌟"  # 优秀
    elif score >= 7:
        return "👍"  # 良好
    elif score >= 5:
        return "😐"  # 一般
    else:
        return "💪"  # 需努力

def add_new_record(db: DatabaseManager):
    print("\n--- 添加新课程记录 ---")
    
    # 先获取所有现有学生，用于提示
    existing_students = db.get_all_student_names_ids()
    if existing_students:
        print("\n现有学生列表:")
        for i, (name, sid) in enumerate(existing_students.items(), 1):
            print(f"  {i}. {name} (ID: {sid})")
        print()
    
    student_name = input("学生姓名: ").strip()
    
    # 检查是否已存在该学生
    existing_id = db.get_student_id_by_name(student_name)
    
    if existing_id:
        print(f"✅ 找到现有学生: {student_name} (ID: {existing_id})")
        use_existing = input("使用这个学生ID? (y/n, 回车默认使用): ").strip().lower()
        if use_existing in ['', 'y', 'yes', '是']:
            student_id = existing_id
            print(f"✅ 使用现有ID: {student_id}")
        else:
            student_id = input("请输入新的学生ID: ").strip()
    else:
        print(f"🆕 新学生: {student_name}")
        student_id = input("请输入学生ID: ").strip()
    
    # 日期输入处理
    while True:
        date_str = input("课程日期 (YYYY-MM-DD，回车默认为今天): ").strip()
        if not date_str:
            course_date = datetime.now().date()
            break
        try:
            course_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            break
        except ValueError:
            print("日期格式错误，请按 YYYY-MM-DD 格式输入。")

    # 课程时长输入
    while True:
        try:
            duration = int(input("课程时长（分钟）: "))
            if duration > 0:
                break
            else:
                print("时长必须大于0")
        except ValueError:
            print("请输入有效的数字")

    # 输入每小时价格
    while True:
        try:
            hourly_rate = float(input("每小时价格（元）: "))
            if hourly_rate > 0:
                break
            else:
                print("价格必须大于0")
        except ValueError:
            print("请输入有效的数字")

    topic = input("课程主题: ").strip()
    homework = input("布置的作业: ").strip()
    
    # 学生表现输入
    while True:
        try:
            performance_input = input("学生表现 (1-10分): ")
            performance = int(performance_input)
            if 1 <= performance <= 10:
                break
            else:
                print("请输入1-10之间的整数")
        except ValueError:
            print("请输入有效的整数(1-10)")

    notes = input("备注/笔记: ").strip()
    next_plan = input("下节课计划: ").strip()

    new_record = TeachingRecord(
        student_name=student_name,
        student_id=student_id,
        date=course_date,
        duration_minutes=duration,
        hourly_rate=hourly_rate,
        total_income=0.0,
        topic_covered=topic,
        homework_assigned=homework,
        student_performance=performance,
        notes=notes,
        next_plan=next_plan
    )

    db.add_record(new_record)

def query_records(db: DatabaseManager):
    print("\n--- 查询课程记录 ---")
    existing_students = db.get_all_student_names_ids()

    # 优先提供学生快速选择，并在最后提供“自定义筛选”
    selected_name = None
    selected_sid = None
    topic = None
    month = None

    if existing_students:
        print("\n学生列表（请选择序号）：")
        items = list(existing_students.items())
        for i, (n, s) in enumerate(items, 1):
            print(f"  {i}. {n} (ID: {s})")
        print(f"  {len(items)+1}. 自定义筛选")

        while True:
            choice = input(f"请输入序号 (1-{len(items)+1}): ").strip()
            if not choice.isdigit():
                print("请输入有效的数字序号。")
                continue
            idx = int(choice)
            if 1 <= idx <= len(items):
                selected_name, selected_sid = items[idx-1]
                break
            elif idx == len(items) + 1:
                break
            else:
                print("超出范围，请重新输入。")

        # 选择了具体学生后，仅再询问主题与月份
        if selected_name:
            topic = input("按课程主题查询（回车跳过）: ") or None
            month = input("按月份查询 (YYYY-MM，回车跳过): ") or None
        else:
            # 自定义筛选
            print("提示：可以按任意条件组合查询，直接回车跳过。")
            selected_name = input("按学生姓名查询: ") or None
            selected_sid = input("按学生ID查询: ") or None
            topic = input("按课程主题查询: ") or None
            month = input("按月份查询 (YYYY-MM，回车跳过): ") or None
    else:
        # 没有学生数据则走原有输入流程
        print("提示：可以按任意条件组合查询，直接回车跳过。")
        selected_name = input("按学生姓名查询: ") or None
        selected_sid = input("按学生ID查询: ") or None
        topic = input("按课程主题查询: ") or None
        month = input("按月份查询 (YYYY-MM，回车跳过): ") or None

    try:
        records = db.query_records(student_name=selected_name, student_id=selected_sid, topic=topic, month=month)

        if not records:
            print("未找到匹配的记录。")
            return

        print(f"\n找到了 {len(records)} 条记录:")
        print("-" * 90)
        for i, record in enumerate(records, 1):
            # 添加表情符号让评分更直观
            performance_emoji = get_performance_emoji(record.student_performance)
            
            print(f"记录 #{i}")
            print(f"  学生: {record.student_name} ({record.student_id})")
            print(f"  日期: {record.date}， 时长: {record.duration_minutes} 分钟")
            try:
                print(f"  月份: {getattr(record, 'month', '')}")
            except Exception:
                pass
            print(f"  费率: ¥{record.hourly_rate}/小时， 收入: ¥{record.total_income}")
            print(f"  主题: {record.topic_covered}")
            print(f"  作业: {record.homework_assigned}")
            print(f"  表现: {record.student_performance}/10 {performance_emoji}")
            print(f"  笔记: {record.notes}")
            print(f"  计划: {record.next_plan}")
            print("-" * 90)
    except Exception as e:
        print(f"查询过程中出错: {e}")
        print("请检查数据文件是否完整。")

def show_all_students(db: DatabaseManager):
    """显示所有学生及其课程统计"""
    students_data = db.get_all_student_names_ids()
    if not students_data:
        print("尚未录入任何学生。")
        return

    # 统计每个学生的课程数量
    student_lesson_count = {}
    records = db.query_records()
    for record in records:
        student_lesson_count[record.student_name] = student_lesson_count.get(record.student_name, 0) + 1

    if RICH_AVAILABLE:
        console = Console()
        table = Table(show_header=True, header_style="bold")
        table.add_column("序号", justify="right", width=4, no_wrap=True)
        table.add_column("学生姓名", justify="left")
        table.add_column("学生ID", justify="left")
        table.add_column("课程数量", justify="right", width=8, no_wrap=True)

        for i, (name, sid) in enumerate(students_data.items(), 1):
            lesson_count = student_lesson_count.get(name, 0)
            table.add_row(str(i), name, sid, f"{lesson_count}节")

        console.print(table)
    else:
        _print_students_plain_table(students_data, student_lesson_count)

def show_financial_summary(db: DatabaseManager):
    """显示财务摘要"""
    summary = db.get_financial_summary()
    print("\n--- 财务摘要 ---")
    print(f"总课程数: {summary['total_lessons']} 节")
    print(f"总授课时长: {summary['total_hours']} 小时")
    print(f"总收入: ¥{summary['total_income']}")

def show_monthly_summary(db: DatabaseManager):
    """显示按月份的课程汇总"""
    summary = db.get_monthly_summary()
    if not summary:
        print("暂无数据。")
        return
    if RICH_AVAILABLE:
        console = Console()
        table = Table(show_header=True, header_style="bold")
        table.add_column("月份", justify="left", no_wrap=True)
        table.add_column("课程数", justify="right", width=8, no_wrap=True)
        table.add_column("总时长(小时)", justify="right", width=12, no_wrap=True)
        table.add_column("总收入(¥)", justify="right", width=10, no_wrap=True)

        for m, stats in summary.items():
            table.add_row(str(m), str(stats.get('lessons', 0)), f"{stats.get('hours', 0.0):.2f}", f"{stats.get('income', 0.0):.2f}")

        console.print(table)
    else:
        _print_monthly_plain_table(summary)

def main():
    db = DatabaseManager()
    print("=== Tutor 课程记录与财务系统 ===")

    while True:
        print("\n请选择操作：")
        print("1. 添加新课程记录")
        print("2. 查询课程记录")
        print("3. 查看所有学生")
        print("4. 查看财务摘要")
        print("5. 查看月度汇总")
        print("6. 退出系统")

        choice = input("请输入选项 (1/2/3/4/5/6): ").strip()

        if choice == '1':
            add_new_record(db)
        elif choice == '2':
            query_records(db)
        elif choice == '3':
            show_all_students(db)
        elif choice == '4':
            show_financial_summary(db)
        elif choice == '5':
            show_monthly_summary(db)
        elif choice == '6':
            print("感谢使用，再见！")
            break
        else:
            print("无效选项，请重新输入。")

if __name__ == "__main__":
    main()