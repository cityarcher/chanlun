"""
A股数据获取工具类
基于 baostock 库获取股票数据，支持日K线和分钟K线
包含数据清洗和异常值处理功能
"""

import baostock as bs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Union, List
import warnings

warnings.filterwarnings('ignore')


class AStockDataFetcher:
    """A股数据获取器"""
    
    def __init__(self):
        """初始化数据获取器"""
        self.is_logged_in = False
        
    def login(self) -> bool:
        """登录baostock"""
        try:
            lg = bs.login()
            if lg.error_code == '0':
                self.is_logged_in = True
                print("登录成功")
                return True
            else:
                print(f"登录失败: {lg.error_code} - {lg.error_msg}")
                return False
        except Exception as e:
            print(f"登录异常: {e}")
            return False
    
    def logout(self):
        """登出baostock"""
        if self.is_logged_in:
            bs.logout()
            self.is_logged_in = False
            print("已登出")
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清理数据异常值
        
        Args:
            df: 原始数据DataFrame
            
        Returns:
            清理后的DataFrame
        """
        if df.empty:
            return df
            
        # 复制数据避免修改原数据
        cleaned_df = df.copy()
        
        # 转换日期列为datetime类型
        if 'date' in cleaned_df.columns:
            cleaned_df['date'] = pd.to_datetime(cleaned_df['date'])
        elif 'datetime' in cleaned_df.columns:
            cleaned_df['datetime'] = pd.to_datetime(cleaned_df['datetime'])
        
        # 将字符串类型的数值列转换为float
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
        for col in numeric_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
        
        # 检查并处理异常值
        for col in ['open', 'high', 'low', 'close']:
            if col in cleaned_df.columns:
                # 移除价格为0或负数的记录
                cleaned_df = cleaned_df[cleaned_df[col] > 0]
                
                # 处理极端异常值（价格偏离超过3个标准差）
                mean_val = cleaned_df[col].mean()
                std_val = cleaned_df[col].std()
                if std_val > 0:
                    upper_bound = mean_val + 3 * std_val
                    lower_bound = mean_val - 3 * std_val
                    cleaned_df = cleaned_df[
                        (cleaned_df[col] >= lower_bound) & 
                        (cleaned_df[col] <= upper_bound)
                    ]
        
        # 处理成交量异常值
        if 'volume' in cleaned_df.columns:
            # 移除成交量为0或负数的记录
            cleaned_df = cleaned_df[cleaned_df['volume'] >= 0]
            
            # 处理成交量极端异常值
            volume_mean = cleaned_df['volume'].mean()
            volume_std = cleaned_df['volume'].std()
            if volume_std > 0 and volume_mean > 0:
                volume_upper = volume_mean + 5 * volume_std  # 成交量允许更大的波动
                cleaned_df = cleaned_df[cleaned_df['volume'] <= volume_upper]
        
        # 检查价格逻辑：high >= low, high >= open/close, low <= open/close
        if all(col in cleaned_df.columns for col in ['open', 'high', 'low', 'close']):
            # 价格逻辑检查
            price_logic = (
                (cleaned_df['high'] >= cleaned_df['low']) &
                (cleaned_df['high'] >= cleaned_df['open']) &
                (cleaned_df['high'] >= cleaned_df['close']) &
                (cleaned_df['low'] <= cleaned_df['open']) &
                (cleaned_df['low'] <= cleaned_df['close']) &
                (cleaned_df['open'] > 0) & 
                (cleaned_df['close'] > 0)
            )
            cleaned_df = cleaned_df[price_logic]
        
        # 按日期排序
        date_col = 'date' if 'date' in cleaned_df.columns else 'datetime'
        cleaned_df = cleaned_df.sort_values(date_col).reset_index(drop=True)
        
        # 移除重复的日期
        if date_col in cleaned_df.columns:
            cleaned_df = cleaned_df.drop_duplicates(subset=[date_col], keep='last')
        
        print(f"数据清洗完成：原始数据 {len(df)} 行，清洗后 {len(cleaned_df)} 行")
        return cleaned_df
    
    def get_daily_data(
        self, 
        stock_code: str, 
        start_date: str, 
        end_date: str,
        frequency: str = 'd',
        adjustflag: str = '2'  # 默认前复权
    ) -> pd.DataFrame:
        """
        获取日K线数据
        
        Args:
            stock_code: 股票代码，格式：sh.600000 或 sz.000001
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
            frequency: 频率，'d'=日线，'w'=周线，'m'=月线
            adjustflag: 复权类型，'3'=不复权，'1'=后复权，'2'=前复权
            
        Returns:
            清理后的DataFrame
        """
        if not self.is_logged_in:
            if not self.login():
                return pd.DataFrame()
        
        try:
            fields = "date,code,open,high,low,close,volume,amount,adjustflag,turn,tradestatus,pctChg,isST"
            
            rs = bs.query_history_k_data_plus(
                code=stock_code,
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                fields=fields,
                adjustflag=adjustflag
            )
            
            if rs.error_code != '0':
                print(f"数据获取失败: {rs.error_code} - {rs.error_msg}")
                return pd.DataFrame()
            
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                print("未获取到数据")
                return pd.DataFrame()
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            df['datetime'] = df['date']

            # 数据清洗
            cleaned_df = self._clean_data(df)
            
            return cleaned_df
            
        except Exception as e:
            print(f"获取日K线数据异常: {e}")
            return pd.DataFrame()
    
    def get_minute_data(
        self, 
        stock_code: str, 
        start_date: str, 
        end_date: str,
        frequency: str = '30'
    ) -> pd.DataFrame:
        """
        获取分钟K线数据
        
        Args:
            stock_code: 股票代码，格式：sh.600000 或 sz.000001
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
            frequency: 分钟频率，可选值：'1', '5', '15', '30', '60'
            
        Returns:
            清理后的DataFrame
        """
        if not self.is_logged_in:
            if not self.login():
                return pd.DataFrame()
        
        try:
            fields = "date,time,code,open,high,low,close,volume,amount,adjustflag"
            
            # 获取分钟数据
            rs = bs.query_history_k_data_plus(
                code=stock_code,
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                fields=fields,
                adjustflag="2"  # 分钟数据默认前复权
            )
            
            if rs.error_code != '0':
                print(f"数据获取失败: {rs.error_code} - {rs.error_msg}")
                return pd.DataFrame()
            
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                print("未获取到数据")
                return pd.DataFrame()
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            # 合并日期和时间列为datetime
            if 'date' in df.columns and 'time' in df.columns:
                # date格式：YYYY-MM-DD，time格式：YYYYMMDDHHMMSSsss
                # 提取time中的时间部分 HHMMSS 并忽略毫秒部分
                df['time_formatted'] = df['time'].str[8:10] + ':' + df['time'].str[10:12] + ':' + df['time'].str[12:14]
                # 合并date和格式化后的time
                df['datetime'] = df['date'] + ' ' + df['time_formatted']
                df.drop(['date', 'time', 'time_formatted'], axis=1, inplace=True)
                # 转换为datetime类型
                df['datetime'] = pd.to_datetime(df['datetime'])
            
            # 数据清洗
            cleaned_df = self._clean_data(df)
            
            return cleaned_df
            
        except Exception as e:
            print(f"获取分钟K线数据异常: {e}")
            return pd.DataFrame()
    
    def get_stock_basic_info(self, stock_code: str) -> pd.DataFrame:
        """
        获取股票基本信息
        
        Args:
            stock_code: 股票代码
            
        Returns:
            股票基本信息DataFrame
        """
        if not self.is_logged_in:
            if not self.login():
                return pd.DataFrame()
        
        try:
            rs = bs.query_stock_basic(code=stock_code)
            
            if rs.error_code != '0':
                print(f"获取基本信息失败: {rs.error_code} - {rs.error_msg}")
                return pd.DataFrame()
            
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if data_list:
                return pd.DataFrame(data_list, columns=rs.fields)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"获取股票基本信息异常: {e}")
            return pd.DataFrame()
    
    def batch_get_data(
        self, 
        stock_codes: List[str], 
        start_date: str, 
        end_date: str,
        data_type: str = 'daily',
        **kwargs
    ) -> dict:
        """
        批量获取多只股票数据
        
        Args:
            stock_codes: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            data_type: 数据类型，'daily' 或 'minute'
            **kwargs: 其他参数
            
        Returns:
            股票数据字典 {stock_code: DataFrame}
        """
        results = {}
        
        for stock_code in stock_codes:
            print(f"正在获取 {stock_code} 的数据...")
            
            if data_type == 'daily':
                df = self.get_daily_data(stock_code, start_date, end_date, **kwargs)
            elif data_type == 'minute':
                df = self.get_minute_data(stock_code, start_date, end_date, **kwargs)
            else:
                print(f"不支持的数据类型: {data_type}")
                continue
            
            if not df.empty:
                results[stock_code] = df
                print(f"{stock_code} 数据获取成功，共 {len(df)} 行")
            else:
                print(f"{stock_code} 数据获取失败")
        
        return results
    
    def __enter__(self):
        """上下文管理器入口"""
        self.login()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.logout()


# 使用示例
if __name__ == "__main__":
    # 使用上下文管理器自动登录登出
    with AStockDataFetcher() as fetcher:
        # 获取日K线数据
        daily_data = fetcher.get_daily_data(
            stock_code="sh.600000",
            start_date="2024-01-01",
            end_date="2024-12-31",
            frequency="d",
            adjustflag="2"  # 使用前复权数据
        )
        print("日K线数据:")
        print(daily_data.head())
        
        # 获取30分钟K线数据
        minute_data = fetcher.get_minute_data(
            stock_code="sh.600000",
            start_date="2024-12-01",
            end_date="2024-12-31",
            frequency="30"
        )
        print("\n30分钟K线数据:")
        print(minute_data.head())
        
        # 批量获取数据
        stocks = ["sh.600000", "sz.000001", "sh.600519"]
        batch_data = fetcher.batch_get_data(
            stock_codes=stocks,
            start_date="2024-01-01",
            end_date="2024-12-31",
            data_type="daily"
        )
        print(f"\n批量获取完成，共获取 {len(batch_data)} 只股票数据")