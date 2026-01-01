"""
基于mootdx库的股票数据获取类
支持A股（沪深京）、港股、ETF、指数的日K和分钟K数据
包含通达信线路测试和最优线路存储功能
与AStockDataFetcher保持完全兼容的数据格式
"""

import pandas as pd
import numpy as np
import json
import socket
import time
import os
from datetime import datetime
from typing import Optional, Union, List
import warnings
from mootdx.quotes import Quotes, ExtQuotes

warnings.filterwarnings('ignore')


class MootdxDataFetcher:
    """基于mootdx的股票数据获取器"""
    
    # 通达信服务器列表
    TDX_SERVERS = [
        ('60.12.136.250', 7709),
        ('115.238.90.165', 7709),
        ('116.205.178.103', 7711),
        ('139.9.81.150', 7711),
        ('139.159.226.137', 7711),
        ('124.71.85.98', 7711),
        ('119.29.19.242', 7711),
        ('43.136.50.60', 7711),
        ('101.33.197.245', 7711),
        ('183.232.222.13', 7711),
    ]
    
    def __init__(self, config_file: str = "best_server.json"):
        """
        初始化数据获取器
        
        Args:
            config_file: 最优线路配置文件路径
        """
        self.config_file = config_file
        self.optimal_server = None
        self.optimal_latency = None
        self.last_test_time = None
        self.is_connected = False
        
        # 加载或测试最优线路
        self._initialize_server()
    
    def _initialize_server(self):
        """初始化服务器连接"""
        # 尝试从配置文件加载最优线路
        if self._load_optimal_server():
            print(f"✓ 已加载最优线路: {self.optimal_server}")
        else:
            # 配置文件不存在或无效，测试所有线路
            print("未找到有效线路配置，开始测试线路...")
            self._test_and_save_best_server()
    
    def _load_optimal_server(self) -> bool:
        """
        从配置文件加载最优线路
        
        Returns:
            加载成功返回True，否则返回False
        """
        try:
            if not os.path.exists(self.config_file):
                return False
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 验证配置格式
            if 'optimal_server' not in config or 'last_updated' not in config:
                return False
            
            # 检查配置是否过期（超过7天重新测试）
            last_updated = datetime.fromisoformat(config['last_updated'])
            days_old = (datetime.now() - last_updated).days
            if days_old > 7:
                print(f"线路配置已过期({days_old}天)，重新测试...")
                return False
            
            self.optimal_server = config['optimal_server']
            self.optimal_latency = config.get('latency_ms', None)
            self.last_test_time = last_updated
            
            # 验证线路是否仍然可用
            if self._test_server_connection(*self._parse_server(self.optimal_server)):
                return True
            else:
                print("最优线路不可用，重新测试...")
                return False
                
        except Exception as e:
            print(f"加载线路配置失败: {e}")
            return False
    
    def _parse_server(self, server_str: str) -> tuple:
        """
        解析服务器字符串
        
        Args:
            server_str: 格式为 "ip:port" 的字符串
            
        Returns:
            (ip, port) 元组
        """
        parts = server_str.split(':')
        return (parts[0], int(parts[1]))
    
    def _test_server_connection(self, host: str, port: int, timeout: int = 3) -> Optional[float]:
        """
        测试单个服务器的连接延迟
        
        Args:
            host: 服务器IP
            port: 服务器端口
            timeout: 超时时间（秒）
            
        Returns:
            连接成功返回延迟（毫秒），失败返回None
        """
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            end_time = time.time()
            sock.close()
            
            latency_ms = (end_time - start_time) * 1000
            return latency_ms
        except Exception as e:
            # print(f"测试 {host}:{port} 失败: {e}")
            return None
    
    def _test_all_servers(self) -> List[tuple]:
        """
        测试所有服务器线路
        
        Returns:
            [(server_str, latency_ms), ...] 列表，按延迟排序
        """
        print("开始测试通达信线路...")
        results = []
        
        for host, port in self.TDX_SERVERS:
            server_str = f"{host}:{port}"
            latency = self._test_server_connection(host, port)
            
            if latency is not None:
                results.append((server_str, latency))
                print(f"  ✓ {server_str}: {latency:.2f}ms")
            else:
                print(f"  ✗ {server_str}: 连接失败")
        
        # 按延迟排序
        results.sort(key=lambda x: x[1])
        return results
    
    def _test_and_save_best_server(self) -> bool:
        """
        测试所有线路并保存最优线路
        
        Returns:
            成功返回True，否则返回False
        """
        results = self._test_all_servers()
        
        if not results:
            print("❌ 未找到可用的通达信线路")
            return False
        
        best_server, best_latency = results[0]
        self.optimal_server = best_server
        self.optimal_latency = best_latency
        self.last_test_time = datetime.now()
        
        print(f"\n✓ 最优线路: {best_server} (延迟: {best_latency:.2f}ms)")
        
        # 保存到配置文件
        self._save_optimal_server()
        return True
    
    def _save_optimal_server(self):
        """保存最优线路到配置文件"""
        try:
            config = {
                'optimal_server': self.optimal_server,
                'latency_ms': self.optimal_latency,
                'last_updated': self.last_test_time.isoformat() if self.last_test_time else datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✓ 最优线路已保存到 {self.config_file}")
        except Exception as e:
            print(f"保存线路配置失败: {e}")
    
    def _get_quotes_client(self, market_type: int = 1):
        """
        获取行情客户端实例
        
        Args:
            market_type: 市场类型
                1: 上海市场
                0: 深圳市场
                2: 港股市场
                
        Returns:
            Quotes实例
        """
        try:
            # 使用mootdx的内置最佳IP选择功能
            client_kwargs = {
                'market': 'std',
                'multithread': True,
                'heartbeat': True,
                'timeout': 15
            }
            
            # 如果有保存的最优服务器，优先使用
            if self.optimal_server:
                try:
                    server_ip, server_port = self._parse_server(self.optimal_server)
                    client_kwargs['server'] = (server_ip, server_port)
                    print(f"使用已保存的最优服务器: {self.optimal_server}")
                except Exception as e:
                    print(f"解析最优服务器失败，使用自动选择: {e}")
                    client_kwargs['bestip'] = True
            else:
                # 使用mootdx的自动最佳IP选择
                client_kwargs['bestip'] = True
                print("使用mootdx自动选择最佳服务器...")
            
            # 创建客户端
            client = Quotes.factory(**client_kwargs)
            
            return client
        except Exception as e:
            print(f"创建行情客户端失败: {e}")
            return None
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清理数据异常值（与AStockDataFetcher保持一致）
        
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
        
        # 处理成交量异常值
        if 'volume' in cleaned_df.columns:
            # 移除成交量为0或负数的记录
            cleaned_df = cleaned_df[cleaned_df['volume'] >= 0]
        
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
        if 'date' in cleaned_df.columns:
            date_col = 'date'
        elif 'datetime' in cleaned_df.columns:
            date_col = 'datetime'
        else:
            # 如果没有日期列，尝试使用索引
            if hasattr(cleaned_df.index, 'name') and cleaned_df.index.name == 'datetime':
                date_col = cleaned_df.index.name
                # 将索引转换为列
                cleaned_df = cleaned_df.reset_index()
            else:
                print("警告：未找到日期列，无法排序")
                return cleaned_df
                
        cleaned_df = cleaned_df.sort_values(date_col).reset_index(drop=True)
        
        # 移除重复的日期
        if date_col in cleaned_df.columns:
            cleaned_df = cleaned_df.drop_duplicates(subset=[date_col], keep='last')
        
        print(f"数据清洗完成：原始数据 {len(df)} 行，清洗后 {len(cleaned_df)} 行")
        return cleaned_df
    
    def normalize_stock_code(self, code: str) -> str:
        """
        标准化股票代码，自动添加交易所前缀
        
        Args:
            code: 用户输入的股票代码，可以是完整格式(sh.600000)或仅数字(600000)
            
        Returns:
            标准化后的股票代码，格式: sh.600000 / sz.000001 / bj.830799
        """
        # 去除空白字符并转为大写
        code = str(code).strip().upper()
        
        # 如果已经是完整格式(包含点)，直接返回
        if "." in code:
            return code.lower()
        
        # 如果不是6位数字，保持原样(可能是其他格式)
        if not code.isdigit() or len(code) != 6:
            print(f"⚠️  股票代码格式不正确: {code}")
            return code
        
        # 根据首位数字判断交易所
        first_digit = code[0]
        
        if first_digit == "6":
            # 上海交易所: 6xxxxx
            return f"sh.{code}"
        elif first_digit in ["0", "3"]:
            # 深圳交易所: 0xxxxx, 3xxxxx
            return f"sz.{code}"
        elif first_digit == "5":
            # 上海ETF: 5xxxxx
            return f"sh.{code}"
        elif first_digit == "1" and len(code) == 6 and code.startswith("15"):
            # 深圳ETF: 15xxxx (如159开头的ETF)
            return f"sz.{code}"
        elif first_digit in ["8", "9", "4"]:
            # 北京交易所: 8xxxxx, 4xxxxx, 9xxxxx
            return f"bj.{code}"
        else:
            # 未知格式，保持原样并提示
            print(f"⚠️  无法识别股票代码所属交易所: {code}")
            return code
    
    def _get_market_from_code(self, stock_code: str) -> int:
        """
        从股票代码获取市场类型
        
        Args:
            stock_code: 股票代码（如 sh.600000 或 600000）
            
        Returns:
            市场类型: 1=上海, 0=深圳, 其他=北交所等
        """
        code = self.normalize_stock_code(stock_code)
        
        if code.startswith('sh.'):
            return 1  # 上海
        elif code.startswith('sz.'):
            return 0  # 深圳
        elif code.startswith('bj.'):
            return 2  # 北京
        else:
            return 1  # 默认上海
    
    def _get_pure_code(self, stock_code: str) -> str:
        """
        获取纯数字股票代码
        
        Args:
            stock_code: 股票代码（如 sh.600000）
            
        Returns:
            纯数字代码（如 600000）
        """
        code = self.normalize_stock_code(stock_code)
        return code.split('.')[-1] if '.' in code else code
    
    def test_connection(self) -> bool:
        """
        测试mootdx连接是否正常
        
        Returns:
            连接成功返回True，否则返回False
        """
        try:
            client = self._get_quotes_client()
            if client is None:
                return False
                
            # 尝试获取股票数量来测试连接
            from mootdx import consts
            count = client.stock_count(market=consts.MARKET_SH)
            
            if count and count > 0:
                print(f"✅ mootdx连接测试成功，上海市场股票数量: {count}")
                return True
            else:
                print("❌ mootdx连接测试失败")
                return False
                
        except Exception as e:
            print(f"❌ mootdx连接测试异常: {e}")
            return False
    
    def login(self) -> bool:
        """
        登录/连接（为兼容AStockDataFetcher接口）
        
        Returns:
            连接成功返回True，否则返回False
        """
        if self.test_connection():
            self.is_connected = True
            print("✅ 已连接通达信行情服务器")
            return True
        else:
            self.is_connected = False
            print("❌ 连接通达信行情服务器失败")
            return False
    
    def logout(self):
        """
        登出（为兼容AStockDataFetcher接口）
        """
        self.is_connected = False
        print("已断开连接")
    
    def __enter__(self):
        """上下文管理器入口"""
        self.login()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.logout()
    
    def get_daily_data(
        self, 
        stock_code: str, 
        start_date: str, 
        end_date: str,
        frequency: str = 'd',
        adjustflag: str = '2'
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
            清理后的DataFrame，格式与AStockDataFetcher一致
        """
        try:
            # 标准化股票代码
            code = self.normalize_stock_code(stock_code)
            pure_code = self._get_pure_code(code)
            market = self._get_market_from_code(code)
            
            # 获取行情客户端
            client = self._get_quotes_client(market)
            if client is None:
                print("无法创建行情客户端")
                return pd.DataFrame()
            
            # 确定市场参数（1=上海, 0=深圳）
            # mootdx的市场参数：1=上海, 0=深圳
            market_param = market  # 1=上海, 0=深圳
            
            print(f"正在获取 {code} 的日K线数据 ({start_date} 至 {end_date})...")
            
            # 获取日线数据
            # 使用mootdx的标准k()接口获取A股日K线数据
            try:
                # 根据adjustflag映射到mootdx的复权参数
                adjust_map = {'1': 'hfq', '2': 'qfq', '3': None}  # 1=后复权, 2=前复权, 3=不复权
                mootdx_adjust = adjust_map.get(adjustflag, 'qfq')  # 默认前复权
                
                # 使用client.k()方法获取A股日K线数据
                data = client.k(
                    symbol=pure_code,        # 股票代码（6位数字）
                    begin=start_date,         # 开始日期
                    end=end_date,            # 结束日期
                    adjust=mootdx_adjust      # 复权类型
                )
                    
            except Exception as e:
                print(f"获取K线数据失败: {e}")
                return pd.DataFrame()
            
            if data is None or len(data) == 0:
                print("未获取到数据")
                return pd.DataFrame()
            
            # mootdx直接返回DataFrame，无需转换
            df = data
            
            # 重命名列以匹配标准格式
            # mootdx返回的字段名：date, open, high, low, close, volume, amount
            if 'date' in df.columns:
                df['datetime'] = pd.to_datetime(df['date'])
                df = df.drop(columns=['date'])
            elif hasattr(df.index, 'name') and df.index.name == 'datetime':
                # 如果datetime是索引名，将其转换为列
                df = df.reset_index()
            
            # 确保必需列存在
            required_columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount', 'code']
            for col in required_columns:
                if col not in df.columns:
                    if col == 'code':
                        df[col] = code
                    elif col in ['volume', 'amount']:
                        df[col] = 0
            
            # 按日期范围过滤数据
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            df = df[(df['datetime'] >= start_dt) & (df['datetime'] <= end_dt)]
            
            # 数据清洗
            cleaned_df = self._clean_data(df)
            
            return cleaned_df
            
        except Exception as e:
            print(f"获取日K线数据异常: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def get_minute_data(
        self, 
        stock_code: str, 
        start_date: str, 
        end_date: str,
        frequency: str = '30',
        adjustflag: str = '2'
    ) -> pd.DataFrame:
        """
        获取分钟K线数据
        
        Args:
            stock_code: 股票代码，格式：sh.600000 或 sz.000001
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
            frequency: 分钟频率，可选值：'1', '5', '15', '30', '60'
            adjustflag: 复权类型，'3'=不复权，'1'=后复权，'2'=前复权
            
        Returns:
            清理后的DataFrame，格式与AStockDataFetcher一致
        """
        try:
            # 标准化股票代码
            code = self.normalize_stock_code(stock_code)
            pure_code = self._get_pure_code(code)
            market = self._get_market_from_code(code)
            
            # 获取行情客户端
            client = self._get_quotes_client(market)
            if client is None:
                print("无法创建行情客户端")
                return pd.DataFrame()
            
            # 确定市场参数
            market_param = market  # 1=上海, 0=深圳
            
            print(f"正在获取 {code} 的{frequency}分钟K线数据 ({start_date} 至 {end_date})...")
            
            # 根据mootdx文档，频率映射：
            # 0->5分钟, 1->15分钟, 2->30分钟, 3->1小时
            freq_map = {
                '1': 0,      # 5分钟（mootdx不支持1分钟，用5分钟代替）
                '5': 0,      # 5分钟  
                '15': 1,     # 15分钟
                '30': 2,     # 30分钟
                '60': 3      # 1小时
            }
            
            mootdx_freq = freq_map.get(frequency, 2)  # 默认30分钟
            
            # 根据adjustflag映射到mootdx的复权参数
            adjust_map = {'1': 'hfq', '2': 'qfq', '3': None}  # 1=后复权, 2=前复权, 3=不复权
            mootdx_adjust = adjust_map.get(adjustflag, 'qfq')  # 默认前复权
            
            # 计算需要获取的K线数量（A股每天交易4小时）
            def calculate_required_klines(start_date: str, end_date: str, frequency: str) -> int:
                """根据时间段和频率计算需要获取的K线数量"""
                from datetime import datetime

                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                days_diff = (end_dt - start_dt).days + 1  # 包含结束日期

                # A股每天交易4小时，按分钟计算
                trading_minutes_per_day = 4 * 60  # 4小时 = 240分钟

                # 根据频率计算每天的数量
                if frequency == '5':
                    klines_per_day = trading_minutes_per_day // 5
                elif frequency == '15':
                    klines_per_day = trading_minutes_per_day // 15
                elif frequency == '30':
                    klines_per_day = trading_minutes_per_day // 30
                elif frequency == '60':
                    klines_per_day = trading_minutes_per_day // 60
                else:
                    klines_per_day = trading_minutes_per_day // 30  # 默认30分钟

                required_klines = days_diff * klines_per_day + 200  # 加上200缓冲
                return required_klines

            required_klines = calculate_required_klines(start_date, end_date, frequency)
            print(f"根据时间段计算需要获取约 {required_klines} 条{frequency}分钟K线数据")

            # 分批次获取数据
            all_data = None
            batch_size = 800  # 每批固定获取800条
            current_start = 0
            empty_batch_count = 0  # 记录连续空批次数
            max_empty_batches = 2   # 最多允许2次连续空批

            while current_start < required_klines and empty_batch_count < max_empty_batches:
                # 每批固定获取batch_size条，而不是动态计算
                current_offset = batch_size

                print(f"获取第 {current_start//batch_size + 1} 批{frequency}分钟数据：{current_offset} 条")

                try:
                    batch_data = client.bars(
                        frequency=mootdx_freq, # 频率
                        symbol=pure_code,        # 股票代码（6位数字）
                        start=current_start,    # 从指定位置开始
                        offset=current_offset,  # 获取指定数量
                        adjust=mootdx_adjust,   # 复权类型
                        market=market          # 市场参数
                    )

                    if batch_data is not None and not batch_data.empty:
                        if all_data is None:
                            all_data = batch_data
                        else:
                            # 合并DataFrame
                            all_data = pd.concat([all_data, batch_data], ignore_index=True)
                        current_start += current_offset
                        empty_batch_count = 0  # 重置空批计数器
                        print(f"  ✓ 批次获取成功，累计 {len(all_data)} 条数据")
                    else:
                        empty_batch_count += 1
                        print(f"  ⚠️  第 {current_start//batch_size + 1} 批{frequency}分钟数据为空（连续空批{empty_batch_count}次）")
                        if empty_batch_count >= max_empty_batches:
                            print(f"  ⚠️  连续{max_empty_batches}次获取失败，停止分批获取")
                            break
                        # 添加短暂延迟避免触发API限制
                        import time
                        time.sleep(1)
                except SyntaxError as e:
                    # 捕获mootdx内部语法错误
                    print(f"  ❌ mootdx内部语法错误（可能是库版本问题）: {e}")
                    print(f"  💡 建议：使用日线数据或升级mootdx库（pip install --upgrade mootdx）")
                    empty_batch_count += 1
                    if empty_batch_count >= max_empty_batches:
                        print(f"  ⚠️  连续{max_empty_batches}次获取失败，停止分批获取")
                        break
                    import time
                    time.sleep(1)
                except Exception as e:
                    print(f"  ❌ 批次获取异常: {e}")
                    empty_batch_count += 1
                    if empty_batch_count >= max_empty_batches:
                        print(f"  ⚠️  连续{max_empty_batches}次获取失败，停止分批获取")
                        break
                    import time
                    time.sleep(1)

            data = all_data if all_data is not None else pd.DataFrame()
            print(f"✅ {frequency}分钟数据分批获取完成，共获取 {len(data)} 条数据")

            if data is None or len(data) == 0:
                print(f"⚠️  未获取到{frequency}分钟数据")
                print("💡 建议使用日线数据进行缠论分析（日线更适合识别笔和线段）")
                return pd.DataFrame()

            # 调试信息：显示获取到的数据结构
            print(f"获取到的原始数据结构：{data.shape if not data.empty else '空数据'}")
            if not data.empty:
                print(f"数据列：{data.columns.tolist()}")
                print(f"数据样例：\n{data.head(2)}")

            # 重命名列以匹配标准格式
            df = data
            if 'date' in df.columns:
                df['datetime'] = pd.to_datetime(df['date'])
                df = df.drop(columns=['date'])
            elif 'time' in df.columns:
                df['datetime'] = pd.to_datetime(df['time'], format='%Y%m%d%H%M%S', errors='coerce')
                df = df.drop(columns=['time'])
            elif hasattr(df.index, 'name') and df.index.name == 'datetime':
                # 如果datetime是索引名，将其转换为列
                df = df.reset_index()
            elif hasattr(df.index, 'name') and df.index.name == 'date':
                # 如果date是索引名，将其转换为列
                df = df.reset_index()
                df['datetime'] = pd.to_datetime(df['date'])
                df = df.drop(columns=['date'])

            # 检查是否成功创建了datetime列
            if 'datetime' not in df.columns:
                print("❌ 错误：无法创建datetime列，可能是数据格式问题")
                print(f"可用列：{df.columns.tolist()}")
                print(f"索引信息：{df.index.name}")
                return pd.DataFrame()

            # 确保必需列存在
            required_columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount', 'code']
            for col in required_columns:
                if col not in df.columns:
                    if col == 'code':
                        df[col] = code
                    elif col in ['volume', 'amount']:
                        df[col] = 0

            # 按日期范围过滤数据（增加错误处理）
            try:
                start_dt = pd.to_datetime(start_date)
                end_dt = pd.to_datetime(end_date)

                # 确保datetime列是datetime类型
                df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')

                # 检查datetime列是否有有效数据
                if df['datetime'].isna().all():
                    print("❌ 错误：datetime列全部为空值")
                    return pd.DataFrame()

                # 按日期范围过滤
                original_len = len(df)
                df = df[(df['datetime'] >= start_dt) & (df['datetime'] <= end_dt)]

                if df.empty:
                    print(f"⚠️  警告：按日期范围过滤后数据为空")
                    print(f"数据时间范围：{start_date} 到 {end_date}")
                    return pd.DataFrame()
                else:
                    print(f"{frequency}分钟数据时间筛选：{original_len} -> {len(df)} 条")

            except Exception as filter_error:
                print(f"❌ 日期过滤出错：{filter_error}")
                return pd.DataFrame()

            # 数据清洗
            cleaned_df = self._clean_data(df)

            print(f"✅ 成功获取{frequency}分钟数据 {len(cleaned_df)} 条")
            return cleaned_df

        except Exception as e:
            print(f"获取分钟K线数据异常: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def get_hk_stock_data(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        data_type: str = 'daily',
        frequency: str = '30'
    ) -> pd.DataFrame:
        """
        获取港股数据
        
        Args:
            stock_code: 港股代码（格式如 00700.HK 或 700）
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
            data_type: 数据类型，'daily' 或 'minute'
            frequency: 分钟频率，仅当data_type='minute'时有效
            
        Returns:
            清理后的DataFrame
            
        Note:
            港股支持复权
        """
        try:
            # 标准化港股代码
            code = str(stock_code).strip()
            
            # 获取港股客户端
            # 港股使用market='ext'的Quotes客户端，测试稳定服务器
            hk_servers = [
                ('183.232.222.14', 7721),  # known HK server
                ('116.205.240.117', 7721),
                ('116.205.128.53', 7721),   # alternative server
                ('1124.71.66.200', 7721)   # backup server
            ]
            
            client = None
            for server_ip, server_port in hk_servers:
                try:
                    print(f"尝试港股服务器 {server_ip}:{server_port}...")
                    client = Quotes.factory(
                        market='ext',
                        server=(server_ip, server_port),
                        timeout=15
                    )
                    # 测试连接
                    test_data = client.bars(
                        frequency=9,
                        market=31,
                        symbol="00700",
                        start=0,
                        offset=1
                    )
                    if test_data is not None and not test_data.empty:
                        print(f"✓ 港股服务器 {server_ip}:{server_port} 连接成功")
                        break
                except Exception as e:
                    print(f"✗ 港股服务器 {server_ip}:{server_port} 连接失败: {e}")
                    client = None
                    continue
            
            if client is None:
                print("❌ 所有港股服务器连接失败，使用默认配置")
                client = Quotes.factory(market='ext')
            
            print(f"正在获取港股 {code} 的数据 ({start_date} 至 {end_date})...")
            
            # 港股市场参数限定为31
            hk_markets = [31]
            data = None
            
            # 尝试不同的港股市场参数
            for market_param in hk_markets:
                try:
                    if data_type == 'daily':
                        # 日线数据（港股支持复权）
                        test_data = client.bars(
                            frequency=9,        # 9=日线
                            market=market_param, # 港股市场参数
                            symbol=code,        # 港股代码
                            start=0,            # 从最新数据开始
                            offset=700,         # 获取最多700条数据
                            adjust='qfq'         # 港股支持复权，默认前复权
                        )
                        
                        if test_data is not None and len(test_data) > 0:
                            data = test_data
                            print(f"✓ 使用港股市场参数 {market_param} 成功获取日线数据")
                            break
                    else:
                        # 分钟频率映射：0->5分钟, 1->15分钟, 2->30分钟, 3->1小时
                        freq_map = {
                            '1': 0,      # 5分钟
                            '5': 0,      # 5分钟  
                            '15': 1,     # 15分钟
                            '30': 2,     # 30分钟
                            '60': 3      # 1小时
                        }
                        mootdx_freq = freq_map.get(frequency, 2)  # 默认30分钟
                        
                        # 计算需要获取的K线数量（港股每天交易5.5小时）
                        def calculate_required_klines(start_date: str, end_date: str, frequency: str) -> int:
                            """根据时间段和频率计算需要获取的K线数量"""
                            from datetime import datetime
                            
                            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                            days_diff = (end_dt - start_dt).days + 1  # 包含结束日期
                            
                            # 港股每天交易5.5小时，按分钟计算
                            trading_minutes_per_day = 5.5 * 60  # 5.5小时 = 330分钟
                            
                            # 根据频率计算每天的数量
                            if frequency == '5':
                                klines_per_day = trading_minutes_per_day // 5
                            elif frequency == '15':
                                klines_per_day = trading_minutes_per_day // 15
                            elif frequency == '30':
                                klines_per_day = trading_minutes_per_day // 30
                            elif frequency == '60':
                                klines_per_day = trading_minutes_per_day // 60
                            else:
                                klines_per_day = trading_minutes_per_day // 30  # 默认30分钟
                            
                            required_klines = days_diff * klines_per_day + 200  # 加上200缓冲
                            return required_klines
                        
                        required_klines = calculate_required_klines(start_date, end_date, frequency)
                        print(f"根据时间段计算需要获取约 {required_klines} 条港股 {frequency}分钟K线数据")
                        
                        # 分批次获取数据
                        all_data = None
                        batch_size = 700  # 每批固定获取700条
                        current_start = 0
                        empty_batch_count = 0  # 记录连续空批次数
                        max_empty_batches = 2   # 最多允许2次连续空批
                        
                        while current_start < required_klines and empty_batch_count < max_empty_batches:
                            # 每批固定获取batch_size条，而不是动态计算
                            current_offset = batch_size
                            
                            print(f"获取第 {current_start//batch_size + 1} 批港股数据（市场参数{market_param}）：{current_offset} 条")
                            
                            try:
                                batch_data = client.bars(
                                    frequency=mootdx_freq, # 频率
                                    market=market_param,    # 港股市场参数
                                    symbol=code,           # 港股代码
                                    start=current_start,    # 从指定位置开始
                                    offset=current_offset,  # 获取指定数量
                                    adjust='qfq'             # 港股支持复权，默认前复权
                                )
                                
                                if batch_data is not None and not batch_data.empty:
                                    if all_data is None:
                                        all_data = batch_data
                                    else:
                                        # 合并DataFrame
                                        all_data = pd.concat([all_data, batch_data], ignore_index=True)
                                    current_start += current_offset
                                    empty_batch_count = 0  # 重置空批计数器
                                    print(f"  ✓ 批次获取成功，累计 {len(all_data)} 条数据")
                                else:
                                    empty_batch_count += 1
                                    print(f"  ⚠️  第 {current_start//batch_size + 1} 批港股数据为空（连续空批{empty_batch_count}次）")
                                    if empty_batch_count >= max_empty_batches:
                                        print(f"  ⚠️  连续{max_empty_batches}次获取失败，停止分批获取")
                                        break
                                    # 添加短暂延迟避免触发API限制
                                    import time
                                    time.sleep(1)
                            except SyntaxError as e:
                                # 捕获mootdx内部语法错误
                                print(f"  ❌ mootdx内部语法错误（可能是库版本问题）: {e}")
                                print(f"  💡 建议：使用日线数据或升级mootdx库（pip install --upgrade mootdx）")
                                empty_batch_count += 1
                                if empty_batch_count >= max_empty_batches:
                                    print(f"  ⚠️  连续{max_empty_batches}次获取失败，停止分批获取")
                                    break
                                import time
                                time.sleep(1)
                            except Exception as e:
                                print(f"  ❌ 批次获取异常: {e}")
                                empty_batch_count += 1
                                if empty_batch_count >= max_empty_batches:
                                    print(f"  ⚠️  连续{max_empty_batches}次获取失败，停止分批获取")
                                    break
                                import time
                                time.sleep(1)
                        
                        if all_data is not None and not all_data.empty:
                            data = all_data
                            print(f"✅ 港股分批获取完成，共获取 {len(data)} 条数据")
                            print(f"✓ 使用港股市场参数 {market_param} 成功获取数据")
                            break
                        else:
                            print(f"⚠️  未获取到任何港股数据（市场参数 {market_param}）")
                            break
                        
                except Exception as e:
                    print(f"港股市场参数 {market_param} 获取失败: {e}")
                    continue
            
            if data is None or len(data) == 0:
                print("❌ 所有港股市场参数都尝试失败")
                return pd.DataFrame()
            
            if data is None or len(data) == 0:
                print("未获取到港股数据")
                return pd.DataFrame()
            
            # mootdx直接返回DataFrame，无需转换
            df = data
            
            # 调试信息：显示获取到的数据结构
            print(f"获取到的港股数据结构：{df.shape if not df.empty else '空数据'}")
            if not df.empty:
                print(f"数据列：{df.columns.tolist()}")
                print(f"数据样例：\n{df.head(2)}")
            
            # 处理mootdx返回的港股数据格式
            # 港股数据可能：DatetimeIndex + datetime列，可能有vol/volume列
            
            # 首先处理DatetimeIndex（如果存在）
            if hasattr(df.index, 'name') and isinstance(df.index, pd.DatetimeIndex):
                df['datetime'] = df.index
                df = df.reset_index(drop=True)  # 删除索引，不添加index列
            
            # 统一列名 - 安全处理datetime列
            if 'datetime' in df.columns:
                # 如果已有datetime列，确保其格式正确
                df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
            elif 'date' in df.columns:
                df['datetime'] = pd.to_datetime(df['date'])
                df = df.drop(columns=['date'])
            elif 'time' in df.columns:
                df['datetime'] = pd.to_datetime(df['time'], format='%Y%m%d%H%M%S', errors='coerce')
                df = df.drop(columns=['time'])
            
            # 处理重复的volume列（ETF数据通常有vol和volume两列）
            if 'vol' in df.columns and 'volume' in df.columns:
                # 优先使用volume列，删除vol列
                df = df.drop(columns=['vol'])
            elif 'vol' in df.columns:
                # 只有vol列，重命名为volume
                df = df.rename(columns={'vol': 'volume'})
            
            # 删除不必要的时间分解列（ETF数据特有的year, month, day, hour, minute列）
            time_decompose_cols = ['year', 'month', 'day', 'hour', 'minute']
            for col in time_decompose_cols:
                if col in df.columns:
                    df = df.drop(columns=[col])
            
            # 检查是否成功创建了datetime列
            if 'datetime' not in df.columns:
                print("❌ 错误：无法创建datetime列，可能是数据格式问题")
                print(f"可用列：{df.columns.tolist()}")
                return pd.DataFrame()
            
            # 确保必需列存在
            required_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = 0
            
            df['code'] = code
            
            # 数据清洗
            cleaned_df = self._clean_data(df)
            
            return cleaned_df
            
        except Exception as e:
            print(f"获取港股数据异常: {e}")
            return pd.DataFrame()
    
    def get_etf_data(
        self,
        etf_code: str,
        start_date: str,
        end_date: str,
        data_type: str = 'daily',
        frequency: str = '30'
    ) -> pd.DataFrame:
        """
        获取ETF数据
        
        Args:
            etf_code: ETF代码（格式如 sh.510300 或 510300）
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
            data_type: 数据类型，'daily' 或 'minute'
            frequency: 分钟频率，仅当data_type='minute'时有效
            
        Returns:
            清理后的DataFrame
            
        Note:
            ETF不支持复权，所有数据均为原始价格
        """
        try:
            # ETF代码通常以5开头（上海）或15开头（深圳）
            code = self.normalize_stock_code(etf_code)
            pure_code = self._get_pure_code(code)
            market = self._get_market_from_code(code)
            
            # 获取行情客户端
            client = self._get_quotes_client(market)
            
            print(f"正在获取ETF {code} 的数据 ({start_date} 至 {end_date})...")
            
            # 获取ETF数据（ETF不支持复权，统一使用bars方法）
            if data_type == 'daily':
                # ETF日线数据
                data = client.bars(
                    frequency=9,        # 9=日线
                    symbol=pure_code,   # ETF代码
                    start=0,            # 从最新数据开始
                    offset=800          # 获取最多800条数据
                    # ETF不支持复权，不传递adjust参数
                )
            else:
                # 分钟频率映射：0->5分钟, 1->15分钟, 2->30分钟, 3->1小时
                freq_map = {
                    '1': 0,      # 5分钟
                    '5': 0,      # 5分钟  
                    '15': 1,     # 15分钟
                    '30': 2,     # 30分钟
                    '60': 3      # 1小时
                }
                mootdx_freq = freq_map.get(frequency, 2)  # 默认30分钟
                
                # 计算需要获取的K线数量（ETF与A股相同，每天4小时交易）
                def calculate_required_klines(start_date: str, end_date: str, frequency: str) -> int:
                    """根据时间段和频率计算需要获取的K线数量"""
                    from datetime import datetime
                    
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                    days_diff = (end_dt - start_dt).days + 1  # 包含结束日期
                    
                    # A股每天交易4小时，按分钟计算
                    trading_minutes_per_day = 4 * 60  # 4小时 = 240分钟
                    
                    # 根据频率计算每天的数量
                    if frequency == '5':
                        klines_per_day = trading_minutes_per_day // 5
                    elif frequency == '15':
                        klines_per_day = trading_minutes_per_day // 15
                    elif frequency == '30':
                        klines_per_day = trading_minutes_per_day // 30
                    elif frequency == '60':
                        klines_per_day = trading_minutes_per_day // 60
                    else:
                        klines_per_day = trading_minutes_per_day // 30  # 默认30分钟
                    
                    required_klines = days_diff * klines_per_day + 200  # 加上200缓冲
                    return required_klines
                
                required_klines = calculate_required_klines(start_date, end_date, frequency)
                print(f"根据时间段计算需要获取约 {required_klines} 条ETF {frequency}分钟K线数据")
                
                # 分批次获取数据
                all_data = None
                batch_size = 800  # 每批固定获取800条
                current_start = 0
                
                while current_start < required_klines:
                    # 每批固定获取batch_size条，而不是动态计算
                    current_offset = batch_size
                    
                    print(f"获取第 {current_start//batch_size + 1} 批ETF数据：{current_offset} 条")
                    
                    batch_data = client.bars(
                        frequency=mootdx_freq, # 频率
                        symbol=pure_code,       # ETF代码
                        start=current_start,    # 从指定位置开始
                        offset=current_offset   # 获取指定数量
                        # ETF不支持复权，不传递adjust参数
                    )
                    
                    if batch_data is not None and not batch_data.empty:
                        if all_data is None:
                            all_data = batch_data
                        else:
                            # 合并DataFrame
                            all_data = pd.concat([all_data, batch_data], ignore_index=True)
                        current_start += current_offset
                    else:
                        print(f"第 {current_start//offset_per_batch + 1} 批ETF数据获取为空，停止获取")
                        break
                
                data = all_data if all_data is not None else pd.DataFrame()
                print(f"✅ ETF分批获取完成，共获取 {len(data)} 条数据")
            
            if data is None or len(data) == 0:
                print("未获取到ETF数据")
                return pd.DataFrame()
            
            # mootdx直接返回DataFrame，无需转换
            df = data
            
            # 调试信息：显示获取到的数据结构
            if data_type == 'minute':
                print(f"获取到的指数 {frequency}分钟数据结构：{df.shape if not df.empty else '空数据'}")
                if not df.empty:
                    print(f"数据列：{df.columns.tolist()}")
                    print(f"数据样例：\n{df.head(2)}")
            
            # 处理mootdx返回的港股数据格式
            # 港股数据可能：DatetimeIndex + datetime列，可能有vol/volume列
            
            # 首先处理DatetimeIndex（如果存在）
            if hasattr(df.index, 'name') and isinstance(df.index, pd.DatetimeIndex):
                df['datetime'] = df.index
                df = df.reset_index(drop=True)  # 删除索引，不添加index列
            
            # 统一列名 - 安全处理datetime列
            if 'datetime' in df.columns:
                # 如果已有datetime列，确保其格式正确
                df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
            elif 'date' in df.columns:
                df['datetime'] = pd.to_datetime(df['date'])
                df = df.drop(columns=['date'])
            elif 'time' in df.columns:
                df['datetime'] = pd.to_datetime(df['time'], format='%Y%m%d%H%M%S', errors='coerce')
                df = df.drop(columns=['time'])
            
            # 处理重复的volume列（ETF数据通常有vol和volume两列）
            if 'vol' in df.columns and 'volume' in df.columns:
                # 优先使用volume列，删除vol列
                df = df.drop(columns=['vol'])
            elif 'vol' in df.columns:
                # 只有vol列，重命名为volume
                df = df.rename(columns={'vol': 'volume'})
            
            # 删除不必要的时间分解列（ETF数据特有的year, month, day, hour, minute列）
            time_decompose_cols = ['year', 'month', 'day', 'hour', 'minute']
            for col in time_decompose_cols:
                if col in df.columns:
                    df = df.drop(columns=[col])
            
            # 检查是否成功创建了datetime列
            if data_type == 'minute' and 'datetime' not in df.columns:
                print("❌ 错误：无法创建datetime列，可能是数据格式问题")
                print(f"可用列：{df.columns.tolist()}")
                return pd.DataFrame()
            
            # 确保必需列存在
            required_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = 0
            
            df['code'] = code
            
            # 分钟数据按日期范围过滤（增加错误处理）
            if data_type == 'minute':
                try:
                    start_dt = pd.to_datetime(start_date)
                    end_dt = pd.to_datetime(end_date)
                    
                    # 确保datetime列是datetime类型
                    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
                    
                    # 检查datetime列是否有有效数据
                    if df['datetime'].isna().all():
                        print("❌ 错误：datetime列全部为空值")
                        return pd.DataFrame()
                    
                    # 按日期范围过滤
                    original_len = len(df)
                    df = df[(df['datetime'] >= start_dt) & (df['datetime'] <= end_dt)]
                    
                    if df.empty:
                        print(f"⚠️  警告：ETF数据按日期范围过滤后为空")
                        print(f"数据时间范围：{start_date} 到 {end_date}")
                        return pd.DataFrame()
                    else:
                        print(f"ETF数据时间筛选：{original_len} -> {len(df)} 条")
                        
                except Exception as filter_error:
                    print(f"❌ ETF日期过滤出错：{filter_error}")
                    return pd.DataFrame()
            
            # 数据清洗
            cleaned_df = self._clean_data(df)
            
            return cleaned_df
            
        except Exception as e:
            print(f"获取ETF数据异常: {e}")
            return pd.DataFrame()
    
    def get_index_data(
        self,
        index_code: str,
        start_date: str,
        end_date: str,
        data_type: str = 'daily',
        frequency: str = '30'
    ) -> pd.DataFrame:
        """
        获取指数数据
        
        Args:
            index_code: 指数代码（格式如 sh.000001 或 000001）
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
            data_type: 数据类型，'daily' 或 'minute'
            frequency: 分钟频率，仅当data_type='minute'时有效
            
        Returns:
            清理后的DataFrame
            
        Note:
            指数支持复权
        """
        try:
            # 指数代码通常以0开头（上证指数）或39开头（深证成指）
            code = self.normalize_stock_code(index_code)
            pure_code = self._get_pure_code(code)
            market = self._get_market_from_code(code)
            
            # 获取行情客户端
            client = self._get_quotes_client(market)
            
            print(f"正在获取指数 {code} 的数据 ({start_date} 至 {end_date})...")
            
            # 获取指数数据（指数不支持复权）
            if data_type == 'daily':
                # 使用client.index()方法获取A股指数日K线数据
                data = client.index(
                    frequency=9,        # 9=日线
                    symbol=pure_code,   # 指数代码（6位数字）
                    start=0,            # 从最新数据开始
                    offset=800,         # 获取最多800条数据
                    adjust='qfq'         # 指数支持复权，默认前复权
                )
            else:
                # 分钟频率映射：0->5分钟, 1->15分钟, 2->30分钟, 3->1小时
                freq_map = {
                    '1': 0,      # 5分钟
                    '5': 0,      # 5分钟  
                    '15': 1,     # 15分钟
                    '30': 2,     # 30分钟
                    '60': 3      # 1小时
                }
                mootdx_freq = freq_map.get(frequency, 2)  # 默认30分钟
                
                # 计算需要获取的K线数量（指数与A股相同，每天4小时交易）
                def calculate_required_klines(start_date: str, end_date: str, frequency: str) -> int:
                    """根据时间段和频率计算需要获取的K线数量"""
                    from datetime import datetime
                    
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                    days_diff = (end_dt - start_dt).days + 1  # 包含结束日期
                    
                    # A股每天交易4小时，按分钟计算
                    trading_minutes_per_day = 4 * 60  # 4小时 = 240分钟
                    
                    # 根据频率计算每天的数量
                    if frequency == '5':
                        klines_per_day = trading_minutes_per_day // 5
                    elif frequency == '15':
                        klines_per_day = trading_minutes_per_day // 15
                    elif frequency == '30':
                        klines_per_day = trading_minutes_per_day // 30
                    elif frequency == '60':
                        klines_per_day = trading_minutes_per_day // 60
                    else:
                        klines_per_day = trading_minutes_per_day // 30  # 默认30分钟
                    
                    required_klines = days_diff * klines_per_day + 200  # 加上200缓冲
                    return required_klines
                
                required_klines = calculate_required_klines(start_date, end_date, frequency)
                print(f"根据时间段计算需要获取约 {required_klines} 条指数 {frequency}分钟K线数据")
                
                # 分批次获取数据
                all_data = None
                batch_size = 800  # 每批固定获取800条
                current_start = 0
                
                while current_start < required_klines:
                    # 每批固定获取batch_size条，而不是动态计算
                    current_offset = batch_size
                    
                    print(f"获取第 {current_start//batch_size + 1} 批指数数据：{current_offset} 条")
                    
                    batch_data = client.index(
                        frequency=mootdx_freq, # 频率
                        symbol=pure_code,       # 指数代码
                        start=current_start,    # 从指定位置开始
                        offset=current_offset,   # 获取指定数量
                        adjust='qfq'             # 指数支持复权，默认前复权
                    )
                    
                    if batch_data is not None and not batch_data.empty:
                        if all_data is None:
                            all_data = batch_data
                        else:
                            # 合并DataFrame
                            all_data = pd.concat([all_data, batch_data], ignore_index=True)
                        current_start += current_offset
                    else:
                        print(f"第 {current_start//offset_per_batch + 1} 批指数数据获取为空，停止获取")
                        break
                
                data = all_data if all_data is not None else pd.DataFrame()
                print(f"✅ 指数分批获取完成，共获取 {len(data)} 条数据")
            
            if data is None or len(data) == 0:
                print("未获取到指数数据")
                return pd.DataFrame()
            
            # mootdx直接返回DataFrame，无需转换
            df = data
            
            # 调试信息：显示获取到的数据结构
            if data_type == 'minute':
                print(f"获取到的指数 {frequency}分钟数据结构：{df.shape if not df.empty else '空数据'}")
                if not df.empty:
                    print(f"数据列：{df.columns.tolist()}")
                    print(f"数据样例：\n{df.head(2)}")
            
            # 处理mootdx返回的港股数据格式
            # 港股数据可能：DatetimeIndex + datetime列，可能有vol/volume列
            
            # 首先处理DatetimeIndex（如果存在）
            if hasattr(df.index, 'name') and isinstance(df.index, pd.DatetimeIndex):
                df['datetime'] = df.index
                df = df.reset_index(drop=True)  # 删除索引，不添加index列
            
            # 统一列名 - 安全处理datetime列
            if 'datetime' in df.columns:
                # 如果已有datetime列，确保其格式正确
                df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
            elif 'date' in df.columns:
                df['datetime'] = pd.to_datetime(df['date'])
                df = df.drop(columns=['date'])
            elif 'time' in df.columns:
                df['datetime'] = pd.to_datetime(df['time'], format='%Y%m%d%H%M%S', errors='coerce')
                df = df.drop(columns=['time'])
            
            # 处理重复的volume列（ETF数据通常有vol和volume两列）
            if 'vol' in df.columns and 'volume' in df.columns:
                # 优先使用volume列，删除vol列
                df = df.drop(columns=['vol'])
            elif 'vol' in df.columns:
                # 只有vol列，重命名为volume
                df = df.rename(columns={'vol': 'volume'})
            
            # 删除不必要的时间分解列（ETF数据特有的year, month, day, hour, minute列）
            time_decompose_cols = ['year', 'month', 'day', 'hour', 'minute']
            for col in time_decompose_cols:
                if col in df.columns:
                    df = df.drop(columns=[col])
            
            # 检查是否成功创建了datetime列
            if data_type == 'minute' and 'datetime' not in df.columns:
                print("❌ 错误：无法创建datetime列，可能是数据格式问题")
                print(f"可用列：{df.columns.tolist()}")
                return pd.DataFrame()
            
            # 确保必需列存在
            required_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = 0
            
            df['code'] = code
            
            # 分钟数据按日期范围过滤（增加错误处理）
            if data_type == 'minute':
                try:
                    start_dt = pd.to_datetime(start_date)
                    end_dt = pd.to_datetime(end_date)
                    
                    # 确保datetime列是datetime类型
                    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
                    
                    # 检查datetime列是否有有效数据
                    if df['datetime'].isna().all():
                        print("❌ 错误：datetime列全部为空值")
                        return pd.DataFrame()
                    
                    # 按日期范围过滤
                    original_len = len(df)
                    df = df[(df['datetime'] >= start_dt) & (df['datetime'] <= end_dt)]
                    
                    if df.empty:
                        print(f"⚠️  警告：ETF数据按日期范围过滤后为空")
                        print(f"数据时间范围：{start_date} 到 {end_date}")
                        return pd.DataFrame()
                    else:
                        print(f"ETF数据时间筛选：{original_len} -> {len(df)} 条")
                        
                except Exception as filter_error:
                    print(f"❌ ETF日期过滤出错：{filter_error}")
                    return pd.DataFrame()
            
            # 数据清洗
            cleaned_df = self._clean_data(df)
            
            return cleaned_df
            
        except Exception as e:
            print(f"获取指数数据异常: {e}")
            return pd.DataFrame()
    
    def get_realtime_quotes(self, stock_codes: List[str]) -> pd.DataFrame:
        """
        获取实时行情报价
        
        Args:
            stock_codes: 股票代码列表，格式：['600000', '000001'] 或 ['sh.600000', 'sz.000001']
            
        Returns:
            实时行情DataFrame
        """
        try:
            client = self._get_quotes_client()
            if client is None:
                print("无法创建行情客户端")
                return pd.DataFrame()
            
            # 标准化股票代码
            normalized_codes = []
            for code in stock_codes:
                normalized_code = self.normalize_stock_code(code)
                pure_code = self._get_pure_code(normalized_code)
                normalized_codes.append(pure_code)
            
            print(f"正在获取 {len(normalized_codes)} 只股票的实时行情...")
            
            # 获取实时行情
            quotes_data = client.quotes(symbol=normalized_codes)
            
            if quotes_data is None or len(quotes_data) == 0:
                print("未获取到实时行情数据")
                return pd.DataFrame()
            
            # 转换为DataFrame
            df = pd.DataFrame(quotes_data)
            
            print(f"✅ 成功获取 {len(df)} 只股票的实时行情")
            return df
            
        except Exception as e:
            print(f"获取实时行情异常: {e}")
            return pd.DataFrame()


    def test_hk_daily_data(self):
        """
        测试港股日线数据获取功能
        """
        print("\n" + "=" * 50)
        print("港股日线数据获取测试")
        print("=" * 50)
        
        # 测试港股代码列表
        hk_test_codes = ["00700", "00388", "01299", "02318", "00005"]  # 腾讯、港交所、友邦、中国平安、汇丰
        
        for hk_code in hk_test_codes:
            print(f"\n【测试港股代码: {hk_code}】")
            try:
                hk_data = self.get_hk_stock_data(
                    stock_code=hk_code,
                    start_date="2024-01-01",
                    end_date="2025-12-29",
                    data_type='daily'
                )
                
                if not hk_data.empty:
                    print(f"✅ {hk_code} 港股日线数据获取成功")
                    print(f"   数据形状: {hk_data.shape}")
                    print(f"   数据列: {hk_data.columns.tolist()}")
                    
                    if 'datetime' in hk_data.columns:
                        print(f"   时间范围: {hk_data['datetime'].min().date()} 到 {hk_data['datetime'].max().date()}")
                    
                    if 'close' in hk_data.columns:
                        latest_price = hk_data['close'].iloc[-1]
                        print(f"   最新价格: {latest_price:.2f}")
                    
                    # 显示前3条数据
                    print("   数据样例:")
                    print(hk_data.head(3)[['datetime', 'open', 'high', 'low', 'close', 'volume']].to_string(index=False))
                    
                else:
                    print(f"❌ {hk_code} 港股日线数据获取失败")
                    
            except Exception as e:
                print(f"❌ {hk_code} 测试异常: {e}")
        
        print("\n" + "=" * 50)
        print("港股日线数据测试完成")
        print("=" * 50)


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("MootdxDataFetcher 测试")
    print("=" * 60)
    
    # 使用上下文管理器自动连接
    with MootdxDataFetcher() as fetcher:
        
        print("\n【测试0：连接测试】")
        connection_ok = fetcher.test_connection()
        print(f"连接状态: {'✅ 正常' if connection_ok else '❌ 异常'}")
        
        if not connection_ok:
            print("连接失败，后续测试可能无法进行")
        
        print("\n【测试1：获取A股日K线数据】")
        daily_data = fetcher.get_daily_data(
            stock_code="600000",
            start_date="2020-12-01",
            end_date="2025-12-29"
        )
        if not daily_data.empty:
            print("\n日K线数据样例：")
            print(daily_data.head())
            print(f"\n数据列: {daily_data.columns.tolist()}")
            print(f"数据类型:\n{daily_data.dtypes}")
        else:
            print("未获取到日K线数据")
        
        print("\n【测试2：获取A股分钟K线数据】")
        minute_data = fetcher.get_minute_data(
            stock_code="000001",
            start_date="2025-05-25",
            end_date="2025-12-29",
            frequency="30"
        )
        if not minute_data.empty:
            print("\n分钟K线数据样例：")
            print(minute_data.head())
            print(f"\n数据列: {minute_data.columns.tolist()}")
        else:
            print("未获取到分钟K线数据")
        
        print("\n【测试3：获取ETF数据】")
        etf_data = fetcher.get_etf_data(
            etf_code="588000",
            start_date="2025-01-01",
            end_date="2025-12-29"
        )
        if not etf_data.empty:
            print("\nETF数据样例：")
            print(etf_data.head())
        else:
            print("未获取到ETF数据")
        
        print("\n【测试4：获取指数数据】")
        index_data = fetcher.get_index_data(
            index_code="000001",
            start_date="2024-12-01",
            end_date="2025-12-29"
        )
        if not index_data.empty:
            print("\n指数数据样例：")
            print(index_data.head())
        else:
            print("未获取到指数数据")
        
        print("\n【测试5：获取港股日线数据】")
        hk_daily_data = fetcher.get_hk_stock_data(
            stock_code="00700",
            start_date="2024-01-01",
            end_date="2025-12-29",
            data_type='daily'
        )
        if not hk_daily_data.empty:
            print("\n港股日线数据样例：")
            print(hk_daily_data.head())
            print(f"\n港股日线数据列: {hk_daily_data.columns.tolist()}")
            print(f"数据时间范围: {hk_daily_data['datetime'].min()} 到 {hk_daily_data['datetime'].max()}")
        else:
            print("未获取到港股日线数据")
        
        print("\n【测试6：获取港股分钟数据】")
        hk_minute_data = fetcher.get_hk_stock_data(
            stock_code="00700",
            start_date="2025-12-01",
            end_date="2025-12-29",
            data_type='minute',
            frequency='30'
        )
        if not hk_minute_data.empty:
            print("\n港股分钟数据样例：")
            print(hk_minute_data.head())
            print(f"\n港股分钟数据列: {hk_minute_data.columns.tolist()}")
            print(f"数据时间范围: {hk_minute_data['datetime'].min()} 到 {hk_minute_data['datetime'].max()}")
        else:
            print("未获取到港股分钟数据")
        
        print("\n【测试7：专门的港股日线数据测试】")
        fetcher.test_hk_daily_data()
        
        # print("\n【测试8：获取实时行情】")
        # realtime_data = fetcher.get_realtime_quotes(["600000", "000001", "000300"])
        # if not realtime_data.empty:
        #     print("\n实时行情数据样例：")
        #     print(realtime_data.head())
        # else:
        #     print("未获取到实时行情数据")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
