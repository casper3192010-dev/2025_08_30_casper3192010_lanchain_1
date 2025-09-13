#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打卡系統
功能：上班打卡、下班打卡、查看記錄、統計工時
作者：AI Assistant
日期：2025-01-27
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class AttendanceSystem:
    """打卡系統類別"""
    
    def __init__(self, data_file: str = "attendance_data.json"):
        """
        初始化打卡系統
        
        Args:
            data_file: 資料檔案路徑
        """
        self.data_file = data_file
        self.data = self.load_data()
    
    def load_data(self) -> Dict:
        """載入打卡資料"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {"records": [], "employees": {}}
        return {"records": [], "employees": {}}
    
    def save_data(self) -> None:
        """儲存打卡資料"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def clock_in(self, employee_id: str, employee_name: str = None) -> Dict:
        """
        上班打卡
        
        Args:
            employee_id: 員工編號
            employee_name: 員工姓名（可選）
        
        Returns:
            打卡結果字典
        """
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        
        # 檢查今天是否已經打卡上班
        today_records = [r for r in self.data["records"] 
                        if r["employee_id"] == employee_id and r["date"] == today]
        
        if today_records and today_records[-1].get("clock_in_time"):
            return {
                "success": False,
                "message": f"今天已經打卡上班了！上班時間：{today_records[-1]['clock_in_time']}"
            }
        
        # 新增打卡記錄
        record = {
            "employee_id": employee_id,
            "employee_name": employee_name or f"員工{employee_id}",
            "date": today,
            "clock_in_time": now.strftime("%H:%M:%S"),
            "clock_out_time": None,
            "work_hours": 0
        }
        
        self.data["records"].append(record)
        
        # 更新員工資料
        if employee_id not in self.data["employees"]:
            self.data["employees"][employee_id] = {
                "name": employee_name or f"員工{employee_id}",
                "total_work_days": 0,
                "total_work_hours": 0
            }
        
        self.save_data()
        
        return {
            "success": True,
            "message": f"打卡成功！上班時間：{now.strftime('%H:%M:%S')}",
            "record": record
        }
    
    def clock_out(self, employee_id: str) -> Dict:
        """
        下班打卡
        
        Args:
            employee_id: 員工編號
        
        Returns:
            打卡結果字典
        """
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        
        # 找到今天的上班記錄
        today_records = [r for r in self.data["records"] 
                        if r["employee_id"] == employee_id and r["date"] == today]
        
        if not today_records:
            return {
                "success": False,
                "message": "今天還沒有打卡上班！"
            }
        
        latest_record = today_records[-1]
        
        if latest_record.get("clock_out_time"):
            return {
                "success": False,
                "message": f"今天已經打卡下班了！下班時間：{latest_record['clock_out_time']}"
            }
        
        # 計算工作時數
        clock_in_time = datetime.strptime(f"{today} {latest_record['clock_in_time']}", "%Y-%m-%d %H:%M:%S")
        clock_out_time = now
        work_hours = (clock_out_time - clock_in_time).total_seconds() / 3600
        
        # 更新記錄
        latest_record["clock_out_time"] = now.strftime("%H:%M:%S")
        latest_record["work_hours"] = round(work_hours, 2)
        
        # 更新員工統計
        if employee_id in self.data["employees"]:
            self.data["employees"][employee_id]["total_work_days"] += 1
            self.data["employees"][employee_id]["total_work_hours"] += work_hours
        
        self.save_data()
        
        return {
            "success": True,
            "message": f"打卡成功！下班時間：{now.strftime('%H:%M:%S')}，工作時數：{work_hours:.2f}小時",
            "record": latest_record
        }
    
    def get_attendance_records(self, employee_id: str = None, date: str = None) -> List[Dict]:
        """
        取得打卡記錄
        
        Args:
            employee_id: 員工編號（可選）
            date: 日期（可選，格式：YYYY-MM-DD）
        
        Returns:
            打卡記錄列表
        """
        records = self.data["records"]
        
        if employee_id:
            records = [r for r in records if r["employee_id"] == employee_id]
        
        if date:
            records = [r for r in records if r["date"] == date]
        
        # 按日期和時間排序
        records.sort(key=lambda x: (x["date"], x["clock_in_time"]), reverse=True)
        
        return records
    
    def get_employee_stats(self, employee_id: str) -> Dict:
        """
        取得員工統計資料
        
        Args:
            employee_id: 員工編號
        
        Returns:
            員工統計資料
        """
        if employee_id not in self.data["employees"]:
            return {"error": "員工不存在"}
        
        employee = self.data["employees"][employee_id]
        records = self.get_attendance_records(employee_id)
        
        # 計算本月工作天數和時數
        current_month = datetime.now().strftime("%Y-%m")
        month_records = [r for r in records if r["date"].startswith(current_month)]
        month_work_days = len([r for r in month_records if r.get("clock_out_time")])
        month_work_hours = sum([r.get("work_hours", 0) for r in month_records])
        
        return {
            "employee_id": employee_id,
            "name": employee["name"],
            "total_work_days": employee["total_work_days"],
            "total_work_hours": round(employee["total_work_hours"], 2),
            "month_work_days": month_work_days,
            "month_work_hours": round(month_work_hours, 2),
            "recent_records": records[:5]  # 最近5筆記錄
        }
    
    def get_all_employees_stats(self) -> List[Dict]:
        """取得所有員工統計資料"""
        stats = []
        for employee_id in self.data["employees"]:
            stats.append(self.get_employee_stats(employee_id))
        return stats

def main():
    """主程式"""
    system = AttendanceSystem()
    
    while True:
        print("\n" + "="*50)
        print("          打卡系統")
        print("="*50)
        print("1. 上班打卡")
        print("2. 下班打卡")
        print("3. 查看我的打卡記錄")
        print("4. 查看員工統計")
        print("5. 查看所有員工統計")
        print("0. 離開")
        print("="*50)
        
        choice = input("請選擇功能 (0-5): ").strip()
        
        if choice == "0":
            print("感謝使用打卡系統！")
            break
        
        elif choice == "1":
            employee_id = input("請輸入員工編號: ").strip()
            employee_name = input("請輸入員工姓名 (可選): ").strip() or None
            
            result = system.clock_in(employee_id, employee_name)
            print(f"\n{result['message']}")
        
        elif choice == "2":
            employee_id = input("請輸入員工編號: ").strip()
            
            result = system.clock_out(employee_id)
            print(f"\n{result['message']}")
        
        elif choice == "3":
            employee_id = input("請輸入員工編號: ").strip()
            date = input("請輸入查詢日期 (YYYY-MM-DD，可選): ").strip() or None
            
            records = system.get_attendance_records(employee_id, date)
            
            if not records:
                print("\n沒有找到打卡記錄！")
            else:
                print(f"\n打卡記錄 (共{len(records)}筆):")
                print("-" * 80)
                print(f"{'日期':<12} {'上班時間':<10} {'下班時間':<10} {'工作時數':<10} {'狀態'}")
                print("-" * 80)
                
                for record in records:
                    status = "已完成" if record.get("clock_out_time") else "進行中"
                    work_hours = f"{record.get('work_hours', 0):.2f}h" if record.get('work_hours') else "-"
                    clock_out = record.get("clock_out_time", "-")
                    
                    print(f"{record['date']:<12} {record['clock_in_time']:<10} {clock_out:<10} {work_hours:<10} {status}")
        
        elif choice == "4":
            employee_id = input("請輸入員工編號: ").strip()
            
            stats = system.get_employee_stats(employee_id)
            
            if "error" in stats:
                print(f"\n{stats['error']}")
            else:
                print(f"\n員工統計 - {stats['name']} ({stats['employee_id']})")
                print("-" * 40)
                print(f"總工作天數: {stats['total_work_days']} 天")
                print(f"總工作時數: {stats['total_work_hours']} 小時")
                print(f"本月工作天數: {stats['month_work_days']} 天")
                print(f"本月工作時數: {stats['month_work_hours']} 小時")
                
                if stats['recent_records']:
                    print(f"\n最近打卡記錄:")
                    for record in stats['recent_records']:
                        status = "已完成" if record.get("clock_out_time") else "進行中"
                        work_hours = f"{record.get('work_hours', 0):.2f}h" if record.get('work_hours') else "-"
                        clock_out = record.get("clock_out_time", "-")
                        print(f"  {record['date']} {record['clock_in_time']} - {clock_out} ({work_hours}) {status}")
        
        elif choice == "5":
            all_stats = system.get_all_employees_stats()
            
            if not all_stats:
                print("\n沒有員工資料！")
            else:
                print(f"\n所有員工統計 (共{len(all_stats)}人):")
                print("-" * 80)
                print(f"{'員工編號':<10} {'姓名':<10} {'總工作天':<8} {'總工時':<10} {'本月天數':<8} {'本月工時'}")
                print("-" * 80)
                
                for stats in all_stats:
                    print(f"{stats['employee_id']:<10} {stats['name']:<10} {stats['total_work_days']:<8} "
                          f"{stats['total_work_hours']:<10} {stats['month_work_days']:<8} {stats['month_work_hours']}")
        
        else:
            print("\n無效的選擇，請重新輸入！")
        
        input("\n按 Enter 鍵繼續...")

if __name__ == "__main__":
    main()

