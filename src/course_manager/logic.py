from typing import List, Optional
from src.course_manager.models import Course
from src.course_manager.storage import CourseStorage

class CourseManager:
    def __init__(self):
        self.storage = CourseStorage()
        self._courses = []  # 使用私有变量确保数据封装
        self.load_courses()

    @property
    def courses(self):
        """直接返回内存中的课程列表"""
        return self._courses

    def load_courses(self):
        """从存储加载数据（确保使用最新数据）"""
        self._courses = self.storage.load()
        print(f"[DEBUG] 加载课程数量: {len(self._courses)}")

    def add_course(self, course: Course) -> tuple[bool, str]:
        try:
            course.validate()
            # 操作内存列表
            self._courses.append(course)
            if not self.storage.save(self._courses):
                self._courses.pop()  # 回滚
                return False, "保存失败"
            print(f"[DEBUG] 添加后内存课程数: {len(self._courses)}")  # 调试点
            return True, ""
        except ValueError as e:
            return False, str(e)
    def clear_all_courses(self) -> bool:
        """清空所有课程，返回是否成功"""
        self.courses.clear()
        return self.storage.save(self.courses)
    def get_sorted_courses(self, sort_key: callable, reverse: bool = False) -> list[Course]:
        """返回排序后的课程列表（不修改原始数据）"""
        return sorted(self.courses, key=sort_key, reverse=reverse)
    def _check_conflict(self, new_course: Course) -> tuple[bool, str]:
        for existing in self.courses:
            if existing.weekday != new_course.weekday:
                continue
                
            # 精确到分钟的时间比较
            start1 = existing.start_time.hour * 60 + existing.start_time.minute
            end1 = existing.end_time.hour * 60 + existing.end_time.minute
            start2 = new_course.start_time.hour * 60 + new_course.start_time.minute
            end2 = new_course.end_time.hour * 60 + new_course.end_time.minute
            
            if (start1 < end2) and (end1 > start2):  # 更精确的重叠判断
                conflict_info = (
                    f"与 [{existing.name}] 冲突\n"
                    f"时间: 周{existing.weekday} {existing.start_time.strftime('%H:%M')}"
                    f"-{existing.end_time.strftime('%H:%M')}\n"
                    f"地点: {existing.location}"
                )
                return True, conflict_info
        return False, ""


    def delete_course(self, index: int) -> bool:
        """删除课程"""
        if 0 <= index < len(self.courses):
            del self.courses[index]
            self.storage.save(self.courses)
            return True
        return False

    def update_course(self, index: int, new_course: Course) -> tuple[bool, str]:
        """更新指定位置的课程"""
        try:
            # 验证新课程数据
            new_course.validate()
            
            # 备份原数据以便回滚
            original = self.courses[index]
            self.courses[index] = new_course
            
            # 尝试保存
            if not self.storage.save(self.courses):
                self.courses[index] = original  # 回滚
                return False, "保存失败"
                
            return True, ""
        except IndexError:
            return False, "课程索引无效"
        except ValueError as e:
            return False, str(e)