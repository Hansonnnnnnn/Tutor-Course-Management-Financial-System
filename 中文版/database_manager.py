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
        """从日期值推导 YYYY-MM 字符串。"""
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
        """确保CSV包含最新字段。如果缺少 'month' 字段，则进行一次性迁移。"""
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
            print(f"迁移/初始化CSV模式时出错: {e}")

    def calculate_income(self, duration_minutes: int, hourly_rate: float) -> float:
        """根据时长和小时费率计算总收入"""
        hours = duration_minutes / 60
        total_income = hours * hourly_rate
        return round(total_income, 2)

    def add_record(self, record: TeachingRecord):
        """向CSV文件添加一条新记录"""
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
            print(f"记录已成功添加！本节课收入: ¥{record.total_income}")
        except Exception as e:
            print(f"添加记录时出错: {e}")

    def safe_convert(self, value, target_type, default):
        """安全的数据类型转换"""
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
        """查询记录。可以根据学生姓名、ID、课程主题、月份(YYYY-MM)进行筛选"""
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
                        print(f"警告：跳过无效记录行: {e}")
                        continue
                        
        except Exception as e:
            print(f"读取数据文件时出错: {e}")
            
        return records

    def get_all_students(self):
        """获取所有唯一的学生列表（姓名和ID）"""
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
            print(f"获取学生列表时出错: {e}")
            
        return sorted(students)

    def get_financial_summary(self):
        """获取财务摘要：总收入、总课时等"""
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
                        continue  # 跳过有问题的行
        except Exception as e:
            print(f"计算财务摘要时出错: {e}")
        
        return {
            'total_income': round(total_income, 2),
            'total_hours': round(total_hours, 2),
            'total_lessons': total_lessons
        }

    def get_monthly_summary(self):
        """按月份(YYYY-MM)汇总：课程数、总时长(小时)、总收入。"""
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
            print(f"计算月度汇总时出错: {e}")
        # 四舍五入
        for m in list(summary.keys()):
            summary[m]['hours'] = round(summary[m]['hours'], 2)
            summary[m]['income'] = round(summary[m]['income'], 2)
        return dict(sorted(summary.items()))

    def get_student_id_by_name(self, student_name: str) -> str:
        """根据学生姓名查找已存在的学生ID"""
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
            print(f"查找学生ID时出错: {e}")
        return None

    def get_all_student_names_ids(self):
        """获取所有学生的姓名和ID映射"""
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
            print(f"获取学生列表时出错: {e}")
        return name_id_map
 