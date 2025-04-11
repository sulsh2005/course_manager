import tkinter as tk
from tkinter import ttk
from src.course_manager.gui.widgets import CourseTable, CourseForm,FilterPanel
from src.course_manager.logic import CourseManager
from tkinter import messagebox
from datetime import datetime
from src.course_manager.models import Course
class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.style = ttk.Style()
        self.style.configure("Danger.TButton", 
            foreground="black", 
            background="#dc3545",  # Bootstrap 危险红
            font=("微软雅黑", 10, "bold")
        )
        self.title("课程表管理系统")
        self.manager = CourseManager()
        
        # 创建所有UI组件
        self._create_widgets()
        self._setup_layout()
        self.refresh_table()
        self.table = ttk.Treeview(
            columns=("weekday", "time", "location", "teacher", "credit"),
            show="headings"
        )
        
        # 添加学分列排序配置
        self.table.heading("credit", 
                          text="学分",
                          command=lambda: self.sort_column("credit", False))
        self.table.column("credit", width=80, anchor='center')
        
        # 绑定所有列点击事件
        for col in ("weekday", "time", "location", "teacher", "credit"):
            self.table.heading(col, 
                              command=lambda _col=col: self.sort_column(_col, False))
def sort_column(self, col, reverse):
    try:
        # 专业数值排序逻辑
        children = self.table.get_children('')
        data = []
        
        for child in children:
            # 从tag中提取原始数值
            raw_value = self.table.item(child)["tags"][0]
            if col == "credit":
                value = float(raw_value)  # 强制转换确保数值类型
            else:
                value = self.table.set(child, col)
            data.append((value, child))
        
        # 执行稳定排序
        data.sort(key=lambda x: x[0], reverse=reverse)
        
        # 重新排列节点
        for index, (_, child) in enumerate(data):
            self.table.move(child, "", index)
            
        # 更新列标题指示器
        header_text = self.table.heading(col)["text"].split(" ")[0]
        self.table.heading(col, 
                          text=f"{header_text} {'↓' if reverse else '↑'}",
                          command=lambda: self.sort_column(col, not reverse))
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        messagebox.showerror("排序错误", f"详细错误：{str(e)}")
    def _create_widgets(self):
        """创建所有UI组件"""
        # 操作工具栏（添加/编辑/删除）
        self.toolbar = ttk.Frame(self)
        ttk.Button(self.toolbar, text="添加", command=self.add_course).pack(side=tk.LEFT, padx=2)        
        ttk.Button(self.toolbar, 
            text="编辑",
            command=self.edit_course  # 绑定编辑方法
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="删除", command=self.delete_course).pack(side=tk.LEFT, padx=2)
        
        # 筛选组件
        self.filter_panel = FilterPanel(self, columns=["课程名称", "星期", "时间", "地点", "教师", "学分"])
        self.filter_buttons = ttk.Frame(self)
        ttk.Button(self.filter_buttons, text="筛选", command=self.apply_filters).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.filter_buttons, text="重置", command=self.reset_filters).pack(side=tk.LEFT, padx=2)
        
        # 表格
        self.table = CourseTable(self)
        ttk.Button(self.toolbar, 
            text="清空", 
            command=self.clear_all_courses,  # 绑定方法
            style="Danger.TButton"  # 可选：危险操作样式
        ).pack(side=tk.LEFT, padx=2)
    def clear_all_courses(self):
        """清空课程表逻辑"""
        if not self.manager.courses:
            messagebox.showinfo("提示", "课程表已经是空的")
            return
        
        if messagebox.askyesno("危险操作", 
            "确定要清空所有课程吗？此操作不可撤销！",
            icon=messagebox.WARNING
        ):
            success = self.manager.clear_all_courses()
            if success:
                self.refresh_table()
                messagebox.showinfo("成功", "已清空全部课程")
            else:
                messagebox.showerror("错误", "清空失败，请检查文件权限")
    def _setup_layout(self):
        """配置网格布局"""
        # 行0: 操作工具栏
        self.toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # 行1: 筛选面板
        self.filter_panel.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        # 行2: 筛选按钮
        self.filter_buttons.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        
        # 行3: 表格（带滚动条）
        self.table.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
        
        # 配置权重
        self.grid_rowconfigure(3, weight=1)  # 表格行可扩展
        self.grid_columnconfigure(0, weight=1)
    def apply_filters(self):
        """筛选方法（此时manager已存在）"""
        filter_rules = self.filter_panel.get_filters()
        filtered = [c for c in self.manager.courses if self._check_course(c, filter_rules)]
        self.table.update_items(filtered)
    
    def reset_filters(self):
        """重置方法（此时manager已存在）"""
        for entry in self.filter_panel.filters.values():
            entry.delete(0, tk.END)
        self.table.update_items(self.manager.courses)
    
    # ...其他方法保持不变...
    def _check_course(self, course: Course, rules: dict) -> bool:
        parsers = {
            "课程名称": lambda value: lambda c: value.lower() in c.name.lower(),
            "星期": lambda value: lambda c: str(c.weekday) == value.strip(),
            "时间": self._create_time_checker,
            "地点": lambda value: lambda c: value in c.location,
            "教师": lambda value: lambda c: value in c.teacher,
            "学分": self._check_credit
        }
        
        for col, value in rules.items():
            if not value:
                continue
            if col not in parsers:
                continue
            try:
                if not parsers[col](value)(course):
                    return False
            except Exception as e:
                print(f"筛选错误: {str(e)}")
                return False
        return True

    def _create_time_checker(self, value: str):
        """时间筛选函数工厂"""
        def checker(course: Course):
            try:
                req_start, req_end = value.split("-")
                req_start = datetime.strptime(req_start, "%H:%M").time()
                req_end = datetime.strptime(req_end, "%H:%M").time()
                course_start = course.start_time
                course_end = course.end_time
                return (req_start <= course_start < req_end) or \
                    (req_start < course_end <= req_end)
            except Exception:
                return False
        return checker

    def _check_credit(self, value: str):
        """学分筛选函数工厂"""
        def checker(course: Course):
            try:
                if ">" in value:
                    return course.credit > float(value[1:])
                elif "<" in value:
                    return course.credit < float(value[1:])
                elif "=" in value:
                    return course.credit == float(value[1:])
                else:
                    return course.credit == float(value)
            except ValueError:
                return False
        return checker

    # 各列条件解析方法
    def _check_weekday(self, value: str):
        def checker(course: Course):
            try:
                return course.weekday == int(value)
            except ValueError:
                return False
        return checker

    def _check_time_range(self, value: str):
        def checker(course: Course):
            try:
                start, end = value.split("-")
                req_start = datetime.strptime(start, "%H:%M").time()
                req_end = datetime.strptime(end, "%H:%M").time()
                return (req_start <= course.start_time < req_end) or \
                       (req_start < course.end_time <= req_end)
            except Exception:
                return False
        return checker

    def _check_credit(self, value: str):
        def checker(course: Course):
            try:
                if ">" in value:
                    return course.credit > float(value[1:])
                elif "<" in value:
                    return course.credit < float(value[1:])
                elif "=" in value:
                    return course.credit == float(value[1:])
                else:
                    return course.credit == float(value)
            except ValueError:
                return False
        return checker
    def refresh_table(self, sort_column: str = "", reverse: bool = False):
        """刷新表格显示（支持排序）"""
        if sort_column:
            # 获取排序键函数
            sort_key = {
                "课程名称": lambda c: c.name,
                "星期": lambda c: c.weekday,
                "时间": lambda c: (c.start_time, c.end_time),
                "地点": lambda c: c.location,
                "教师": lambda c: c.teacher,
                "学分": lambda c: c.credit
            }[sort_column]
            
            courses = self.manager.get_sorted_courses(sort_key, reverse)
        else:
            courses = self.manager.courses
        
        self.table.update_items(courses)    
        self.table.delete(*self.table.get_children())
        for idx, course in enumerate(self.manager.courses):
            # 使用浮点数存储实际值，显示时格式化为字符串
            self.table.insert("", "end",
                            values=(
                                f"周{course.weekday}",
                                f"{course.start_time.strftime('%H:%M')}-{course.end_time.strftime('%H:%M')}",
                                course.location,
                                course.teacher,
                                f"{course.credit:.1f}"  # 显示格式化后的字符串
                            ),
                            tags=(str(course.credit),))  # 在tag中保留原始数值
    def build_ui(self):
        # 创建主容器
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # 工具栏使用 grid
        toolbar = ttk.Frame(main_frame)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        # 按钮添加到工具栏
        ttk.Button(toolbar, text="添加", command=self.add_course).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="编辑", command=self.edit_course).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="删除", command=self.delete_course).pack(side=tk.LEFT, padx=2)
        
        # 表格和滚动条使用 grid
        self.table = CourseTable(main_frame)
        scroll_y = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure(yscrollcommand=scroll_y.set)
        
        self.table.grid(row=1, column=0, sticky="nsew")
        scroll_y.grid(row=1, column=1, sticky="ns")
        
        # 配置权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
            
    def refresh_table(self):
        """刷新表格数据"""
        self.table.update_items(self.manager.courses)
        
    def add_course(self):
        form = CourseForm(self)
        self.wait_window(form)
        if form.result:
            success, msg = self.manager.add_course(form.result)
            if success:
                self.refresh_table()
                messagebox.showinfo("成功", "课程添加成功！")
            else:
                # 显示详细错误信息（包含换行）
                error_msg = f"添加失败！\n\n原因：\n{msg}"
                messagebox.showerror("操作失败", error_msg)
                    
    def edit_course(self):
        """编辑课程逻辑"""
        selection = self.table.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的课程")
            return
        
        # 获取选中课程的索引
        item_id = selection[0]
        index = self.table.index(item_id)
        
        # 获取原始课程数据
        original_course = self.manager.courses[index]
        
        # 打开编辑表单并传入原数据
        form = CourseForm(self, course=original_course)
        self.wait_window(form)
        
        if form.result:
            # 执行更新操作
            success, msg = self.manager.update_course(index, form.result)
            if success:
                self.refresh_table()
                messagebox.showinfo("成功", "课程更新成功")
            else:
                messagebox.showerror("错误", f"更新失败: {msg}")
                
    def delete_course(self):
        """删除选中课程"""
        selection = self.table.selection()
        if not selection:
            return
            
        index = self.table.index(selection[0])
        if self.manager.delete_course(index):
            self.refresh_table()

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()