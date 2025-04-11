import json
from pathlib import Path
from typing import List
from src.course_manager.models import Course
from datetime import time 
class CourseStorage:
    def __init__(self, file_path: str = "data/courses.json"):
        self.file_path = Path(file_path)
        # 新增调试信息
        print(f"存储路径: {self.file_path.absolute()}")
    
    def save(self, courses: List[Course]) -> bool:
        """带详细错误信息的保存方法"""
        try:
            # 确保目录存在
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            print(f"正在保存到: {self.file_path}")
            
            # 转换数据时处理特殊类型
            serializable_data = []
            for c in courses:
                data = c.__dict__.copy()
                # 手动转换时间类型
                data["start_time"] = c.start_time.strftime("%H:%M")
                data["end_time"] = c.end_time.strftime("%H:%M")
                serializable_data.append(data)
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
                print("保存成功")
                return True
        except Exception as e:
            print(f"保存失败原因: {str(e)}")
            return False
        """保存课程数据"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json_data = [{
                'name': course.name,
                'weekday': course.weekday,
                'start_time': course.start_time.strftime("%H:%M"),
                'end_time': course.end_time.strftime("%H:%M"),
                'location': course.location,
                'teacher': course.teacher,
                'credit': course.credit
            } for course in courses]
            json.dump(json_data, f, indent=2)

    def load(self) -> List[Course]:
        """加载所有课程"""
        if not self.file_path.exists():
            return []
            
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Course(
                name=item['name'],
                weekday=item['weekday'],
                start_time=_parse_time(item['start_time']),
                end_time=_parse_time(item['end_time']),
                location=item['location'],
                teacher=item.get('teacher', ''),
                credit=item.get('credit', 1.0)
            ) for item in data]
    def verify_integrity(self, mem_courses: list) -> bool:
        """验证内存与文件数据一致性"""
        file_courses = self.load()
        if len(mem_courses) != len(file_courses):
            print(f"[ERROR] 数据不一致: 内存{len(mem_courses)}条 vs 文件{len(file_courses)}条")
            return False
        
        for mem_c, file_c in zip(mem_courses, file_courses):
            if mem_c != file_c:
                print(f"[ERROR] 数据不匹配:\n内存: {mem_c}\n文件: {file_c}")
                return False
        return True

def _parse_time(time_str: str) -> time:
    """字符串转time对象"""
    return time(*map(int, time_str.split(':')))