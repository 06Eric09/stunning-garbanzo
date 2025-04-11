# calendar_ui.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import calendar
from datetime import datetime
import json

class CalendarUI:
    
    def __init__(self, root, event_manager, api_handler):
        self.root = root
        self.root.title("📅 智能日历管理系统")
        self.event_manager = event_manager
        self.api_handler = api_handler
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.root.geometry("900x750")
        self.selected_day = None
        self.is_analyzing = False
        
        # 设置主题和样式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.setup_styles()
        
        self.setup_ui()

    def setup_styles(self):
        """设置自定义样式"""
        self.style.configure('TFrame', background='#f5f5f5')
        self.style.configure('TLabel', background='#f5f5f5', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10), anchor='center', padding=5)
        self.style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        self.style.configure('Header.TLabel', font=('Arial', 11, 'bold'))
        self.style.configure('Event.TButton', 
                           foreground='white', 
                           background='#4a90e2',
                           anchor='center',
                           font=('Arial', 10, 'bold'))
        self.style.configure('Today.TButton', 
                           foreground='white', 
                           background='#50c878',
                           anchor='center',
                           font=('Arial', 10, 'bold'))
        self.style.configure('Accent.TButton', 
                           foreground='white', 
                           background='#4a90e2',
                           anchor='center',
                           font=('Arial', 10, 'bold'))
        self.style.configure('Danger.TButton', 
                           foreground='white', 
                           background='#e74c3c',
                           anchor='center',
                           font=('Arial', 10, 'bold'))
        self.style.configure('TEntry', padding=5)
        self.style.configure('TText', padding=5)
        self.style.configure('TLabelframe', background='#f5f5f5')
        self.style.configure('TLabelframe.Label', background='#f5f5f5')
        
        # 按钮状态样式映射
        self.style.map('Event.TButton',
                     foreground=[('pressed', 'white'), ('active', 'white')],
                     background=[('pressed', '#3a7bd5'), ('active', '#3a7bd5')])
        self.style.map('Today.TButton',
                     foreground=[('pressed', 'white'), ('active', 'white')],
                     background=[('pressed', '#3cb371'), ('active', '#3cb371')])
        self.style.map('Accent.TButton',
                     foreground=[('pressed', 'white'), ('active', 'white')],
                     background=[('pressed', '#3a7bd5'), ('active', '#3a7bd5')])
        self.style.map('Danger.TButton',
                     foreground=[('pressed', 'white'), ('active', 'white')],
                     background=[('pressed', '#c0392b'), ('active', '#c0392b')])

    def setup_ui(self):
        # 主容器 - 使用PanedWindow实现可调整区域
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # 上部容器(API设置、输入区域、日历控制)
        self.top_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.top_frame, weight=1)
        
        # 下部容器(日历和事件区域)
        self.bottom_paned = ttk.PanedWindow(self.main_paned, orient=tk.HORIZONTAL)
        self.main_paned.add(self.bottom_paned, weight=2)
        self.bottom_paned.update_idletasks()
        # API设置区域
        api_frame = ttk.LabelFrame(self.top_frame, text="API 设置", padding=10)
        api_frame.pack(fill=tk.X, pady=(0, 10))
        
        api_inner_frame = ttk.Frame(api_frame)
        api_inner_frame.pack(fill=tk.X)
        
        ttk.Label(api_inner_frame, text="DeepSeek API 密钥:").pack(side=tk.LEFT, padx=(0, 5))
        self.api_entry = ttk.Entry(api_inner_frame, width=50)
        saved_key = self.api_handler.load_api_key()
        if saved_key:
            self.api_entry.insert(0, saved_key)
        self.api_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        ttk.Button(
            api_inner_frame, 
            text="更新密钥", 
            command=self.update_api,
            style='Accent.TButton'
        ).pack(side=tk.LEFT)

        # 输入区域
        input_frame = ttk.LabelFrame(self.top_frame, text="📝 事件输入", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.text_input = scrolledtext.ScrolledText(
            input_frame, 
            height=1,
            wrap=tk.WORD,
            font=('Arial', 10),
            padx=5,
            pady=5
        )
        self.text_input.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.btn_analyze = ttk.Button(
            btn_frame,
            text="🔍 分析文本",
            command=self.analyze_text,
            style='Accent.TButton'
        )
        self.btn_analyze.pack(side=tk.RIGHT)

        # 日历控制区域
        control_frame = ttk.Frame(self.top_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        control_frame.config(height=50) 
        control_frame.pack_propagate(False) 
        # 年份选择
        year_frame = ttk.Frame(control_frame)
        year_frame.pack(side=tk.LEFT, padx=5)
        ttk.Label(year_frame, text="年份:").pack(side=tk.LEFT)
        self.year_var = tk.StringVar(value=str(self.current_year))
        self.spin_year = ttk.Spinbox(
            year_frame,
            from_=2000,
            to=2100,
            textvariable=self.year_var,
            width=6,
            command=self.update_calendar,
            font=('Arial', 10)
        )
        self.spin_year.pack(side=tk.LEFT)

        # 月份选择
        month_frame = ttk.Frame(control_frame)
        month_frame.pack(side=tk.LEFT, padx=5)
        ttk.Label(month_frame, text="月份:").pack(side=tk.LEFT)
        self.month_var = tk.StringVar(value=str(self.current_month))
        self.spin_month = ttk.Spinbox(
            month_frame,
            from_=1,
            to=12,
            textvariable=self.month_var,
            width=4,
            command=self.update_calendar,
            font=('Arial', 10)
        )
        self.spin_month.pack(side=tk.LEFT)

        # 新增：日期快速跳转
        date_frame = ttk.Frame(control_frame)
        date_frame.pack(side=tk.LEFT, padx=5)
        ttk.Label(date_frame, text="跳转到:").pack(side=tk.LEFT)
        
        self.day_var = tk.StringVar()
        self.day_entry = ttk.Entry(date_frame, textvariable=self.day_var, width=3)
        self.day_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(date_frame, text="日").pack(side=tk.LEFT)
        
        ttk.Button(
            date_frame,
            text="跳转",
            command=self.jump_to_date,
            style='Accent.TButton',
            width=6,
            padding=(10, 5)
        ).pack(side=tk.LEFT, padx=5)

        # 今天按钮
        ttk.Button(
            control_frame,
            text="今天",
            command=self.go_to_today,
            style='Accent.TButton',
            padding=(10, 5)
            ).pack(side=tk.RIGHT)

        # 日历显示区域
        self.calendar_container = ttk.Frame(self.bottom_paned)
        self.bottom_paned.add(self.calendar_container, weight=1)
        
        # 日历垂直滚动条
        self.calendar_vscroll = ttk.Scrollbar(self.calendar_container)
        self.calendar_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 日历水平滚动条
        self.calendar_hscroll = ttk.Scrollbar(self.calendar_container, orient=tk.HORIZONTAL)
        self.calendar_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 日历Canvas
        self.calendar_canvas = tk.Canvas(
            self.calendar_container,
            yscrollcommand=self.calendar_vscroll.set,
            xscrollcommand=self.calendar_hscroll.set,
            highlightthickness=0
        )
        self.calendar_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.calendar_vscroll.config(command=self.calendar_canvas.yview)
        self.calendar_hscroll.config(command=self.calendar_canvas.xview)
        
        # 日历框架
        self.calendar_frame = ttk.Frame(self.calendar_canvas)
        self.calendar_canvas.create_window((0, 0), window=self.calendar_frame, anchor="nw")
        
        # 绑定配置事件
        self.calendar_frame.bind(
            "<Configure>",
            lambda e: self.calendar_canvas.configure(
                scrollregion=self.calendar_canvas.bbox("all"))
        )
        
       # 事件区域 - 使用PanedWindow实现可调整分割
        self.event_paned = ttk.PanedWindow(self.bottom_paned, orient=tk.VERTICAL)
        self.bottom_paned.add(self.event_paned, weight=2)

        # 当天事项区域（上方）
        self.event_buttons_frame = ttk.LabelFrame(
            self.event_paned,
            text="📌 当天事项",
            padding=10
        )
        self.event_paned.add(self.event_buttons_frame, weight=2)

        # 当天事项滚动区域
        self.events_canvas = tk.Canvas(self.event_buttons_frame, highlightthickness=0)
        self.events_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.events_scroll = ttk.Scrollbar(
            self.event_buttons_frame,
            orient="vertical",
            command=self.events_canvas.yview
        )
        self.events_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.events_canvas.configure(yscrollcommand=self.events_scroll.set)
        
        self.events_inner_frame = ttk.Frame(self.events_canvas)
        self.events_canvas.create_window((0, 0), window=self.events_inner_frame, anchor="nw")
        
        self.events_inner_frame.bind(
            "<Configure>",
            lambda e: self.events_canvas.configure(
                scrollregion=self.events_canvas.bbox("all"))
        )

        # 删除按钮（在当天事项区域内底部）
        self.btn_delete_day = ttk.Button(
            self.event_buttons_frame,
            text="🗑️ 删除当天所有事项",
            command=self.delete_day_events,
            state='disabled',
            style='Danger.TButton'
        )
        self.btn_delete_day.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        # 事项详情区域（下方）
        self.event_detail_frame = ttk.LabelFrame(
            self.event_paned,
            text="🔎 事项详情",
            padding=10
        )
        self.event_paned.add(self.event_detail_frame, weight=1)
        
        # 详情文本框
        self.detail_text = scrolledtext.ScrolledText(
            self.event_detail_frame,
            height=8,
            state='disabled',
            font=('Arial', 10),
            wrap=tk.WORD,
            padx=5,
            pady=5
        )
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        
        # 创建日历
        self.create_calendar()

    def create_calendar(self):
        """创建日历视图"""
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        year = int(self.year_var.get())
        month = int(self.month_var.get())
        today = datetime.now()

        # 日历标题
        title_frame = ttk.Frame(self.calendar_frame)
        title_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(
            title_frame,
            text=f"{calendar.month_name[month]} {year}",
            style='Header.TLabel',
            font=('Arial', 10, 'bold')
        ).pack()

        # 星期标题
        weekdays_frame = ttk.Frame(self.calendar_frame)
        weekdays_frame.pack(fill=tk.X, pady=2)

        for day in ["Mon.", "Tue.", "Wed.", "Thu.", "Fri.", "Sat.", "Sun."]:
            ttk.Label(
                weekdays_frame,
                text=day,
                width=4,
                anchor='center',
                font=4,
                style='Header.TLabel'
            ).pack(side=tk.LEFT, expand=True)

        # 日历日期
        cal = calendar.monthcalendar(year, month)
        for week in cal:
            week_frame = ttk.Frame(self.calendar_frame)
            week_frame.pack(fill=tk.X, pady=1)

            for day in week:
                day_frame = ttk.Frame(week_frame, width=70, height=60)
                day_frame.pack_propagate(0)
                day_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

                if day == 0:
                    continue

                has_event = self.event_manager.has_events_on_day(day, year, month)
                is_today = (day == today.day and month == today.month and year == today.year)

                btn_style = 'Today.TButton' if is_today else ('Event.TButton' if has_event else 'TButton')
                
                day_btn = ttk.Button(
                    day_frame,
                    text=str(day),
                    padding=2,
                    command=lambda d=day, y=year, m=month: self.show_day_events(d, y, m),
                    style=btn_style
                )
                day_btn.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    def show_day_events(self, day, year, month):
        """显示选定日期的事件"""
        self.selected_day = (day, year, month)

        # 清除现有事件显示
        for widget in self.events_inner_frame.winfo_children():
            widget.destroy()

        day_events = self.event_manager.get_day_events(day, year, month)

        if not day_events:
            ttk.Label(
                self.events_inner_frame,
                text=f"{year}年{month}月{day}日没有安排",
                foreground='gray',
                font=('Arial', 10, 'italic')
            ).pack(anchor='w', pady=10)
            self.btn_delete_day.config(state='disabled')
            self.detail_text.config(state='normal')
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.config(state='disabled')
            return
        else:
            self.btn_delete_day.config(state='normal')

        # 添加事件按钮
        for event in day_events:
            event_frame = ttk.Frame(self.events_inner_frame)
            event_frame.pack(fill='x', pady=2, padx=5)

            ttk.Button(
                event_frame,
                text=f"⏰ {event['time']} - {event['activity']}",
                command=lambda e=event: self.show_event_detail(e),
                style='TButton'
            ).pack(side=tk.LEFT, expand=True, fill=tk.X)

            ttk.Button(
                event_frame,
                text="✕",
                command=lambda e=event: self.delete_single_event(e),
                width=3,
                style='Danger.TButton'
            ).pack(side=tk.LEFT, padx=(5, 0))

        # 显示第一个事件的详情
        if day_events:
            self.show_event_detail(day_events[0])

    def delete_single_event(self, event):
        """删除单个事件"""
        if messagebox.askyesno("确认删除", f"确定要删除事项 '{event['activity']}' 吗？"):
            if self.event_manager.delete_event(event):
                self.event_manager.save_events_to_log()
                self.update_calendar()
                self.show_day_events(event["day"], event["year"], event["month"])
                messagebox.showinfo("成功", "事项已删除")

    def delete_day_events(self):
        """删除当天所有事件"""
        if not self.selected_day:
            return
            
        day, year, month = self.selected_day
        
        if messagebox.askyesno("确认删除", f"确定要删除{year}年{month}月{day}日的所有事项吗？"):
            if self.event_manager.delete_day_events(day, year, month):
                self.event_manager.save_events_to_log()
                self.update_calendar()
                self.show_day_events(day, year, month)

    def show_event_detail(self, event):
        """显示事件详情"""
        self.detail_text.config(state='normal')
        self.detail_text.delete(1.0, tk.END)

        details = (
            f"📌 事项: {event['activity']}\n\n"
            f"🕒 时间: {event['time']}\n\n"
            f"📍 地点: {event['location']}\n\n"
            f"📅 日期: {event['year']}年{event['month']}月{event['day']}日"
        )
        self.detail_text.insert(tk.END, details)
        self.detail_text.config(state='disabled')

    def update_api(self):
        """更新API密钥"""
        new_key = self.api_entry.get()
        success, message = self.api_handler.update_api_key(new_key)
        if success:
            messagebox.showinfo("成功", message)
        else:
            messagebox.showerror("错误", message)

    def analyze_text(self):
        """分析文本并提取事件"""
        if self.is_analyzing:
            return
            
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("警告", "请输入要分析的文本内容")
            return

        self.is_analyzing = True
        self.btn_analyze.config(state='disabled', text="分析中...")
        
        def analysis_callback(success, result):
            self.is_analyzing = False
            self.btn_analyze.config(state='normal', text="🔍 分析文本")
            if success:
                try:
                    parsed_response = json.loads(result)
                    self.parse_events(parsed_response)
                    self.event_manager.save_events_to_log()
                    messagebox.showinfo("成功", "文本分析完成！")
                except json.JSONDecodeError:
                    messagebox.showerror("错误", "API返回了无效的JSON格式")
            else:
                messagebox.showerror("错误", result)

        self.api_handler.analyze_text_async(text, analysis_callback)

    def parse_events(self, api_response):
        """解析API返回的事件数据"""
        try:
            if isinstance(api_response, str):
                api_response = json.loads(api_response)
            
            events_data = api_response
            if isinstance(api_response, dict):
                if 'events' in api_response:
                    events_data = api_response['events']
                else:
                    events_data = [api_response]
            
            for event in events_data:
                try:
                    date_str = event.get("date") or event.get("日期")
                    if not date_str:
                        continue

                    date_parts = date_str.split("-")
                    if len(date_parts) != 3:
                        continue

                    year, month, day = map(int, date_parts)
                    new_event = {
                        "date": date_str,
                        "year": year,
                        "month": month,
                        "day": day,
                        "location": event.get("location", event.get("地点", "未指定")),
                        "time": event.get("time", event.get("时间", "未指定")),
                        "activity": event.get("activity", event.get("事项", "未指定"))
                    }
                    
                    self.event_manager.add_event(new_event)
                        
                except (ValueError, AttributeError, KeyError):
                    continue
            
            self.update_calendar()
            today = datetime.now()
            self.show_day_events(today.day, today.year, today.month)
            
        except Exception as e:
            print(f"Error parsing events: {str(e)}")
            raise

    def update_calendar(self):
        """更新日历显示"""
        self.create_calendar()

    def go_to_today(self):
        """跳转到今天"""
        today = datetime.now()
        self.year_var.set(today.year)
        self.month_var.set(today.month)
        self.day_var.set(today.day)  # 新增：自动填充当前日
        self.update_calendar()
        self.show_day_events(today.day, today.year, today.month)

    def jump_to_date(self):
        """跳转到指定日期"""
        try:
            day = int(self.day_var.get())
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            
            # 验证日期有效性
            if month < 1 or month > 12:
                raise ValueError("月份无效")
                
            _, last_day = calendar.monthrange(year, month)
            if day < 1 or day > last_day:
                raise ValueError("日期无效")
                
            self.show_day_events(day, year, month)
            
        except ValueError as e:
            messagebox.showerror("错误", f"无效日期: {str(e)}")



