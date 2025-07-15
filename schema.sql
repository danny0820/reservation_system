SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- 表格結構: user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `user_id` CHAR(36) NOT NULL COMMENT 'UUID 主鍵',
  `stylist_id` CHAR(36) NULL COMMENT '設計師ID',
  `image` VARCHAR(255) NULL COMMENT '頭像',
  `username` VARCHAR(100) NOT NULL COMMENT '通用名稱',
  `first_name` VARCHAR(50) NULL COMMENT '名字',
  `last_name` VARCHAR(50) NULL COMMENT '姓氏',
  `role` ENUM('customer', 'stylist', 'admin') NOT NULL DEFAULT 'customer' COMMENT '使用者角色',
  `phone` VARCHAR(30) NOT NULL COMMENT '電話號碼',
  `email` VARCHAR(100) UNIQUE NULL COMMENT '電子郵件',
  `password` VARCHAR(255) NULL COMMENT '密碼雜湊值，長度保留255以相容各種演算法',
  `google_uid` VARCHAR(100) UNIQUE NULL,
  `line_uid` VARCHAR(100) UNIQUE NULL,
  `status` VARCHAR(50) NOT NULL,
  `notification` VARCHAR(50) NULL,
  `created_at` DATETIME NOT NULL ,
  `updated_at` DATETIME NOT NULL ,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 表格結構: Products
-- ----------------------------
DROP TABLE IF EXISTS `Products`;
CREATE TABLE `Products` (
  `product_id` CHAR(36) NOT NULL COMMENT 'UUID 主鍵',
  `name` VARCHAR(150) NOT NULL,
  `description` TEXT NULL COMMENT '詳細描述，使用 TEXT 型態以容納長篇文字',
  `price` INT NOT NULL,
  `duration_time` INT NULL COMMENT '服務耗時(分鐘) 或 商品的某種時間屬性',
  `stock_quantity` INT NOT NULL DEFAULT 0,
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  `is_service` BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 表格結構: Appointments
-- ----------------------------
DROP TABLE IF EXISTS `Appointments`;
CREATE TABLE `Appointments` (
  `appointment_id` CHAR(36) NOT NULL COMMENT 'UUID 主鍵',
  `user_id` CHAR(36) NOT NULL COMMENT '預約顧客的ID',
  `stylist_id` CHAR(36) NOT NULL COMMENT '負責服務的設計師ID',
  `start_time` DATETIME NOT NULL,
  `end_time` DATETIME NOT NULL,
  `status` VARCHAR(50) NOT NULL COMMENT '預約狀態',
  `created_at` DATETIME NOT NULL ,
  `updated_at` DATETIME NOT NULL ,
  PRIMARY KEY (`appointment_id`),
  FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`),
  FOREIGN KEY (`stylist_id`) REFERENCES `user`(`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 表格結構: AppointmentServices
-- ----------------------------
DROP TABLE IF EXISTS `AppointmentServices`;
CREATE TABLE `AppointmentServices` (
  `appointment_id` CHAR(36) NOT NULL,
  `product_id` CHAR(36) NOT NULL COMMENT '此處關聯到 Products 表，代表預約的服務項目',
  PRIMARY KEY (`appointment_id`, `product_id`),
  FOREIGN KEY (`appointment_id`) REFERENCES `Appointments`(`appointment_id`) ON DELETE CASCADE,
  FOREIGN KEY (`product_id`) REFERENCES `Products`(`product_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ----------------------------
-- 表格結構: Order
-- ----------------------------
DROP TABLE IF EXISTS `Order`;
CREATE TABLE `Order` (
  `order_id` CHAR(36) NOT NULL COMMENT 'UUID 主鍵',
  `user_id` CHAR(36) NOT NULL COMMENT '顧客ID',
  `appointment_id` CHAR(36) NULL COMMENT '預約ID',
  `total_amount` INT NOT NULL,
  `status` VARCHAR(50) NOT NULL COMMENT '訂單狀態',
  `created_at` DATETIME NOT NULL ,
  `updated_at` DATETIME NOT NULL ,
  PRIMARY KEY (`order_id`),
  FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`),
  FOREIGN KEY (`appointment_id`) REFERENCES `Appointments`(`appointment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 表格結構: Order_detail
-- ----------------------------
DROP TABLE IF EXISTS `Order_detail`;
CREATE TABLE `Order_detail` (
  `order_detail_id` CHAR(36) NOT NULL COMMENT 'UUID 主鍵',
  `order_id` CHAR(36) NOT NULL,
  `product_id` CHAR(36) NOT NULL,
  `quantity` INT NOT NULL,
  `price_per_item` INT NOT NULL,
  `message` TEXT NULL,
  PRIMARY KEY (`order_detail_id`),
  FOREIGN KEY (`order_id`) REFERENCES `Order`(`order_id`) ON DELETE CASCADE,
  FOREIGN KEY (`product_id`) REFERENCES `Products`(`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 排班系統表格
-- ----------------------------
DROP TABLE IF EXISTS `StoreBusinessHours`;
CREATE TABLE `StoreBusinessHours` (
  `hour_id` CHAR(36) NOT NULL COMMENT 'UUID 主鍵',
  `day_of_week` INT NOT NULL COMMENT '星期幾',
  `open_time` TIME NULL COMMENT '開始時間',
  `close_time` TIME NULL COMMENT '結束時間',
  `is_closed` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '當天是否固定公休',
  PRIMARY KEY (`hour_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `StoreClosures`;
CREATE TABLE `StoreClosures` (
  `closure_id` CHAR(36) NOT NULL COMMENT 'UUID 主鍵',
  `start_datetime` DATETIME NOT NULL COMMENT '休業開始時間',
  `end_datetime` DATETIME NOT NULL COMMENT '休業結束時間',
  `reason` TEXT NULL COMMENT '休業原因',
  PRIMARY KEY (`closure_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `StylistSchedules`;
CREATE TABLE `StylistSchedules` (
  `schedule_id` CHAR(36) NOT NULL COMMENT 'UUID 主鍵',
  `stylist_id` CHAR(36) NOT NULL,
  `day_of_week` INT NOT NULL COMMENT '星期幾',
  `start_time` TIME NOT NULL COMMENT '開始時間',
  `end_time` TIME NOT NULL COMMENT '結束時間',
  PRIMARY KEY (`schedule_id`),
  FOREIGN KEY (`stylist_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `StylistTimeOff`;
CREATE TABLE `StylistTimeOff` (
  `time_off_id` CHAR(36) NOT NULL COMMENT 'UUID 主鍵',
  `stylist_id` CHAR(36) NOT NULL,
  `start_datetime` DATETIME NOT NULL COMMENT '休假開始時間',
  `end_datetime` DATETIME NOT NULL COMMENT '休假結束時間',
  `reason` TEXT NULL COMMENT '休假原因',
  PRIMARY KEY (`time_off_id`),
  FOREIGN KEY (`stylist_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- 表格結構: coupon
-- ----------------------------
DROP TABLE IF EXISTS `coupon`;
CREATE TABLE `coupon` (
  `coupon_id` CHAR(36) NOT NULL COMMENT 'UUID 主鍵',
  `code` VARCHAR(255) NULL COMMENT '優惠券代碼',
  `discount_type` VARCHAR(50) NOT NULL COMMENT '折扣類型',
  `discount_value` INT NOT NULL COMMENT '折扣值',
  `name` VARCHAR(255) NULL COMMENT '優惠券名稱',
  `status` VARCHAR(50) NOT NULL COMMENT '優惠券狀態',
  `message` TEXT NULL COMMENT '優惠券訊息',
  `start_at` DATETIME NULL COMMENT '優惠券開始時間',
  `end_at` DATETIME NULL COMMENT '優惠券結束時間',
  PRIMARY KEY (`coupon_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;