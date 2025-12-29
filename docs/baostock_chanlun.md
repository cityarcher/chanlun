# baostock_chanlun.py - BaoStock版缠论分析主程序

## 📋 文件概述

`baostock_chanlun.py` 是基于BaoStock数据源的缠论K线分析主程序，提供完整的A股日K线和分钟K线分析功能。

## 🎯 主要功能

### 核心特性
- **数据获取**：使用BaoStock接口获取A股数据
- **缠论分析**：自动识别分型、笔等缠论要素
- **交互式输入**：支持命令行交互式参数输入
- **可视化输出**：支持Plotly和Matplotlib两种可视化方式
- **HTML导出**：自动保存分析结果为HTML文件

## 🏗️ 类和函数说明

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

### 核心函数

#### `analyze_stock(stock_code, start_date, end_date, data_type='daily', frequency='30')`
分析单只股票的缠论数据

```python
def analyze_stock(stock_code, start_date, end_date, data_type='daily', frequency='30')
```

**参数说明**：
- `stock_code`：股票代码（格式：sh.600000 或 sz.000001）
- `start_date`：开始日期（格式：YYYY-MM-DD）
- `end_date`：结束日期（格式：YYYY-MM-DD）
- `data_type`：数据类型，'daily' 或 'minute'，默认为 'daily'
- `frequency`：分钟K线周期，'5'/'15'/'30'/'60'，默认为 '30'

**返回值**：
- 包含缠论分析结果的DataFrame，如果失败则返回None

**功能流程**：
1. 使用AStockDataFetcher获取股票数据
2. 使用ChanlunProcessor进行缠论分析
3. 显示简要统计信息（缠论K线数量、分型数量）

#### `normalize_stock_code(code: str) -> str`
标准化股票代码，自动添加交易所前缀

```python
def normalize_stock_code(code: str) -> str
```

**参数说明**：
- `code`：用户输入的股票代码，可以是完整格式(sh.600000)或仅数字(600000)

**返回值**：
- 标准化后的股票代码，格式：sh.600000 / sz.000001

**转换规则**：
- 首位数字为6：上海交易所 → `sh.代码`
- 首位数字为0或3：深圳交易所 → `sz.代码`
- 首位数字为8、9、4：北京交易所 → `bj.代码`
- 其他格式：保持原样

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
  - `chart_obj`：图表对象
  - `save_success`：保存是否成功

**功能**：
1. 确保results目录存在
2. 根据可视化类型（Plotly/Matplotlib）创建图表
3. 保存为HTML文件到results目录
4. 返回图表对象用于后续显示

#### `show_chart(chart_obj, data_type)`
显示图表

```python
def show_chart(chart_obj, data_type)
```

**参数说明**：
- `chart_obj`：图表对象
- `data_type`：数据类型

**功能**：
- 根据可视化类型显示图表
- 显示使用说明（拖拽缩放、Hover信息等）

### 主函数

#### `main()`
主程序入口

```python
def main()
```

**执行流程**：
1. 显示欢迎信息和可视化引擎类型
2. 进入循环：
   - 调用`get_user_input()`获取用户输入
   - 调用`analyze_stock()`分析股票
   - 如果分析成功：
     - 调用`create_and_save_chart()`创建并保存图表
     - 调用`show_chart()`显示图表
     - 显示分型统计
   - 询问是否继续分析其他股票
3. 程序结束提示

## 💡 使用示例

### 基本使用

```python
# 运行程序
python baostock_chanlun.py
```

### 程序交互示例

```
🎯 缠论K线分析工具
========================================
💡 可视化引擎：Plotly

📝 请输入分析参数（直接回车使用默认值）：
股票代码（默认 600000）: 600000
📝 已自动识别为: sh.600000
开始日期（默认 2024-01-01）: 2024-01-01
结束日期（默认 2025-12-29）: 

数据类型选择：
1. 日线数据（默认）
2. 分钟线数据
请选择 (1-2): 1

==================================================
📊 正在分析 sh.600000 (A股 日线)...
正在获取 sh.600000 的日K线数据 (2024-01-01 至 2025-12-29)...
数据清洗完成：原始数据 492 行，清洗后 492 行
✅ 获取数据 492 根K线
[缠论处理过程...]
🎯 缠论K线: 158 根
🔺 顶分型: 8 个
🔻 底分型: 7 个
✅ HTML文件已保存: results/sh.600000_2024-01-01_2025-12-29_daily.html
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
from baostock_chanlun import analyze_stock, normalize_stock_code
from plotly_visualizer import plotly_chanlun_visualization

# 标准化股票代码
stock_code = normalize_stock_code("600000")
print(f"标准化代码: {stock_code}")  # sh.600000

# 分析股票
result = analyze_stock(
    stock_code=stock_code,
    start_date="2024-01-01",
    end_date="2025-12-29",
    data_type='daily'
)

# 如果分析成功，显示图表
if result is not None:
    plotly_chanlun_visualization(result, data_type='daily')
```

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

## 📊 输出文件

### HTML文件

文件保存在`results/`目录，命名格式：
```
{股票代码}_{开始日期}_{结束日期}_{数据类型}.html
```

示例：
- `sh.600000_2024-01-01_2025-12-29_daily.html`
- `sz.000001_2024-12-01_2025-12-29_minute_30.html`

### 文件内容

HTML文件包含：
- K线图表（蜡烛图）
- 成交量柱状图
- 分型标记（顶分型、底分型）
- 笔的连线
- 交互功能（zoom、pan、hover等）

## 🔍 数据流程

```
用户输入
    ↓
normalize_stock_code() - 标准化股票代码
    ↓
AStockDataFetcher - 获取股票数据
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
   - 支持6位数字代码（600000）
   - 支持完整格式（sh.600000）
   - 程序会自动标准化

2. **日期格式**：
   - 必须使用YYYY-MM-DD格式
   - 结束日期默认为智能工作日

3. **数据获取**：
   - BaoStock数据可能有延迟
   - 建议在工作日交易时间外使用

4. **可视化**：
   - Plotly需要网络连接加载JS库
   - Matplotlib需要mpld3库保存HTML

5. **文件保存**：
   - results目录会自动创建
   - 重复运行会覆盖同名文件

## 🐛 常见问题

### Q1: 程序提示"BaoStock连接失败"

**原因**：网络问题或BaoStock服务不稳定

**解决方法**：
1. 检查网络连接
2. 稍后重试
3. 或使用Mootdx版本（mootdx_chanlun.py）

### Q2: "可视化模块不可用"

**原因**：未安装Plotly或Matplotlib

**解决方法**：
```bash
pip install plotly
# 或
pip install matplotlib mpld3
```

### Q3: HTML文件无法打开

**原因**：浏览器不支持或文件损坏

**解决方法**：
1. 使用现代浏览器（Chrome、Firefox、Edge）
2. 检查文件是否完整
3. 尝试重新运行程序

### Q4: 分型数量为0

**原因**：数据量不足或数据质量差

**解决方法**：
1. 增加时间范围
2. 选择活跃股票
3. 使用日线数据

## 📚 相关文档

- [BaoStock数据获取器](baostock_data_fetcher.md)
- [缠论核心算法](chanlun_processor.md)
- [Plotly可视化工具](plotly_visualizer.md)
- [Matplotlib可视化工具](enhanced_visualizer.md)
