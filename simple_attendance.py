#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版打卡程式
適合快速使用和學習
"""

import json
import os
from datetime import datetime

class SimpleAttendance:
    """簡化版打卡系統"""
    
    def __init__(self):
        self.data_file = "simple_attendance.json"
        self.data = self.load_data()
    
    def load_data(self):
        """載入資料"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_data(self):
        """儲存資料"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def clock_in(self, name):
        """上班打卡"""
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        
        # 檢查今天是否已打卡
        for record in self.data:
            if record['name'] == name and record['date'] == today and 'clock_in' in record:
                return f"{name} 今天已經打卡上班了！時間：{record['clock_in']}"
        
        # 新增打卡記錄
        record = {
            'name': name,
            'date': today,
            'clock_in': now.strftime("%H:%M:%S")
        }
        self.data.append(record)
        self.save_data()
        
        return f"{name} 上班打卡成功！時間：{now.strftime('%H:%M:%S')}"
    
    def clock_out(self, name):
        """下班打卡"""
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        
        # 找到今天的記錄
        for record in self.data:
            if record['name'] == name and record['date'] == today:
                if 'clock_out' in record:
                    return f"{name} 今天已經打卡下班了！時間：{record['clock_out']}"
                
                # 計算工作時數
                clock_in_time = datetime.strptime(f"{today} {record['clock_in']}", "%Y-%m-%d %H:%M:%S")
                work_hours = (now - clock_in_time).total_seconds() / 3600
                
                record['clock_out'] = now.strftime("%H:%M:%S")
                record['work_hours'] = round(work_hours, 2)
                self.save_data()
                
                return f"{name} 下班打卡成功！時間：{now.strftime('%H:%M:%S')}，工作時數：{work_hours:.2f}小時"
        
        return f"{name} 今天還沒有打卡上班！"
    
    def show_records(self, name=None):
        """顯示打卡記錄"""
        if not self.data:
            return "沒有打卡記錄！"
        
        records = self.data
        if name:
            records = [r for r in records if r['name'] == name]
        
        if not records:
            return f"沒有找到 {name} 的打卡記錄！"
        
        result = "打卡記錄：\n"
        result += "-" * 60 + "\n"
        result += f"{'姓名':<10} {'日期':<12} {'上班':<10} {'下班':<10} {'工時'}\n"
        result += "-" * 60 + "\n"
        
        for record in records:
            clock_out = record.get('clock_out', '-')
            work_hours = f"{record.get('work_hours', 0):.2f}h" if record.get('work_hours') else '-'
            result += f"{record['name']:<10} {record['date']:<12} {record['clock_in']:<10} {clock_out:<10} {work_hours}\n"
        
        return result

def main():
    """主程式"""
    attendance = SimpleAttendance()
    
    while True:
        print("\n" + "="*40)
        print("    簡化版打卡系統")
        print("="*40)
        print("1. 上班打卡")
        print("2. 下班打卡")
        print("3. 查看記錄")
        print("0. 離開")
        print("="*40)
        
        choice = input("請選擇 (0-3): ").strip()
        
        if choice == "0":
            print("再見！")
            break
        elif choice == "1":
            name = input("請輸入姓名: ").strip()
            if name:
                print(attendance.clock_in(name))
        elif choice == "2":
            name = input("請輸入姓名: ").strip()
            if name:
                print(attendance.clock_out(name))
        elif choice == "3":
            name = input("請輸入姓名 (可選): ").strip() or None
            print(attendance.show_records(name))
        else:
            print("無效選擇！")
        
        input("\n按 Enter 繼續...")

if __name__ == "__main__":
    main()

