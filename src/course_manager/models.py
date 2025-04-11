from dataclasses import dataclass
from datetime import time

@dataclass
class Course:
    """课程数据模型"""
    name: str
    weekday: int          # 1-7 表示周一到周日
    start_time: time
    end_time: time
    location: str
    teacher: str = ""
    credit: float = 1.0

    def __post_init__(self):
        self.validate()

    def validate(self):
        """数据校验"""
        if not 1 <= self.weekday <= 7:
            raise ValueError("星期数必须为1-7")
        if self.start_time >= self.end_time:
            raise ValueError("开始时间必须早于结束时间")