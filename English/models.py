# models.py
from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class TeachingRecord:
    student_name: str
    student_id: str
    date: date
    duration_minutes: int
    hourly_rate: float
    total_income: float
    topic_covered: str
    homework_assigned: str
    student_performance: int  # integer from 1 to 10
    notes: str
    next_plan: str