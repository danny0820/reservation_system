"""
時區工具函數
提供統一的時區處理功能，確保所有時間都使用 UTC+8 時區
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
import pytz

# 定義 UTC+8 時區
UTC_8 = timezone(timedelta(hours=8))
TAIWAN_TZ = pytz.timezone('Asia/Taipei')


def now_utc8() -> datetime:
    """
    獲取目前的 UTC+8 時間
    
    Returns:
        datetime: 當前 UTC+8 時間
    """
    return datetime.now(UTC_8)


def utc_to_taipei(dt: datetime) -> datetime:
    """
    將 UTC 時間轉換為台北時間 (UTC+8)
    
    Args:
        dt: UTC 時間
        
    Returns:
        datetime: 台北時間
    """
    if dt.tzinfo is None:
        # 如果沒有時區信息，假設是 UTC
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.astimezone(TAIWAN_TZ)


def ensure_utc8(dt: Optional[datetime]) -> Optional[datetime]:
    """
    確保時間是 UTC+8 時區
    
    Args:
        dt: 輸入時間
        
    Returns:
        datetime: UTC+8 時間或 None
    """
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        # 沒有時區信息，假設是本地時間 (UTC+8)
        return dt.replace(tzinfo=UTC_8)
    
    # 轉換為 UTC+8
    return dt.astimezone(UTC_8)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化時間為字符串
    
    Args:
        dt: 時間對象
        format_str: 格式字符串
        
    Returns:
        str: 格式化後的時間字符串
    """
    # 確保時間是 UTC+8
    utc8_dt = ensure_utc8(dt)
    return utc8_dt.strftime(format_str) if utc8_dt else ""


def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    解析時間字符串為 UTC+8 時間
    
    Args:
        date_str: 時間字符串
        format_str: 格式字符串
        
    Returns:
        datetime: UTC+8 時間
    """
    dt = datetime.strptime(date_str, format_str)
    return dt.replace(tzinfo=UTC_8)


def get_current_timestamp() -> datetime:
    """
    獲取當前時間戳 (UTC+8)
    這個函數專門用於資料庫模型的 default 值
    
    Returns:
        datetime: 當前 UTC+8 時間
    """
    return now_utc8()