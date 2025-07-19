-- 修復 Products 表，添加缺失的時間戳記欄位（UTC+8 時區）
ALTER TABLE Products 
ADD COLUMN created_at DATETIME NOT NULL DEFAULT (CONVERT_TZ(CURRENT_TIMESTAMP, @@session.time_zone, '+08:00')),
ADD COLUMN updated_at DATETIME NOT NULL DEFAULT (CONVERT_TZ(CURRENT_TIMESTAMP, @@session.time_zone, '+08:00')) ON UPDATE (CONVERT_TZ(CURRENT_TIMESTAMP, @@session.time_zone, '+08:00'));
