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
        rows.append((str(i), name, sid, f"{student_lesson_count.get(name, 0)} lessons"))

    headers = ("No.", "Student Name", "Student ID", "Lessons")
    widths = [0, 0, 0, 0]
    for idx, h in enumerate(headers):
        widths[idx] = max(widths[idx], _visual_len(h))
    for r in rows:
        for idx, cell in enumerate(r):
            widths[idx] = max(widths[idx], _visual_len(cell))

    header_line = "  ".join(_pad_right(h, widths[i]) for i, h in enumerate(headers))
    print("\n--- All Students ---")
    print(header_line)
    print("-" * max(45, len(header_line)))
    for r in rows:
        print("  ".join(_pad_right(r[i], widths[i]) for i in range(4)))

def _print_monthly_plain_table(summary: dict):
    headers = ("Month", "Lessons", "Total Hours", "Total Income ($)")
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
    print("\n--- Monthly Summary ---")
    print(header_line)
    print("-" * max(45, len(header_line)))
    for r in rows:
        print("  ".join(_pad_right(r[i], widths[i]) for i in range(4)))

def get_performance_emoji(score: int) -> str:
    """Return an emoji representation for the given performance score."""
    if score >= 9:
        return "🌟"
    elif score >= 7:
        return "👍"
    elif score >= 5:
        return "😐"
    else:
        return "💪"

def add_new_record(db: DatabaseManager):
    print("\n--- Add New Lesson Record ---")
    
    # Load existing students for quick selection
    existing_students = db.get_all_student_names_ids()
    if existing_students:
        print("\nExisting students:")
        for i, (name, sid) in enumerate(existing_students.items(), 1):
            print(f"  {i}. {name} (ID: {sid})")
        print()
    
    student_name = input("Student Name: ").strip()
    
    # Check if the student already exists
    existing_id = db.get_student_id_by_name(student_name)
    
    if existing_id:
        print(f"✅ Found existing student: {student_name} (ID: {existing_id})")
        use_existing = input("Use this student ID? (y/n, Enter = yes): ").strip().lower()
        if use_existing in ['', 'y', 'yes']:
            student_id = existing_id
            print(f"✅ Using existing ID: {student_id}")
        else:
            student_id = input("Enter a new student ID: ").strip()
    else:
        print(f"🆕 New student: {student_name}")
        student_id = input("Enter student ID: ").strip()
    
    # Date input handling
    while True:
        date_str = input("Lesson Date (YYYY-MM-DD, Enter = today): ").strip()
        if not date_str:
            course_date = datetime.now().date()
            break
        try:
            course_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            break
        except ValueError:
            print("Invalid date format, please use YYYY-MM-DD.")

    # Lesson duration input
    while True:
        try:
            duration = int(input("Lesson Duration (minutes): "))
            if duration > 0:
                break
            else:
                print("Duration must be greater than 0.")
        except ValueError:
            print("Please enter a valid number.")

    # Hourly rate input
    while True:
        try:
            hourly_rate = float(input("Hourly Rate ($): "))
            if hourly_rate > 0:
                break
            else:
                print("Rate must be greater than 0.")
        except ValueError:
            print("Please enter a valid number.")

    topic = input("Lesson Topic: ").strip()
    homework = input("Assigned Homework: ").strip()
    
    # Student performance input
    while True:
        try:
            performance_input = input("Student Performance (1-10): ")
            performance = int(performance_input)
            if 1 <= performance <= 10:
                break
            else:
                print("Please enter an integer between 1 and 10.")
        except ValueError:
            print("Please enter a valid integer (1-10).")

    notes = input("Notes: ").strip()
    next_plan = input("Next Lesson Plan: ").strip()

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
    print("\n--- Query Lesson Records ---")
    existing_students = db.get_all_student_names_ids()

    # Provide quick student selection first, with a custom filter option
    selected_name = None
    selected_sid = None
    topic = None
    month = None

    if existing_students:
        print("\nStudents (select a number):")
        items = list(existing_students.items())
        for i, (n, s) in enumerate(items, 1):
            print(f"  {i}. {n} (ID: {s})")
        print(f"  {len(items)+1}. Custom filter")

        while True:
            choice = input(f"Enter number (1-{len(items)+1}): ").strip()
            if not choice.isdigit():
                print("Please enter a valid number.")
                continue
            idx = int(choice)
            if 1 <= idx <= len(items):
                selected_name, selected_sid = items[idx-1]
                break
            elif idx == len(items) + 1:
                break
            else:
                print("Out of range, please try again.")

        # 选择了具体学生后，仅再询问主题与月份
        if selected_name:
            topic = input("Filter by lesson topic (Enter to skip): ") or None
            month = input("Filter by month (YYYY-MM, Enter to skip): ") or None
        else:
            # Custom filter
            print("Tip: You can filter by any combination; press Enter to skip a field.")
            selected_name = input("Filter by student name: ") or None
            selected_sid = input("Filter by student ID: ") or None
            topic = input("Filter by lesson topic: ") or None
            month = input("Filter by month (YYYY-MM, Enter to skip): ") or None
    else:
        # Fallback when there is no student data
        print("Tip: You can filter by any combination; press Enter to skip a field.")
        selected_name = input("Filter by student name: ") or None
        selected_sid = input("Filter by student ID: ") or None
        topic = input("Filter by lesson topic: ") or None
        month = input("Filter by month (YYYY-MM, Enter to skip): ") or None

    try:
        records = db.query_records(student_name=selected_name, student_id=selected_sid, topic=topic, month=month)

        if not records:
            print("No matching records found.")
            return

        print(f"\nFound {len(records)} record(s):")
        print("-" * 90)
        for i, record in enumerate(records, 1):
            # Emoji for quick visualization of performance
            performance_emoji = get_performance_emoji(record.student_performance)
            
            print(f"Record #{i}")
            print(f"  Student: {record.student_name} ({record.student_id})")
            print(f"  Date: {record.date}, Duration: {record.duration_minutes} minutes")
            try:
                print(f"  Month: {getattr(record, 'month', '')}")
            except Exception:
                pass
            print(f"  Rate: ${record.hourly_rate}/hour, Income: ${record.total_income}")
            print(f"  Topic: {record.topic_covered}")
            print(f"  Homework: {record.homework_assigned}")
            print(f"  Performance: {record.student_performance}/10 {performance_emoji}")
            print(f"  Notes: {record.notes}")
            print(f"  Plan: {record.next_plan}")
            print("-" * 90)
    except Exception as e:
        print(f"Error during query: {e}")
        print("Please check if the data file is intact.")

def show_all_students(db: DatabaseManager):
    """Display all students and their lesson counts."""
    students_data = db.get_all_student_names_ids()
    if not students_data:
        print("No students recorded yet.")
        return

    # Count lessons per student
    student_lesson_count = {}
    records = db.query_records()
    for record in records:
        student_lesson_count[record.student_name] = student_lesson_count.get(record.student_name, 0) + 1

    if RICH_AVAILABLE:
        console = Console()
        table = Table(show_header=True, header_style="bold")
        table.add_column("No.", justify="right", width=4, no_wrap=True)
        table.add_column("Student Name", justify="left")
        table.add_column("Student ID", justify="left")
        table.add_column("Lessons", justify="right", width=8, no_wrap=True)

        for i, (name, sid) in enumerate(students_data.items(), 1):
            lesson_count = student_lesson_count.get(name, 0)
            table.add_row(str(i), name, sid, f"{lesson_count}")

        console.print(table)
    else:
        _print_students_plain_table(students_data, student_lesson_count)

def show_financial_summary(db: DatabaseManager):
    """Display financial summary."""
    summary = db.get_financial_summary()
    print("\n--- Financial Summary ---")
    print(f"Total Lessons: {summary['total_lessons']}")
    print(f"Total Hours: {summary['total_hours']}")
    print(f"Total Income: ${summary['total_income']}")

def show_monthly_summary(db: DatabaseManager):
    """Display monthly lesson summary."""
    summary = db.get_monthly_summary()
    if not summary:
        print("No data available.")
        return
    if RICH_AVAILABLE:
        console = Console()
        table = Table(show_header=True, header_style="bold")
        table.add_column("Month", justify="left", no_wrap=True)
        table.add_column("Lessons", justify="right", width=8, no_wrap=True)
        table.add_column("Total Hours", justify="right", width=12, no_wrap=True)
        table.add_column("Total Income ($)", justify="right", width=10, no_wrap=True)

        for m, stats in summary.items():
            table.add_row(str(m), str(stats.get('lessons', 0)), f"{stats.get('hours', 0.0):.2f}", f"{stats.get('income', 0.0):.2f}")

        console.print(table)
    else:
        _print_monthly_plain_table(summary)

def main():
    db = DatabaseManager()
    print("=== Tutor Lesson Records & Finance System ===")

    while True:
        print("\nPlease choose an option:")
        print("1. Add new lesson record")
        print("2. Query lesson records")
        print("3. Show all students")
        print("4. Show financial summary")
        print("5. Show monthly summary")
        print("6. Exit")

        choice = input("Enter choice (1/2/3/4/5/6): ").strip()

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
            print("Thank you for using the system. Goodbye!")
            break
        else:
            print("Invalid option, please try again.")

if __name__ == "__main__":
    main()