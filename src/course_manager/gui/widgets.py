import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime,time
from ..models import Course
from tkinter import messagebox

class CourseForm(tk.Toplevel):
    """课程编辑表单"""
    
    def __init__(self, parent, course: Course = None):
        super().__init__(parent)
        self.course = course
        self.result = None
        self.build_form()

    def build_form(self):
        self.title("课程编辑" if self.course else "添加课程")
        
        # 表单字段
        fields = [
            ("课程名称", "name", str),
            ("星期（1-7）", "weekday", int),
            ("开始时间（HH:MM）", "start_time", str),
            ("结束时间（HH:MM）", "end_time", str),
            ("地点", "location", str),
            ("教师", "teacher", str),
            ("学分", "credit", float)
        ]
        
        for i, (label, attr, dtype) in enumerate(fields):
            ttk.Label(self, text=label).grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(self)
            entry.grid(row=i, column=1, padx=5, pady=5)
            if self.course:
                value = getattr(self.course, attr)
                entry.insert(0, str(value) if not isinstance(value, time) else value.strftime("%H:%M"))
            setattr(self, f"{attr}_entry", entry)

        ttk.Button(self, text="保存", command=self.on_save).grid(row=7, columnspan=2)

    def on_save(self):
        try:
            # 先转换基础类型
            weekday = int(self.weekday_entry.get())
            credit = float(self.credit_entry.get())
            
            # 再创建Course对象
            new_course = Course(
                name=self.name_entry.get().strip(),
                weekday=weekday,
                start_time=datetime.strptime(self.start_time_entry.get(), "%H:%M").time(),
                end_time=datetime.strptime(self.end_time_entry.get(), "%H:%M").time(),
                location=self.location_entry.get().strip(),
                teacher=self.teacher_entry.get().strip(),
                credit=credit
            )
            new_course.validate()  # 显式调用验证
            self.result = new_course
            self.destroy()
        except ValueError as e:
            messagebox.showerror("输入错误", f"数据格式错误：\n{str(e)}")
        except Exception as e:
            messagebox.showerror("未知错误", f"发生意外错误：\n{str(e)}")

class CourseTable(ttk.Treeview):
    def __init__(self, parent):
        super().__init__(parent, 
            columns=("weekday", "time", "location", "teacher", "credit"),
            show="tree headings"
        )
        # 新增状态变量初始化
        self._sort_column = ""       # 当前排序列
        self._sort_reverse = False   # 是否逆序
        self.configure_columns()
        self._bind_sort_events()

    def _bind_sort_events(self):
        """绑定列标题点击事件"""
        for col in self["columns"] + ("#0",):
            self.heading(col, command=lambda c=col: self._on_sort(c))

    def _on_sort(self, column: str):
        """处理排序逻辑（修复主列不可设置问题）"""
        if column == self._sort_column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            self._sort_reverse = False

        # 获取数据时区分主列和其他列
        items = []
        for item in self.get_children(""):
            if column == "#0":
                # 主列数据通过 text 获取
                value = self.item(item, "text")
            else:
                # 其他列通过 set 方法获取
                value = self.set(item, column)
            items.append((value, item))

        # 后续排序逻辑保持不变
        key_func = self._get_sort_key(column)
        items = [(self._get_sort_key(column)(item), item) for item in self.get_children("")]
        
        try:
            # 使用Python的元组排序特性（先主键后次键）
            items.sort(key=lambda x: x[0], reverse=self._sort_reverse)
        except Exception as e:
            messagebox.showerror("排序错误", f"排序失败: {str(e)}")
            return
        
        # 重新插入项目
        for index, (_, item) in enumerate(items):
            self.move(item, "", index)

        # 更新排序指示箭头
        self._update_sort_indicators()

    def _update_sort_indicators(self):
        """更新列标题排序箭头"""
        for col in self["columns"] + ("#0",):
            text = self.heading(col)["text"].replace(" ↑", "").replace(" ↓", "")
            if col == self._sort_column:
                text += " ↓" if self._sort_reverse else " ↑"
            self.heading(col, text=text)
    def _get_sort_key(self, column: str):
        """为每列定义安全的排序键函数"""
        column_parsers = {
            "#0": lambda x: x,                     # 课程名称按原始字符串排序
            "weekday": lambda item: (
                self._parse_weekday(self.set(item, "weekday")),  # 主键：周数
                self._parse_time(self.set(item, "time"))[0]      # 次键：开始时间
            ),
            "time": lambda item: self._parse_time(self.set(item, "time")),
            "location": lambda x: x.strip().lower(),# 地点转为小写后排序
            "teacher": lambda x: x.strip() or "未填写",  # 处理空教师名称
            "credit": self._parse_credit            # 学分安全转换
        }
        return column_parsers.get(column, lambda item: self.set(item, column))

    @staticmethod
    def _parse_credit(credit_str: str) -> float:
        """安全转换学分"""
        try:
            return float(credit_str)
        except ValueError:
            return 0.0  # 无效值视为0学分

    @staticmethod
    def _parse_weekday(weekday_str: str) -> int:
        """安全转换周数"""
        try:
            return int(weekday_str.replace("周", "").strip())
        except ValueError:
            return 0  # 无效值视为周0（实际不会存在）

    @staticmethod
    def _parse_time(time_str: str) -> tuple:
        """安全解析时间"""
        try:
            start, end = time_str.split("-")
            sh, sm = map(int, start.split(":"))
            eh, em = map(int, end.split(":"))
            return (sh * 60 + sm, eh * 60 + em)
        except Exception:
            return (0, 0)  # 无效时间视为00:00-00:00
    @staticmethod
    def _parse_time(time_str: str) -> tuple:
        """将时间字符串转换为可排序的元组"""
        start_end = time_str.split("-")
        return (
            tuple(map(int, start_end[0].split(":"))),
            tuple(map(int, start_end[1].split(":")))
        )
    def configure_columns(self):
        # 主列配置（课程名称）
        self.column("#0", width=200, anchor="center", stretch=False)
        self.heading("#0", text="课程名称", anchor="center")
        
        # 其他列配置
        other_columns = [
            ("weekday", "星期", 80),
            ("time", "时间", 120),
            ("location", "地点", 200),
            ("teacher", "教师", 150),
            ("credit", "学分", 80)
        ]
        
        for col_id, text, width in other_columns:
            self.column(col_id, width=width, anchor="center")
            self.heading(col_id, text=text, anchor="center")
        
        # 强制刷新列布局
        self.update_idletasks()
    def update_items(self, courses: list[Course]):
        print(f"正在加载 {len(courses)} 门课程")  # ✅ 调试输出
        self.delete(*self.get_children())
        if not courses:
            self.insert("", "end", values=("无课程数据", "", "", "", ""))
            return
        for idx, course in enumerate(courses):
            print(f"插入课程 {idx+1}: {course.name}")  # ✅ 调试输出
            self.insert("", "end", 
                text=course.name,
                values=(
                    f"周{course.weekday}",
                    f"{course.start_time.strftime('%H:%M')}-{course.end_time.strftime('%H:%M')}",
                    course.location,
                    course.teacher,
                    str(course.credit)
                ),
                tags=("rowstyle",)
            )
class FilterPanel(ttk.Frame):
    """多列筛选面板"""
    def __init__(self, parent, columns):
        super().__init__(parent)
        self.filters = {}
        self._build_ui(columns)
    
    def _build_ui(self, columns):
        """为每列创建输入框"""
        for idx, col in enumerate(columns):
            ttk.Label(self, text=f"{col}:").grid(row=0, column=idx*2, padx=2)
            entry = ttk.Entry(self, width=12)
            entry.grid(row=0, column=idx*2+1, padx=2)
            self.filters[col] = entry
    
    def get_filters(self) -> dict:
        """获取当前筛选条件"""
        return {col: entry.get().strip() for col, entry in self.filters.items()}