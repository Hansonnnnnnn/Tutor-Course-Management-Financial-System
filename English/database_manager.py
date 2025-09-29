# database_manager.py
import csv
import os
from datetime import datetime, date
from models import TeachingRecord

CSV_FILE = 'teaching_records.csv'
# 新增 'month' 字段用于按月统计与查询（格式: YYYY-MM）
FIELDNAMES = ['student_name', 'student_id', 'date', 'month', 'duration_minutes', 
              'hourly_rate', 'total_income', 'topic_covered', 
              'homework_assigned', 'student_performance', 'notes', 'next_plan']

class DatabaseManager:
    def __init__(self):
        # 如果CSV文件不存在，则创建它并写入表头；如果存在则确保表头包含 'month'
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()
        else:
            self._ensure_schema()

    def _derive_month_str(self, date_value) -> str:
        """Derive YYYY-MM string from a date value."""
        try:
            if isinstance(date_value, date):
                return date_value.strftime('%Y-%m')
            if isinstance(date_value, str) and date_value:
                # 兼容 'YYYY-MM-DD' 或已是 'YYYY-MM'
                if len(date_value) >= 7:
                    # 优先尝试完整日期解析
                    try:
                        parsed = datetime.strptime(date_value[:10], '%Y-%m-%d').date()
                        return parsed.strftime('%Y-%m')
                    except Exception:
                        return date_value[:7]
            return ''
        except Exception:
            return ''

    def _ensure_schema(self):
        """Ensure CSV contains the latest fields; migrate once if 'month' is missing."""
        try:
            if os.path.getsize(CSV_FILE) == 0:
                # 空文件，写入表头
                with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                    writer.writeheader()
                return

            with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                existing_fieldnames = reader.fieldnames or []
                rows = list(reader)

            if 'month' in existing_fieldnames:
                # 无需迁移
                return

            # 执行迁移：为每一行补充 'month' 字段
            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()
                for row in rows:
                    date_raw = row.get('date', '')
                    month_str = self._derive_month_str(date_raw)
                    writer.writerow({
                        'student_name': row.get('student_name', ''),
                        'student_id': row.get('student_id', ''),
                        'date': row.get('date', ''),
                        'month': month_str,
                        'duration_minutes': row.get('duration_minutes', ''),
                        'hourly_rate': row.get('hourly_rate', ''),
                        'total_income': row.get('total_income', ''),
                        'topic_covered': row.get('topic_covered', ''),
                        'homework_assigned': row.get('homework_assigned', ''),
                        'student_performance': row.get('student_performance', ''),
                        'notes': row.get('notes', ''),
                        'next_plan': row.get('next_plan', '')
                    })
        except Exception as e:
            print(f"Error during CSV schema migration/initialization: {e}")

    def calculate_income(self, duration_minutes: int, hourly_rate: float) -> float:
        """Calculate total income based on duration and hourly rate."""
        hours = duration_minutes / 60
        total_income = hours * hourly_rate
        return round(total_income, 2)

    def add_record(self, record: TeachingRecord):
        """Add a new record to the CSV file."""
        try:
            record.total_income = self.calculate_income(record.duration_minutes, record.hourly_rate)
            
            with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writerow({
                    'student_name': record.student_name,
                    'student_id': record.student_id,
                    'date': record.date.isoformat(),
                    'month': self._derive_month_str(record.date),
                    'duration_minutes': record.duration_minutes,
                    'hourly_rate': record.hourly_rate,
                    'total_income': record.total_income,
                    'topic_covered': record.topic_covered,
                    'homework_assigned': record.homework_assigned,
                    'student_performance': record.student_performance,
                    'notes': record.notes,
                    'next_plan': record.next_plan
                })
            print(f"Record added successfully! Session income: ${record.total_income}")
        except Exception as e:
            print(f"Error adding record: {e}")

    def safe_convert(self, value, target_type, default):
        """Safe data type conversion."""
        try:
            if target_type == int:
                return int(value)
            elif target_type == float:
                return float(value)
            elif target_type == date:
                return datetime.strptime(value, '%Y-%m-%d').date()
            else:
                return str(value)
        except (ValueError, TypeError):
            return default

    def query_records(self, student_name=None, student_id=None, topic=None, month=None):
        """Query records. Filter by student name, ID, topic, and month (YYYY-MM)."""
        records = []
        
        # 检查文件是否为空或不存在
        if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
            return records
            
        try:
            with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # 检查是否只有表头没有数据
                rows = list(reader)
                if not rows:
                    return records
                
                for row in rows:
                    try:
                        # 安全的数据类型转换
                        converted_row = {
                            'student_name': str(row.get('student_name', '')),
                            'student_id': str(row.get('student_id', '')),
                            'date': self.safe_convert(row.get('date', ''), date, datetime.now().date()),
                            'month': str(row.get('month', '') or self._derive_month_str(row.get('date', ''))),
                            'duration_minutes': self.safe_convert(row.get('duration_minutes', 0), int, 0),
                            'hourly_rate': self.safe_convert(row.get('hourly_rate', 0), float, 0.0),
                            'total_income': self.safe_convert(row.get('total_income', 0), float, 0.0),
                            'topic_covered': str(row.get('topic_covered', '')),
                            'homework_assigned': str(row.get('homework_assigned', '')),
                            'student_performance': self.safe_convert(row.get('student_performance', 5), int, 5),
                            'notes': str(row.get('notes', '')),
                            'next_plan': str(row.get('next_plan', ''))
                        }
                        
                        record = TeachingRecord(**{k: v for k, v in converted_row.items() if k != 'month'})
                        
                        # 筛选逻辑
                        match = True
                        if student_name and student_name.lower() not in record.student_name.lower():
                            match = False
                        if student_id and student_id != record.student_id:
                            match = False
                        if topic and topic.lower() not in record.topic_covered.lower():
                            match = False
                        if month:
                            month_str = converted_row['month']
                            if not month_str or not month_str.startswith(str(month)):
                                match = False

                        if match:
                            # 将月份附加到记录对象，便于上层使用
                            try:
                                record.month = converted_row['month']
                            except Exception:
                                pass
                            records.append(record)
                            
                    except Exception as e:
                        print(f"Warning: skipping invalid record row: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error reading data file: {e}")
            
        return records

    def get_all_students(self):
        """Get all unique students (name and ID)."""
        students = set()
        
        if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
            return sorted(students)
            
        try:
            with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get('student_name', '').strip()
                    sid = row.get('student_id', '').strip()
                    if name and sid:  # 只添加非空的学生信息
                        students.add((name, sid))
        except Exception as e:
            print(f"Error retrieving student list: {e}")
            
        return sorted(students)

    def get_financial_summary(self):
        """Get financial summary: total income, total hours, total lessons."""
        total_income = 0.0
        total_hours = 0.0
        total_lessons = 0
        
        if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
            return {
                'total_income': 0.0,
                'total_hours': 0.0,
                'total_lessons': 0
            }
            
        try:
            with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        total_income += self.safe_convert(row.get('total_income', 0), float, 0.0)
                        total_hours += self.safe_convert(row.get('duration_minutes', 0), int, 0) / 60
                        total_lessons += 1
                    except:
                        continue  # Skip problematic rows
        except Exception as e:
            print(f"Error computing financial summary: {e}")
        
        return {
            'total_income': round(total_income, 2),
            'total_hours': round(total_hours, 2),
            'total_lessons': total_lessons
        }

    def get_monthly_summary(self):
        """Summarize by month (YYYY-MM): lessons, total hours, total income."""
        summary = {}
        if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
            return summary
        try:
            with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        month_str = row.get('month') or self._derive_month_str(row.get('date', ''))
                        if not month_str:
                            continue
                        minutes = self.safe_convert(row.get('duration_minutes', 0), int, 0)
                        income = self.safe_convert(row.get('total_income', 0), float, 0.0)
                        if month_str not in summary:
                            summary[month_str] = {
                                'lessons': 0,
                                'hours': 0.0,
                                'income': 0.0
                            }
                        summary[month_str]['lessons'] += 1
                        summary[month_str]['hours'] += minutes / 60
                        summary[month_str]['income'] += income
                    except Exception:
                        continue
        except Exception as e:
            print(f"Error computing monthly summary: {e}")
        # 四舍五入
        for m in list(summary.keys()):
            summary[m]['hours'] = round(summary[m]['hours'], 2)
            summary[m]['income'] = round(summary[m]['income'], 2)
        return dict(sorted(summary.items()))

    def get_student_id_by_name(self, student_name: str) -> str:
        """Find an existing student ID by student name."""
        if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
            return None
        try:
            with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_name = row.get('student_name', '').strip()
                    existing_id = row.get('student_id', '').strip()
                    if existing_name.lower() == student_name.lower():
                        return existing_id
        except Exception as e:
            print(f"Error finding student ID: {e}")
        return None

    def get_all_student_names_ids(self):
        """Get a mapping of all student names to IDs."""
        name_id_map = {}
        if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
            return name_id_map
        try:
            with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get('student_name', '').strip()
                    sid = row.get('student_id', '').strip()
                    if name and sid:
                        name_id_map[name] = sid
        except Exception as e:
            print(f"Error retrieving student list: {e}")
        return name_id_map
 