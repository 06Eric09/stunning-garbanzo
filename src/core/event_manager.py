# event_manager.py
import json
import os
from datetime import datetime

class EventManager:
    def __init__(self, log_file="calendar_events.log"):
        self.log_file = log_file
        self.events = []
        self.load_events_from_log()

    def load_events_from_log(self):
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.events = json.load(f)
                print(f"从日志文件加载了 {len(self.events)} 个事件")
        except Exception as e:
            print(f"加载日志文件失败: {str(e)}")
            self.events = []

    def save_events_to_log(self):
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.events, f, ensure_ascii=False, indent=2)
            print(f"成功保存 {len(self.events)} 个事件到日志文件")
        except Exception as e:
            print(f"保存日志文件失败: {str(e)}")

    def add_event(self, event):
        # 检查重复事件
        if not any(
            e["year"] == event["year"] and 
            e["month"] == event["month"] and 
            e["day"] == event["day"] and
            e["time"] == event["time"] and
            e["activity"] == event["activity"]
            for e in self.events
        ):
            self.events.append(event)
            self.events.sort(key=lambda x: (x["year"], x["month"], x["day"], x["time"]))
            return True
        return False

    def delete_event(self, event):
        self.events = [e for e in self.events if not (
            e["year"] == event["year"] and 
            e["month"] == event["month"] and 
            e["day"] == event["day"] and
            e["time"] == event["time"] and
            e["activity"] == event["activity"] and
            e["location"] == event["location"]
        )]
        return True

    def delete_day_events(self, day, year, month):
        initial_count = len(self.events)
        self.events = [e for e in self.events if not (
            e["year"] == year and e["month"] == month and e["day"] == day
        )]
        return initial_count != len(self.events)

    def get_day_events(self, day, year, month):
        return [
            e for e in self.events
            if e["year"] == year and e["month"] == month and e["day"] == day
        ]

    def has_events_on_day(self, day, year, month):
        return any(
            e["year"] == year and e["month"] == month and e["day"] == day
            for e in self.events
        )
