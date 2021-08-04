SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for tbl_fund_total_stock
-- ----------------------------
DROP TABLE IF EXISTS `tbl_fund_total_stock`;
CREATE TABLE `tbl_fund_total_stock`  (
  `stock_value` bigint(255) NOT NULL COMMENT '股市的总市值',
  `stock_increase` bigint(255) NOT NULL DEFAULT 0 COMMENT '股票相对上一期的增长值',
  `stock_increase_rate` decimal(10, 4) NOT NULL DEFAULT 0.0000 COMMENT '股票相对上一期的增长比例',
  `interval_day` bigint(255) NOT NULL DEFAULT 0 COMMENT '股票跟上一期的相差的天数',
  `fund_date` datetime(0) NOT NULL COMMENT '基金公布公布日期',
  `create_time` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp(0) DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
  PRIMARY KEY (`fund_date`) USING BTREE,
  UNIQUE INDEX `idx_stock_date`(`fund_date`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '基金持仓股票每季的总市值信息' ROW_FORMAT = Compact;

SET FOREIGN_KEY_CHECKS = 1;
