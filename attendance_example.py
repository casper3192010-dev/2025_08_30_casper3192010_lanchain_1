#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打卡系統使用範例
展示如何使用 AttendanceSystem 類別
"""

from attendance_system import AttendanceSystem

def demo_attendance_system():
    """打卡系統示範"""
    print("打卡系統示範")
    print("="*50)
    
    # 創建打卡系統實例
    system = AttendanceSystem("demo_attendance.json")
    
    # 示範員工資料
    employees = [
        {"id": "E001", "name": "張小明"},
        {"id": "E002", "name": "李美華"},
        {"id": "E003", "name": "王大雄"}
    ]
    
    print("\n1. 員工上班打卡")
    print("-" * 30)
    for emp in employees:
        result = system.clock_in(emp["id"], emp["name"])
        print(f"{result['message']}")
    
    print("\n2. 查看所有員工記錄")
    print("-" * 30)
    records = system.get_attendance_records()
    for record in records:
        status = "已完成" if record.get("clock_out_time") else "進行中"
        print(f"{record['employee_name']} ({record['employee_id']}) - {record['date']} "
              f"{record['clock_in_time']} {status}")
    
    print("\n3. 員工下班打卡")
    print("-" * 30)
    for emp in employees:
        result = system.clock_out(emp["id"])
        print(f"{result['message']}")
    
    print("\n4. 查看員工統計")
    print("-" * 30)
    for emp in employees:
        stats = system.get_employee_stats(emp["id"])
        print(f"{stats['name']} ({stats['employee_id']}):")
        print(f"  總工作天數: {stats['total_work_days']} 天")
        print(f"  總工作時數: {stats['total_work_hours']} 小時")
        print(f"  本月工作天數: {stats['month_work_days']} 天")
        print(f"  本月工作時數: {stats['month_work_hours']} 小時")
        print()

if __name__ == "__main__":
    demo_attendance_system()

