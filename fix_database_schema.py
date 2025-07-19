#!/usr/bin/env python3
"""
修復資料庫表結構腳本
解決 StylistTimeOff 表欄位名稱不一致問題
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.models.schedule_models import StylistTimeOff
from app.database import Base

def fix_stylist_timeoff_table():
    """修復 StylistTimeOff 表結構"""
    
    # 創建資料庫引擎
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as connection:
        # 檢查表是否存在
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print("現有表格:", tables)
        
        if 'StylistTimeOff' in tables:
            # 獲取現有表結構
            columns = inspector.get_columns('StylistTimeOff')
            column_names = [col['name'] for col in columns]
            
            print("StylistTimeOff 表現有欄位:", column_names)
            
            # 檢查是否需要修復
            if 'start_date' in column_names or 'end_date' in column_names:
                print("檢測到需要修復的欄位，開始修復...")
                
                try:
                    # 如果同時存在新舊欄位，刪除舊的欄位
                    if 'start_datetime' in column_names and 'start_date' in column_names:
                        connection.execute(text("ALTER TABLE StylistTimeOff DROP COLUMN start_date"))
                        print("deleted old start_date column")
                    elif 'start_date' in column_names and 'start_datetime' not in column_names:
                        connection.execute(text(
                            "ALTER TABLE StylistTimeOff "
                            "CHANGE COLUMN start_date start_datetime DATETIME NOT NULL COMMENT 'start time'"
                        ))
                        print("renamed start_date to start_datetime")
                    
                    if 'end_datetime' in column_names and 'end_date' in column_names:
                        connection.execute(text("ALTER TABLE StylistTimeOff DROP COLUMN end_date"))
                        print("deleted old end_date column")
                    elif 'end_date' in column_names and 'end_datetime' not in column_names:
                        connection.execute(text(
                            "ALTER TABLE StylistTimeOff "
                            "CHANGE COLUMN end_date end_datetime DATETIME NOT NULL COMMENT 'end time'"
                        ))
                        print("renamed end_date to end_datetime")
                    
                    # 如果存在 status 欄位但模型中沒有，也刪除它
                    if 'status' in column_names:
                        connection.execute(text("ALTER TABLE StylistTimeOff DROP COLUMN status"))
                        print("deleted unused status column")
                    
                    connection.commit()
                    print("table structure fixed successfully!")
                    
                except Exception as e:
                    print(f"❌ 修復過程中發生錯誤: {e}")
                    connection.rollback()
                    return False
                    
            elif 'start_datetime' in column_names and 'end_datetime' in column_names:
                print("✅ 表結構已經正確，無需修復")
            else:
                print("❌ 表結構異常，請檢查資料庫")
                return False
        else:
            print("❌ StylistTimeOff 表不存在，正在創建...")
            # 創建表
            Base.metadata.create_all(bind=engine)
            print("✅ 表創建完成")
    
    # 驗證修復結果
    print("\n驗證修復結果...")
    with engine.connect() as connection:
        inspector = inspect(engine)
        columns = inspector.get_columns('StylistTimeOff')
        column_names = [col['name'] for col in columns]
        print("修復後的欄位:", column_names)
        
        required_columns = ['time_off_id', 'stylist_id', 'start_datetime', 'end_datetime', 'reason']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"❌ 缺少必要欄位: {missing_columns}")
            return False
        else:
            print("✅ 所有必要欄位都已存在")
            return True

if __name__ == "__main__":
    print("開始修復 StylistTimeOff 表結構...")
    success = fix_stylist_timeoff_table()
    
    if success:
        print("\n🎉 資料庫表結構修復成功！")
        print("請重新啟動應用程式並測試請假功能。")
    else:
        print("\n❌ 資料庫表結構修復失敗，請檢查錯誤訊息。")
    
    sys.exit(0 if success else 1)