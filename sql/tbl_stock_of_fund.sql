CREATE TABLE `tbl_stock_of_fund` (
  `stock_code` varchar(10) NOT NULL COMMENT '股票编码',
  `stock_name` varchar(255) DEFAULT NULL COMMENT '股票名称',
  `stock_value` bigint(255) NOT NULL COMMENT '股票的市值',
  `fund_proportion` decimal(10,4) NOT NULL COMMENT '股票占基金的比例',
  `fund_code` varchar(10) NOT NULL COMMENT '基金编码',
  `fund_name` varchar(255) NOT NULL COMMENT '基金名称',
  `fund_page` varchar(255) NOT NULL COMMENT '基金地址信息',
  `fund_date` datetime NOT NULL COMMENT '基金公布日期',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`stock_code`,`fund_code`,`fund_date`) USING BTREE,
  UNIQUE KEY `idx_stock_fund_code` (`stock_code`,`fund_code`,`fund_date`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=COMPACT;