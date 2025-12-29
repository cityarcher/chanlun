# baostock_data_fetcher.py - BaoStock数据获取器

## 📋 文件概述

`baostock_data_fetcher.py` 是基于BaoStock库的A股数据获取工具，提供日K线、分钟K线、股票基本信息等数据获取功能，包含完整的数据清洗和异常值处理逻辑。

## 🎯 主要功能

### 核心特性
- **数据获取**：支持日K线和分钟K线数据
- **数据清洗**：自动处理异常值、缺失值
- **复权支持**：支持前复权、后复权、不复权
- **批量获取**：支持多只股票批量数据获取
- **上下文管理**：支持with语句自动登录/登出

## 🏗️ 类说明

### AStockDataFetcher类

#### 类属性
```python
class AStockDataFetcher:
    """A股数据获取器"""
```
- `is_logged_in`：登录状态标识

## 📖 方法详解

### 基础方法

#### `__init__(self)`
初始化数据获取器

```python
def __init__(self)
```
- 创建数据获取器实例
- 初始化登录状态为False

#### `login(self) -> bool`
登录BaoStock

```python
def login(self) -> bool
```

**返回值**：
- 登录成功返回True，失败返回False

**功能**：
- 调用`bs.login()`登录BaoStock服务
- 检查登录结果，更新`is_logged_in`状态
- 显示登录成功或失败信息

#### `logout(self)`
登出BaoStock

```python
def logout(self)
```

**功能**：
- 调用`bs.logout()`登出BaoStock服务
- 更新`is_logged_in`状态为False
- 显示登出信息

### 数据获取方法

#### `get_daily_data(self, stock_code, start_date, end_date, frequency='d', adjustflag='2')`
获取日K线数据

```python
def get_daily_data(
    self, 
    stock_code: str, 
    start_date: str, 
    end_date: str,
    frequency: str = 'd',
    adjustflag: str = '2'
) -> pd.DataFrame
```

**参数说明**：
- `stock_code`：股票代码，格式：sh.600000 或 sz.000001
- `start_date`：开始日期，格式：YYYY-MM-DD
- `end_date`：结束日期，格式：YYYY-MM-DD
- `frequency`：频率，'d'=日线，'w'=周线，'m'=月线，默认'd'
- `adjustflag`：复权类型
  - '3' = 不复权
  - '1' = 后复权
  - '2' = 前复权（默认）

**返回值**：
- 清理后的DataFrame，包含列：datetime, open, high, low, close, volume, amount等

**数据列说明**：
- `date`：日期（字符串）
- `code`：股票代码
- `open`：开盘价
- `high`：最高价
- `low`：最低价
- `close`：收盘价
- `volume`：成交量
- `amount`：成交额
- `adjustflag`：复权类型
- `turn`：换手率
- `tradestatus`：交易状态
- `pctChg`：涨跌幅
- `isST`：是否ST股

**功能流程**：
1. 检查登录状态，未登录则自动登录
2. 调用`bs.query_history_k_data_plus()`获取数据
3. 转换为DataFrame格式
4. 添加`datetime`列
5. 调用`_clean_data()`清洗数据
6. 返回清理后的DataFrame

**使用示例**：
```python
with AStockDataFetcher() as fetcher:
    data = fetcher.get_daily_data(
        stock_code="sh.600000",
        start_date="2024-01-01",
        end_date="2025-12-29",
        frequency="d",
        adjustflag="2"  # 前复权
    )
    print(data.head())
```

#### `get_minute_data(self, stock_code, start_date, end_date, frequency='30', adjustflag='2')`
获取分钟K线数据

```python
def get_minute_data(
    self, 
    stock_code: str, 
    start_date: str, 
    end_date: str,
    frequency: str = '30',
    adjustflag: str = '2'
) -> pd.DataFrame
```

**参数说明**：
- `stock_code`：股票代码，格式：sh.600000 或 sz.000001
- `start_date`：开始日期，格式：YYYY-MM-DD
- `end_date`：结束日期，格式：YYYY-MM-DD
- `frequency`：分钟频率
  - '5' = 5分钟
  - '15' = 15分钟
  - '30' = 30分钟（默认）
  - '60' = 60分钟
- `adjustflag`：复权类型，默认前复权

**返回值**：
- 清理后的DataFrame，包含datetime, open, high, low, close, volume, amount等列

**数据处理**：
1. 合并`date`和`time`列为`datetime`
2. 提取time中的时间部分（HH:MM:SS）
3. 转换为datetime类型
4. 调用`_clean_data()`清洗数据

**使用示例**：
```python
with AStockDataFetcher() as fetcher:
    data = fetcher.get_minute_data(
        stock_code="sh.600000",
        start_date="2024-12-01",
        end_date="2024-12-31",
        frequency="30"
    )
    print(data.head())
```

#### `get_stock_basic_info(self, stock_code: str)`
获取股票基本信息

```python
def get_stock_basic_info(self, stock_code: str) -> pd.DataFrame
```

**参数说明**：
- `stock_code`：股票代码

**返回值**：
- 股票基本信息DataFrame

**使用示例**：
```python
with AStockDataFetcher() as fetcher:
    info = fetcher.get_stock_basic_info("sh.600000")
    print(info)
```

#### `batch_get_data(self, stock_codes, start_date, end_date, data_type='daily', **kwargs)`
批量获取多只股票数据

```python
def batch_get_data(
    self, 
    stock_codes: List[str], 
    start_date: str, 
    end_date: str,
    data_type: str = 'daily',
    **kwargs
) -> dict
```

**参数说明**：
- `stock_codes`：股票代码列表
- `start_date`：开始日期
- `end_date`：结束日期
- `data_type`：数据类型，'daily' 或 'minute'
- `**kwargs`：其他参数（frequency, adjustflag等）

**返回值**：
- 字典：{stock_code: DataFrame}

**功能**：
- 遍历股票代码列表
- 依次调用`get_daily_data()`或`get_minute_data()`
- 返回成功获取的数据字典

**使用示例**：
```python
with AStockDataFetcher() as fetcher:
    stocks = ["sh.600000", "sz.000001", "sh.600519"]
    batch_data = fetcher.batch_get_data(
        stock_codes=stocks,
        start_date="2024-01-01",
        end_date="2024-12-31",
        data_type="daily"
    )
    for code, data in batch_data.items():
        print(f"{code}: {len(data)} 行数据")
```

### 数据清洗方法

#### `_clean_data(self, df: pd.DataFrame)`
清理数据异常值

```python
def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame
```

**参数说明**：
- `df`：原始数据DataFrame

**返回值**：
- 清理后的DataFrame

**清洗步骤**：

1. **日期转换**：
   ```python
   # 将date/datetime列转换为datetime类型
   df['datetime'] = pd.to_datetime(df['date'])
   ```

2. **数值转换**：
   ```python
   # 将字符串类型的数值列转换为float
   numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
   for col in numeric_columns:
       df[col] = pd.to_numeric(df[col], errors='coerce')
   ```

3. **价格异常值处理**：
   - 移除价格为0或负数的记录
   - 处理极端异常值（偏离超过3个标准差）
   ```python
   mean_val = cleaned_df[col].mean()
   std_val = cleaned_df[col].std()
   upper_bound = mean_val + 3 * std_val
   lower_bound = mean_val - 3 * std_val
   cleaned_df = cleaned_df[
       (cleaned_df[col] >= lower_bound) & 
       (cleaned_df[col] <= upper_bound)
   ]
   ```

4. **成交量异常值处理**：
   - 移除成交量为0或负数的记录
   - 处理极端异常值（偏离超过5个标准差）
   ```python
   volume_upper = volume_mean + 5 * volume_std
   cleaned_df = cleaned_df[cleaned_df['volume'] <= volume_upper]
   ```

5. **价格逻辑检查**：
   ```python
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
   ```

6. **去重和排序**：
   - 按日期排序
   - 移除重复的日期记录
   ```python
   cleaned_df = cleaned_df.sort_values(date_col)
   cleaned_df = cleaned_df.drop_duplicates(subset=[date_col], keep='last')
   ```

**输出信息**：
```python
数据清洗完成：原始数据 492 行，清洗后 492 行
```

### 上下文管理器

#### `__enter__(self)`
上下文管理器入口

```python
def __enter__(self)
```
- 自动调用`login()`
- 返回self实例

#### `__exit__(self, exc_type, exc_val, exc_tb)`
上下文管理器出口

```python
def __exit__(self, exc_type, exc_val, exc_tb)
```
- 自动调用`logout()`
- 确保资源正确释放

## 💡 使用示例

### 基本使用

#### 日K线数据获取

```python
from baostock_data_fetcher import AStockDataFetcher

# 使用上下文管理器
with AStockDataFetcher() as fetcher:
    data = fetcher.get_daily_data(
        stock_code="sh.600000",
        start_date="2024-01-01",
        end_date="2024-12-31",
        frequency="d",
        adjustflag="2"  # 前复权
    )
    
    print(f"获取到 {len(data)} 条数据")
    print(data.head())
```

#### 分钟K线数据获取

```python
with AStockDataFetcher() as fetcher:
    data = fetcher.get_minute_data(
        stock_code="sh.600000",
        start_date="2024-12-01",
        end_date="2024-12-31",
        frequency="30"
    )
    
    print(f"获取到 {len(data)} 条30分钟数据")
    print(data.head())
```

#### 批量获取数据

```python
with AStockDataFetcher() as fetcher:
    stocks = ["sh.600000", "sz.000001", "sh.600519"]
    batch_data = fetcher.batch_get_data(
        stock_codes=stocks,
        start_date="2024-01-01",
        end_date="2024-12-31",
        data_type="daily"
    )
    
    print(f"成功获取 {len(batch_data)} 只股票数据")
    for code, df in batch_data.items():
        print(f"{code}: {len(df)} 条数据")
```

### 高级使用

#### 手动登录/登出

```python
from baostock_data_fetcher import AStockDataFetcher

fetcher = AStockDataFetcher()

# 手动登录
if fetcher.login():
    # 获取数据
    data = fetcher.get_daily_data("sh.600000", "2024-01-01", "2024-12-31")
    print(data)
    
    # 手动登出
    fetcher.logout()
```

#### 复权类型选择

```python
with AStockDataFetcher() as fetcher:
    # 不复权
    data1 = fetcher.get_daily_data(
        "sh.600000", "2024-01-01", "2024-12-31",
        adjustflag="3"
    )
    
    # 后复权
    data2 = fetcher.get_daily_data(
        "sh.600000", "2024-01-01", "2024-12-31",
        adjustflag="1"
    )
    
    # 前复权
    data3 = fetcher.get_daily_data(
        "sh.600000", "2024-01-01", "2024-12-31",
        adjustflag="2"
    )
```

## 📊 数据格式

### 输出DataFrame列说明

| 列名 | 类型 | 说明 |
|-----|------|------|
| datetime | datetime | 日期时间 |
| code | str | 股票代码 |
| open | float | 开盘价 |
| high | float | 最高价 |
| low | float | 最低价 |
| close | float | 收盘价 |
| volume | float | 成交量 |
| amount | float | 成交额 |
| adjustflag | str | 复权类型 |
| turn | float | 换手率 |
| tradestatus | str | 交易状态 |
| pctChg | float | 涨跌幅 |
| isST | str | 是否ST股 |

### 数据示例

```
datetime                code    open    high     low   close    volume      amount
2024-01-02 00:00:00  sh.600000  10.50   10.80   10.45   10.78  1500000  16000000
2024-01-03 00:00:00  sh.600000  10.78   10.90   10.70   10.85  1200000  13000000
2024-01-04 00:00:00  sh.600000  10.85   11.00   10.80   10.95  1800000  19500000
```

## ⚙️ 配置选项

### BaoStock服务

- **免费使用**：BaoStock提供免费的数据服务
- **无需注册**：无需API Key，直接使用
- **数据范围**：支持A股、指数、基金等

### 复权类型

| 类型 | 参数 | 说明 |
|-----|------|------|
| 不复权 | '3' | 原始价格，不复权处理 |
| 前复权 | '2' | 向前复权，适合长期分析 |
| 后复权 | '1' | 向后复权，适合短期分析 |

### K线频率

#### 日线频率
- 'd'：日线
- 'w'：周线
- 'm'：月线

#### 分钟频率
- '5'：5分钟K线
- '15'：15分钟K线
- '30'：30分钟K线
- '60'：60分钟K线

## 🔍 数据清洗规则

### 价格异常值
- **规则**：剔除偏离均值超过3个标准差的数据
- **原因**：防止错误数据影响分析结果
- **影响**：一般只影响极少数异常K线

### 成交量异常值
- **规则**：剔除偏离均值超过5个标准差的数据
- **原因**：成交量波动较大，放宽异常值阈值
- **影响**：过滤异常成交日（如分红送股日）

### 价格逻辑检查
- **规则**：
  - high ≥ low
  - high ≥ open/close
  - low ≤ open/close
  - open > 0, close > 0
- **原因**：确保K线数据逻辑正确
- **影响**：过滤数据错误的K线

## ⚠️ 注意事项

1. **登录状态**：
   - 使用上下文管理器自动管理登录/登出
   - 避免频繁登录/登出

2. **数据范围**：
   - BaoStock数据可能有一定延迟
   - 建议在工作日交易时间外使用

3. **股票代码**：
   - 必须包含交易所前缀（sh./sz.）
   - 6位数字代码需要标准化

4. **日期格式**：
   - 必须使用YYYY-MM-DD格式
   - 结束日期不能早于开始日期

5. **分钟数据**：
   - 分钟数据获取较慢
   - 建议缩短时间范围
   - 5分钟数据可能不稳定

6. **数据清洗**：
   - 自动清洗会减少数据量
   - 查看清洗后的数据量
   - 如数据过少，检查清洗规则

## 🐛 常见问题

### Q1: 登录失败

**原因**：网络问题或BaoStock服务不可用

**解决方法**：
```python
# 检查网络连接
import bs as bs
lg = bs.login()
print(f"登录状态: {lg.error_code} - {lg.error_msg}")
```

### Q2: 获取到空数据

**原因**：
- 股票代码错误
- 日期范围无效
- 数据不存在（如新股）

**解决方法**：
```python
# 检查股票基本信息
info = fetcher.get_stock_basic_info("sh.600000")
print(info)
```

### Q3: 数据清洗后数据量过少

**原因**：数据质量差或异常值多

**解决方法**：
- 检查原始数据
- 调整清洗规则
- 选择其他股票

### Q4: 分钟数据获取很慢

**原因**：BaoStock分钟数据接口限制

**解决方法**：
- 缩短时间范围
- 增大K线周期（如用30分钟代替5分钟）
- 使用日线数据

## 📚 相关文档

- [BaoStock官方文档](http://baostock.com/)
- [缠论分析主程序](baostock_chanlun.md)
- [缠论核心算法](chanlun_processor.md)
