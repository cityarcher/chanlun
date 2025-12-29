# mootdx_chanlun.py - Mootdx版缠论分析主程序

## 📋 文件概述

`mootdx_chanlun.py` 是基于Mootdx数据源的缠论K线分析主程序，支持多市场数据获取（A股、ETF、港股、指数），提供完整的日K线和分钟K线分析功能。

## 🎯 主要功能

### 核心特性
- **多市场支持**：A股、ETF、港股、指数、北交所
- **智能识别**：自动识别股票代码所属市场
- **灵活代码**：支持多种股票代码格式
- **实时数据**：相对实时的数据获取
- **多服务器**：自动选择最优服务器
- **缠论分析**：自动识别分型、笔等缠论要素
- **可视化输出**：支持Plotly和Matplotlib两种可视化方式
- **HTML导出**：自动保存分析结果为HTML文件

## 🏗️ 函数说明

### 工具函数

#### `get_previous_workday()`
获取上一个工作日

```python
def get_previous_workday() -> str
```
- **返回值**：上一个工作日的日期字符串（YYYY-MM-DD格式）
- **说明**：跳过周末（周六、周日）

#### `is_workday(date=None)`
判断是否为工作日

```python
def is_workday(date=None) -> bool
```
- **参数**：
  - `date`：日期对象，默认为当前日期
- **返回值**：如果是工作日返回True，否则返回False

#### `get_default_end_date()`
获取默认结束日期

```python
def get_default_end_date() -> str
```
- **返回值**：如果今天是工作日则返回今天，否则返回上一个工作日
- **说明**：用于智能设置分析截止日期

### 市场类型识别

#### `get_market_type(stock_code: str) -> str`
根据股票代码判断市场类型

```python
def get_market_type(stock_code: str) -> str
```

**参数说明**：
- `stock_code`：股票代码

**返回值**：
- 市场类型：'stock', 'etf', 'index', 'hk'

**识别规则**：
- 港股：`.`在代码中且包含`HK`，或5位以内数字
- ETF：以`5`开头，或以`15`开头且长度为6
- 指数：以`000`、`399`、`880`开头
- A股：其他情况

**使用示例**：
```python
print(get_market_type("600000"))    # stock
print(get_market_type("588000"))    # etf
print(get_market_type("000001"))    # index
print(get_market_type("00700"))     # hk
```

### 核心函数

#### `analyze_stock(stock_code, start_date, end_date, data_type='daily', frequency='30')`
分析单只股票的缠论数据

```python
def analyze_stock(stock_code, start_date, end_date, data_type='daily', frequency='30')
```

**参数说明**：
- `stock_code`：股票代码（支持多市场格式）
- `start_date`：开始日期（格式：YYYY-MM-DD）
- `end_date`：结束日期（格式：YYYY-MM-DD）
- `data_type`：数据类型，'daily' 或 'minute'，默认为 'daily'
- `frequency`：分钟K线周期，'5'/'15'/'30'/'60'，默认为 '30'

**返回值**：
- 包含缠论分析结果的DataFrame，如果失败则返回None

**功能流程**：
1. 识别市场类型
2. 使用MootdxDataFetcher获取相应市场数据
3. 使用ChanlunProcessor进行缠论分析
4. 显示简要统计信息

**使用示例**：
```python
# 分析A股
result = analyze_stock("600000", "2024-01-01", "2025-12-29")

# 分析港股
result = analyze_stock("00700", "2024-01-01", "2025-12-29")

# 分析ETF
result = analyze_stock("588000", "2024-01-01", "2025-12-29")

# 分析指数
result = analyze_stock("000001", "2024-01-01", "2025-12-29")
```

#### `normalize_stock_code(code: str) -> str`
标准化股票代码，自动添加交易所前缀

```python
def normalize_stock_code(code: str) -> str
```

**参数说明**：
- `code`：用户输入的股票代码，可以是完整格式(sh.600000)或仅数字(600000)

**返回值**：
- 标准化后的股票代码，格式：sh.600000 / sz.000001 / bj.830799

**转换规则**：
- 港股：直接返回（00700或00700.HK）
- 首位数字为6：上海交易所 → `sh.代码`
- 首位数字为0或3：深圳交易所 → `sz.代码`
- 首位数字为5：上海ETF → `sh.代码`
- 首位数字为1且以15开头：深圳ETF → `sz.代码`
- 首位数字为8、9、4：北京交易所 → `bj.代码`
- 其他格式：保持原样并提示

**使用示例**：
```python
print(normalize_stock_code("600000"))     # sh.600000
print(normalize_stock_code("000001"))     # sz.000001
print(normalize_stock_code("00700"))      # 00700
print(normalize_stock_code("588000"))     # sh.588000
print(normalize_stock_code("159915"))     # sz.159915
```

### 用户交互

#### `get_user_input()`
获取用户输入

```python
def get_user_input() -> tuple
```

**返回值**：
- 元组：(stock_code, start_date, end_date, data_type, frequency)

**交互流程**：
1. 输入股票代码（默认：600000）
2. 自动标准化股票代码
3. 输入开始日期（默认：2024-01-01）
4. 输入结束日期（默认：智能工作日）
5. 选择数据类型（1=日线，2=分钟线）
6. 如果是分钟线，输入K线周期（默认：30分钟）

### 可视化函数

#### `create_and_save_chart(result, stock_code, start_date, end_date, data_type)`
创建图表并保存HTML

```python
def create_and_save_chart(result, stock_code, start_date, end_date, data_type)
```

**参数说明**：
- `result`：缠论分析结果DataFrame
- `stock_code`：股票代码
- `start_date`：开始日期
- `end_date`：结束日期
- `data_type`：数据类型

**返回值**：
- 元组：(chart_obj, save_success)

#### `show_chart(chart_obj, data_type)`
显示图表

```python
def show_chart(chart_obj, data_type)
```

**参数说明**：
- `chart_obj`：图表对象
- `data_type`：数据类型

#### `print_supported_codes_info()`
打印支持的股票代码信息

```python
def print_supported_codes_info()
```

**输出信息**：
```
📚 支持的股票代码格式：
   A股：600000（浦发银行）或 sh.600000
   深股：000001（平安银行）或 sz.000001
   ETF：588000（科创ETF）或 159915（创业板ETF）
   指数：000001（上证指数）或 399001（深证成指）
   港股：00700（腾讯）或 00700.HK
   北交所：830799（安达科技）或 bj.830799
```

### 主函数

#### `main()`
主程序入口

```python
def main()
```

**执行流程**：
1. 显示欢迎信息和可视化引擎类型
2. 打印支持的股票代码信息
3. 进入循环：
   - 调用`get_user_input()`获取用户输入
   - 调用`analyze_stock()`分析股票
   - 如果分析成功：
     - 调用`create_and_save_chart()`创建并保存图表
     - 调用`show_chart()`显示图表
     - 显示分型统计
   - 询问是否继续分析其他股票
4. 程序结束提示

## 💡 使用示例

### 基本使用

```bash
# 运行程序
python mootdx_chanlun.py
```

### 程序交互示例

```
🎯 缠论K线分析工具 - Mootdx版本
支持A股、ETF、指数、港股数据获取
==================================================
💡 可视化引擎：Plotly

📚 支持的股票代码格式：
   A股：600000（浦发银行）或 sh.600000
   深股：000001（平安银行）或 sz.000001
   ETF：588000（科创ETF）或 159915（创业板ETF）
   指数：000001（上证指数）或 399001（深证成指）
   港股：00700（腾讯）或 00700.HK
   北交所：830799（安达科技）或 bj.830799

📝 请输入分析参数（直接回车使用默认值）：
股票代码（支持A股/ETF/指数/港股，默认 600000）: 00700
📝 已自动识别为: 00700
开始日期（默认 2024-01-01）: 
结束日期（默认 2025-12-29）: 

数据类型选择：
1. 日线数据（默认）
2. 分钟线数据
请选择 (1-2): 1

==================================================
📊 正在分析 00700 (港股 日线)...
正在获取港股 00700 的数据 (2024-01-01 至 2025-12-29)...
✓ 使用港股市场参数 31 成功获取日线数据
✅ 获取数据 492 根K线
[缠论处理过程...]
🎯 缠论K线: 158 根
🔺 顶分型: 8 个
🔻 底分型: 7 个
✅ HTML文件已保存: results/mootdx_00700_2024-01-01_2025-12-29_daily.html
✅ Plotly交互图表显示成功
💡 功能说明：
   - 拖拽缩放：鼠标拖拽可以缩放图表
   - Hover信息：鼠标悬停显示详细数据
   - Y轴调节：使用按钮重置或自动调节Y轴
   - 成交量显示：底部显示成交量柱状图

📊 分型统计：顶分型8个，底分型7个

==================================================
是否继续分析其他股票？(y/n): n

🎉 分析完成！
```

### 代码调用示例

```python
from mootdx_chanlun import analyze_stock, normalize_stock_code, get_market_type
from plotly_visualizer import plotly_chanlun_visualization

# 识别市场类型
market_type = get_market_type("00700")
print(f"市场类型: {market_type}")  # hk

# 标准化股票代码
code = normalize_stock_code("600000")
print(f"标准化代码: {code}")  # sh.600000

# 分析港股股票
result = analyze_stock(
    stock_code="00700",
    start_date="2024-01-01",
    end_date="2025-12-29",
    data_type='daily'
)

# 分析ETF
result = analyze_stock(
    stock_code="588000",
    start_date="2024-01-01",
    end_date="2025-12-29",
    data_type='daily'
)

# 分析指数
result = analyze_stock(
    stock_code="000001",
    start_date="2024-01-01",
    end_date="2025-12-29",
    data_type='daily'
)

# 如果分析成功，显示图表
if result is not None:
    plotly_chanlun_visualization(result, data_type='daily')
```

## 📊 输出文件

### HTML文件

文件保存在`results/`目录，命名格式：
```
mootdx_{股票代码}_{开始日期}_{结束日期}_{数据类型}.html
```

示例：
- `mootdx_00700_2024-01-01_2025-12-29_daily.html` - 港股日线
- `mootdx_sz.000001_2024-12-01_2025-12-29_minute_30.html` - A股30分钟线
- `mootdx_588000_2024-01-01_2025-12-29_daily.html` - ETF日线

## ⚙️ 配置选项

### 可视化引擎选择

程序默认优先使用Plotly，如果Plotly不可用则回退到Matplotlib：

```python
# 优先使用Plotly
from plotly_visualizer import plotly_chanlun_visualization
VISUALIZATION_AVAILABLE = True
VISUALIZATION_TYPE = "plotly"
```

### 默认参数

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| 股票代码 | 600000 | 浦发银行 |
| 开始日期 | 2024-01-01 | 固定默认值 |
| 结束日期 | 智能工作日 | 今天或上一个工作日 |
| 数据类型 | daily | 日线数据 |
| K线周期 | 30 | 30分钟K线 |

## 🔍 数据流程

```
用户输入
    ↓
normalize_stock_code() - 标准化股票代码
    ↓
get_market_type() - 识别市场类型
    ↓
MootdxDataFetcher - 获取股票数据
    ├─ A股: get_daily_data() / get_minute_data()
    ├─ ETF: get_etf_data()
    ├─ 指数: get_index_data()
    └─ 港股: get_hk_stock_data()
    ↓
ChanlunProcessor - 缠论分析
    ├─ trim_data_by_extremes() - 极值修剪
    ├─ merge_klines() - K线合并
    ├─ identify_fractals() - 分型识别
    └─ identify_segments() - 笔识别
    ↓
可视化处理
    ├─ plotly_chanlun_visualization() - Plotly版本
    └─ enhanced_chanlun_visualization() - Matplotlib版本
    ↓
保存HTML文件
    ↓
显示图表
```

## ⚠️ 注意事项

1. **股票代码格式**：
   - 支持多种格式（600000、sh.600000、00700等）
   - 程序会自动标准化

2. **市场识别**：
   - 指数代码可能与深交所代码冲突
   - 建议深股代码加sz.前缀

3. **日期格式**：
   - 必须使用YYYY-MM-DD格式
   - 结束日期默认为智能工作日

4. **数据获取**：
   - Mootdx数据相对实时
   - 需要网络连接
   - 多服务器自动选择

5. **可视化**：
   - Plotly需要网络连接加载JS库
   - Matplotlib需要mpld3库保存HTML

6. **文件保存**：
   - results目录会自动创建
   - 重复运行会覆盖同名文件

## 🐛 常见问题

### Q1: 市场类型识别错误

**原因**：股票代码格式不标准

**解决方法**：
```python
# 指定市场前缀
code = "sz.000001"  # 深股
code = "000001"      # 上证指数
```

### Q2: 港股数据获取失败

**原因**：网络问题或港股服务器不可用

**解决方法**：
1. 检查网络连接
2. 稍后重试
3. 或使用A股数据测试

### Q3: "可视化模块不可用"

**原因**：未安装Plotly或Matplotlib

**解决方法**：
```bash
pip install plotly
# 或
pip install matplotlib mpld3
```

### Q4: 分钟数据获取为空

**原因**：
- 时间范围过大
- 数据接口限制
- 市场不活跃时段

**解决方法**：
1. 缩短时间范围
2. 使用日线数据
3. 选择活跃市场

### Q5: 分型数量为0

**原因**：
- 数据量不足
- 数据质量差
- 市场波动小

**解决方法**：
1. 增加时间范围
2. 选择活跃股票
3. 使用日线数据

## 📚 相关文档

- [Mootdx数据获取器](mootdx_data_fetcher.md)
- [缠论核心算法](chanlun_processor.md)
- [Plotly可视化工具](plotly_visualizer.md)
- [BaoStock版本文档](baostock_chanlun.md)
