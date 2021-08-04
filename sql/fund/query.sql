-- 基金的股票市值
SELECT FORMAT(stock_value,0) as 基金的股票总市值,  FORMAT(stock_increase,0) as 基金的股票增长市值 ,  concat ( round(stock_increase_rate *100,2),'%')  as 环比增长率 ,interval_day as 间隔天数, stock_date as 发布日期 FROM `tbl_fund_total_stock` ORDER BY stock_date  desc;

-- 最近一期增长值降序
SELECT stock_code as 股市代码 ,stock_name as 股票名称, FORMAT(stock_value,0) as 股票市值,  FORMAT(stock_increase,0) as 股票环比增长市值 , concat ( round(stock_increase_rate *100,2),'%')  as 环比增长率 , interval_day as 环比间隔天数, stock_date as 发布日期 FROM `tbl_fund_stock_value` where stock_date = "2021-06-30 00:00:00"  ORDER BY stock_increase  desc;

-- 最近一期增长率降序
SELECT stock_code as 股市代码 ,stock_name as 股票名称, FORMAT(stock_value,0) as 股票市值,  FORMAT(stock_increase,0) as 股票环比增长市值 , concat ( round(stock_increase_rate *100,2),'%')  as 环比增长率 , interval_day as 环比间隔天数, stock_date as 发布日期 FROM `tbl_fund_stock_value` where stock_date = "2021-06-30 00:00:00"  ORDER BY stock_increase_rate  desc;

-- 最近一期 市值大于1个亿 增长率降序
SELECT stock_code as 股市代码 ,stock_name as 股票名称, FORMAT(stock_value,0) as 股票市值,  FORMAT(stock_increase,0) as 股票环比增长市值 , concat ( round(stock_increase_rate *100,2),'%')  as 环比增长率 , interval_day as 环比间隔天数, stock_date as 发布日期 FROM `tbl_fund_stock_value` where stock_date = "2021-06-30 00:00:00" and stock_value > 100000000 ORDER BY stock_increase_rate  desc;