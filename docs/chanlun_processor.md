# chanlun_processor.py - 缠论核心算法处理器

## 📋 文件概述

`chanlun_processor.py` 实现了缠论的核心算法，包括K线处理、分型识别、笔段分析等功能。这是整个项目的核心算法模块，实现了缠论理论中的关键概念。

## 🎯 主要功能

### 核心算法
- **极值修剪**：根据最高价和最低价修剪K线数据
- **K线合并**：基于包含关系合并K线生成缠论K线
- **分型识别**：识别顶分型和底分型
- **多重筛选**：极值筛选、连续分型筛选、关系验证等
- **笔段分析**：识别上升笔和下降笔
- **处理摘要**：提供详细的处理统计信息

## 🏗️ 类说明

### ChanlunProcessor类

#### 类属性
```python
class ChanlunProcessor:
    """缠论K线处理器"""
```

**主要属性**：
- `original_data`：原始K线数据
- `trimmed_data`：修剪后的数据
- `chanlun_data`：缠论K线数据
- `initial_direction`：初始方向（'up'或'down'）
- `fractals_data`：分型数据
- `segments_data`：笔段数据
- `segments`：笔列表
- `fractal_filter_stats`：分型筛选统计信息

## 📖 方法详解

### 数据预处理方法

#### `trim_data_by_extremes(self, df: pd.DataFrame)`
根据极值点修剪K线数据

```python
def trim_data_by_extremes(self, df: pd.DataFrame) -> pd.DataFrame
```

**参数说明**：
- `df`：原始K线数据，必须包含datetime, high, low列

**返回值**：
- 修剪后的DataFrame

**算法步骤**：
1. 找到所有K线中的最高价及其对应的datetime
2. 找到所有K线中的最低价及其对应的datetime
3. 取这两个datetime中较小的一个
4. 丢弃该K线之前的所有数据

**方向判断**：
- 如果最高价的datetime较小：初始方向为向下
- 如果最低价的datetime较小：初始方向为向上

**使用示例**：
```python
processor = ChanlunProcessor()
trimmed_data = processor.trim_data_by_extremes(original_data)
```

### K线合并方法

#### `check_inclusion(self, k1, k2)`
检查两根K线是否存在包含关系

```python
def check_inclusion(self, k1, k2)
```

**参数说明**：
- `k1, k2`：K线数据，包含high, low列

**返回值**：
- 元组：(has_inclusion, included_kline, including_kline)
  - `has_inclusion`：是否存在包含关系
  - `included_kline`：被包含的K线
  - `including_kline`：包含其他K线的K线

**判断规则**：
```python
# k1包含k2
if (k1['high'] >= k2['high'] and k1['low'] <= k2['low']):
    has_inclusion = True
    included_kline = k2
    including_kline = k1

# k2包含k1
elif (k2['high'] >= k1['high'] and k2['low'] <= k1['low']):
    has_inclusion = True
    included_kline = k1
    including_kline = k2
```

#### `determine_direction(self, chanlun_klines)`
根据已处理好的缠论K线的最后2根来判断方向

```python
def determine_direction(self, chanlun_klines)
```

**参数说明**：
- `chanlun_klines`：已处理的缠论K线列表

**返回值**：
- 方向字符串："up" 或 "down"

**判断规则**：
- 如果只有0根或1根缠论K线，使用初始方向
- 如果最后2根K线中，后一根K线高价更高，则方向向上
- 如果最后2根K线中，后一根K线低价更低，则方向向下
- 否则保持方向不变

#### `merge_klines(self, df: pd.DataFrame)`
基于包含关系合并K线生成缠论K线

```python
def merge_klines(self, df: pd.DataFrame) -> pd.DataFrame
```

**参数说明**：
- `df`：修剪后的K线数据

**返回值**：
- 合并后的缠论K线DataFrame

**合并规则**：
1. **包含关系判断**：只有存在包含关系的K线才合并
2. **方向判断**：根据已经处理好的缠论K线的最后2根来判断方向
3. **合并规则**：
   - 向上时：高价取高者，低价取高者
   - 向下时：高价取低者，低价取低者
4. **价格设定**：
   - 缠论K线的开盘价为第一根K线开盘价
   - 缠论K线的收盘价为最后一根K线收盘价
   - 成交量和成交额为所有参与合并K线的累加

**算法流程**：
```python
1. 遍历K线数据
2. 对每根K线，检查与后续K线是否有包含关系
3. 如果有包含关系：
   a. 判断当前方向
   b. 根据方向合并高低价
   c. 累加成交量和成交额
   d. 继续检查下一根K线
4. 如果没有包含关系，形成缠论K线，继续下一根
```

**使用示例**：
```python
processor = ChanlunProcessor()
chanlun_data = processor.merge_klines(trimmed_data)
print(f"合并后K线数: {len(chanlun_data)}")
```

### 分型识别方法

#### `check_top_fractal(self, klines, index)`
检查顶分型

```python
def check_top_fractal(self, klines, index) -> bool
```

**参数说明**：
- `klines`：缠论K线列表
- `index`：要检查的中间K线的索引

**返回值**：
- 是否为顶分型（True/False）

**判断规则**：
- 需要连续3根K线：第1、2、3根K线
- 第2根K线的高点必须是3根中最高的
- 第1根和第3根K线的高点都低于第2根

#### `check_bottom_fractal(self, klines, index)`
检查底分型

```python
def check_bottom_fractal(self, klines, index) -> bool
```

**参数说明**：
- `klines`：缠论K线列表
- `index`：要检查的中间K线的索引

**返回值**：
- 是否为底分型（True/False）

**判断规则**：
- 需要连续3根K线：第1、2、3根K线
- 第2根K线的低点必须是3根中最低的
- 第1根和第3根K线的低点都高于第2根

#### `identify_fractals(self, df: pd.DataFrame)`
识别缠论K线中的顶分型和底分型

```python
def identify_fractals(self, df: pd.DataFrame) -> pd.DataFrame
```

**参数说明**：
- `df`：缠论K线DataFrame

**返回值**：
- 添加了分型标记的DataFrame

**识别规则**：
1. **第1根K线**：
   - 如果初始方向为向下，则标记为顶分型
   - 如果初始方向为向上，则标记为底分型
2. **后续K线**：
   - 顶分型：中间K线的高点是连续3根K线中最高的
   - 底分型：中间K线的低点是连续3根K线中最低的

**输出列**：
- `fractal_type`：分型类型（'top'/'bottom'/None）
- `is_fractal`：是否为分型（True/False）

**使用示例**：
```python
processor = ChanlunProcessor()
fractals_df = processor.identify_fractals(chanlun_data)

# 统计分型数量
fractals = fractals_df[fractals_df['is_fractal']]
top_count = len(fractals[fractals['fractal_type'] == 'top'])
bottom_count = len(fractals[fractals['fractal_type'] == 'bottom'])
print(f"顶分型: {top_count}, 底分型: {bottom_count}")
```

### 分型筛选方法

#### `filter_fractals_by_extremes(self, df: pd.DataFrame, window: int = 5)`
根据极值筛选分型

```python
def filter_fractals_by_extremes(self, df: pd.DataFrame, window: int = 5)
```

**参数说明**：
- `df`：包含分型标记的DataFrame
- `window`：前后K线的数量，默认为5（总共检查11根K线）

**返回值**：
- 筛选后的DataFrame

**筛选规则**：
- 对于标记为底分型的K线，如果其低价不是前面5根K线以及后面5根K线中低价最低的，则取消其底分型标记
- 对于标记为顶分型的K线，如果其高价不是前面5根K线以及后面5根K线中高价最高的，则取消其顶分型标记

#### `filter_consecutive_fractals(self, df: pd.DataFrame)`
筛选连续的同类型分型

```python
def filter_consecutive_fractals(self, df: pd.DataFrame)
```

**参数说明**：
- `df`：包含分型标记的DataFrame

**返回值**：
- 筛选后的DataFrame

**筛选规则**：
- 对于连续的顶分型（指顶分型与顶分型之间没有底分型的），仅保留高价大于这些顶分型中其他顶分型高价的那个顶分型，取消其他顶分型的标记
- 对于连续的底分型（指底分型与底分型之间没有顶分型的），仅保留低价小于这些底分型中其他底分型低价的那个底分型，取消其他底分型的标记

#### `validate_fractal_relationships(self, df: pd.DataFrame)`
验证分型之间的关系

```python
def validate_fractal_relationships(self, df: pd.DataFrame)
```

**参数说明**：
- `df`：包含分型标记的DataFrame

**返回值**：
- 验证后的DataFrame

**验证规则**：
- 除第一个分型外，如果一个分型是底分型，那么它的低点必须小于它前一个顶分型的高点，也必须低于它后一个顶分型的高点
- 如果不满足这个条件，那么取消这个底分型的标记
- 同样的，如果一个分型是顶分型，那么它的高点必须大于它前一个底分型的低点，也必须高于它后一个底分型的低点
- 如果不满足这个条件，那么取消这个顶分型的标记
- 如果这一步有取消任何分型标记，那么这一步后要重新执行连续分型的筛选

#### `filter_close_fractals(self, df: pd.DataFrame, min_gap: int = 4)`
筛选过于接近的分型对

```python
def filter_close_fractals(self, df: pd.DataFrame, min_gap: int = 4)
```

**参数说明**：
- `df`：包含分型标记的DataFrame
- `min_gap`：最小索引间隔，默认为4

**返回值**：
- 筛选后的DataFrame

**处理逻辑**：
1. 顶分型→底分型情况（索引差<min_gap）：
   - 找到Bn后面的顶分型An+1，比较An+1和An的高价，保留高价更高的
   - 根据保留的顶分型，处理相关的底分型

2. 底分型→顶分型情况（索引差<min_gap）：
   - 找到Bn后面的底分型An+1，比较An+1和An的低价，保留低价更低的
   - 根据保留的底分型，处理相关的顶分型

#### `process_fractals(self, df: pd.DataFrame)`
处理分型识别的入口方法

```python
def process_fractals(self, df: pd.DataFrame) -> pd.DataFrame
```

**参数说明**：
- `df`：缠论K线DataFrame

**返回值**：
- 包含分型信息的DataFrame

**处理流程**：
```python
1. 识别分型（identify_fractals）
2. 根据极值筛选分型（filter_fractals_by_extremes）
3. 筛选连续分型（filter_consecutive_fractals）
4. 验证分型之间的关系（validate_fractal_relationships）
5. 筛选接近分型（filter_close_fractals）
```

### 笔段分析方法

#### `identify_segments(self, df: pd.DataFrame)`
识别笔（由分型组成的连续交叉序列）

```python
def identify_segments(self, df: pd.DataFrame)
```

**参数说明**：
- `df`：包含分型标记的DataFrame

**返回值**：
- 添加了笔标记的DataFrame

**识别规则**：
- 第一个分型是顶分型：按照顶分型、底分型、顶分型、底分型、……这样交叉的原则
- 第一个分型是底分型：按照底分型、顶分型、底分型、顶分型、……这样交叉的原则
- 一笔由一个顶分型和一个底分型组成
- 笔与笔之间是连续的

**输出列**：
- `segment_id`：笔ID
- `is_segment`：是否为笔端点
- `segment_start_idx`：笔起始索引
- `segment_end_idx`：笔结束索引
- `segment_start_type`：笔起始分型类型
- `segment_end_type`：笔结束分型类型

**使用示例**：
```python
processor = ChanlunProcessor()
segments_df = processor.identify_segments(fractals_df)

# 统计笔数量
segments = segments_df[segments_df['is_segment']]
print(f"总笔数: {len(segments['segment_id'].unique())}")
```

### 主处理方法

#### `process_klines(self, df: pd.DataFrame)`
处理K线数据的主入口

```python
def process_klines(self, df: pd.DataFrame) -> pd.DataFrame
```

**参数说明**：
- `df`：原始K线数据

**返回值**：
- 处理后的K线数据（包含分型和笔信息）

**处理流程**：
```python
1. 根据极值修剪数据（trim_data_by_extremes）
2. 合并K线生成缠论K线（merge_klines）
3. 识别顶分型和底分型（process_fractals）
4. 识别笔（identify_segments）
```

**使用示例**：
```python
from chanlun_processor import ChanlunProcessor
import pandas as pd

# 加载数据
data = pd.read_csv('stock_data.csv')

# 处理数据
processor = ChanlunProcessor()
result = processor.process_klines(data)

# 获取处理摘要
summary = processor.get_processing_summary()
print(summary)
```

#### `get_processing_summary(self)`
获取数据处理摘要信息

```python
def get_processing_summary(self) -> dict
```

**返回值**：
- 包含处理信息的字典

**摘要内容**：
```python
{
    "status": "已完成",
    "original_count": 原始数据数量,
    "initial_direction": 初始方向,
    "trimmed_count": 修剪后数据数量,
    "first_datetime_trimmed": 修剪后开始时间,
    "last_datetime_trimmed": 修剪后结束时间,
    "dropped_count": 丢弃数据数量,
    "chanlun_count": 缠论K线数量,
    "merged_count": 合并K线数量,
    "fractal_count": 分型总数,
    "top_fractal_count": 顶分型数量,
    "bottom_fractal_count": 底分型数量,
    "segment_count": 笔总数,
    "up_segment_count": 上升笔数量,
    "down_segment_count": 下降笔数量,
    # 分型筛选统计
    "original_fractal_count": 原始分型数量,
    "extreme_filtered_fractal_count": 极值筛选后分型数量,
    "consecutive_filtered_fractal_count": 连续筛选后分型数量,
    "relationship_filtered_fractal_count": 关系验证后分型数量,
    "final_fractal_count": 最终分型数量,
    "total_removed_count": 总共取消分型数量
}
```

**使用示例**：
```python
processor = ChanlunProcessor()
result = processor.process_klines(data)
summary = processor.get_processing_summary()

print(f"原始K线: {summary['original_count']} 根")
print(f"缠论K线: {summary['chanlun_count']} 根")
print(f"顶分型: {summary['top_fractal_count']} 个")
print(f"底分型: {summary['bottom_fractal_count']} 个")
print(f"上升笔: {summary['up_segment_count']} 笔")
print(f"下降笔: {summary['down_segment_count']} 笔")
```

## 💡 使用示例

### 基本使用

```python
from chanlun_processor import ChanlunProcessor
import pandas as pd

# 加载K线数据
data = pd.read_csv('stock_data.csv')

# 创建处理器
processor = ChanlunProcessor()

# 处理数据
result = processor.process_klines(data)

# 获取处理摘要
summary = processor.get_processing_summary()
print(summary)
```

### 分步处理

```python
processor = ChanlunProcessor()

# 步骤1：修剪数据
trimmed_data = processor.trim_data_by_extremes(data)
print(f"修剪后: {len(trimmed_data)} 根K线")

# 步骤2：合并K线
chanlun_data = processor.merge_klines(trimmed_data)
print(f"合并后: {len(chanlun_data)} 根缠论K线")

# 步骤3：识别分型
fractals_df = processor.identify_fractals(chanlun_data)
print(f"识别到分型: {len(fractals_df[fractals_df['is_fractal']])} 个")

# 步骤4：识别笔
segments_df = processor.identify_segments(fractals_df)
print(f"识别到笔: {len(segments_df['segment_id'].unique())} 笔")
```

### 访问处理结果

```python
# 原始数据
print(processor.original_data)

# 修剪后的数据
print(processor.trimmed_data)

# 缠论K线数据
print(processor.chanlun_data)

# 分型数据
print(processor.fractals_data)

# 笔段数据
print(processor.segments_data)

# 笔列表
print(processor.segments)
```

## 📊 算法流程图

```
原始K线数据
    ↓
trim_data_by_extremes() - 极值修剪
    ↓
    └─ 确定初始方向（up/down）
    ↓
merge_klines() - K线合并
    ↓
    ├─ check_inclusion() - 检查包含关系
    ├─ determine_direction() - 判断方向
    └─ 合并生成缠论K线
    ↓
process_fractals() - 分型处理
    ↓
    ├─ identify_fractals() - 识别分型
    │   ├─ check_top_fractal() - 检查顶分型
    │   └─ check_bottom_fractal() - 检查底分型
    ├─ filter_fractals_by_extremes() - 极值筛选
    ├─ filter_consecutive_fractals() - 连续分型筛选
    ├─ validate_fractal_relationships() - 关系验证
    └─ filter_close_fractals() - 接近分型筛选
    ↓
identify_segments() - 笔段识别
    ↓
最终结果（包含分型和笔信息）
```

## 🔍 算法详解

### 极值修剪算法

**目的**：确定分析的起始点，统一初始方向

**步骤**：
1. 找到数据中的最高价和最低价
2. 比较两者发生的时间
3. 选择时间较早的那个作为起始点
4. 丢弃起始点之前的所有数据
5. 根据起始点类型确定初始方向

### K线合并算法

**目的**：基于包含关系简化K线，生成缠论K线

**包含关系**：
- K线A包含K线B：A.high ≥ B.high 且 A.low ≤ B.low
- K线B包含K线A：B.high ≥ A.high 且 B.low ≤ A.low

**合并规则**：
- 向上趋势：高价取高者，低价取高者
- 向下趋势：高价取低者，低价取低者

### 分型识别算法

**顶分型**：
- 连续3根K线：K1, K2, K3
- 条件：K2.high > K1.high 且 K2.high > K3.high

**底分型**：
- 连续3根K线：K1, K2, K3
- 条件：K2.low < K1.low 且 K2.low < K3.low

### 笔段识别算法

**交叉原则**：
- 第一个分型是顶分型：顶 → 底 → 顶 → 底 → ...
- 第一个分型是底分型：底 → 顶 → 底 → 顶 → ...

**笔的定义**：
- 一笔由一个顶分型和一个底分型组成
- 笔的方向：从第一个分型到第二个分型
- 上升笔：底 → 顶
- 下降笔：顶 → 底

## ⚙️ 配置选项

### 分型筛选参数

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| window | 5 | 极值筛选窗口（前后各window根，共2*window+1根） |
| min_gap | 4 | 接近分型筛选的最小索引间隔 |

### 自定义筛选规则

```python
# 调整极值筛选窗口
fractals_df = processor.filter_fractals_by_extremes(chanlun_df, window=10)

# 调整接近分型筛选间隔
final_df = processor.filter_close_fractals(filtered_df, min_gap=6)
```

## ⚠️ 注意事项

1. **数据要求**：
   - 必须包含datetime, open, high, low, close列
   - 数据必须按时间排序
   - 数据量建议至少100根K线

2. **分型识别**：
   - 至少需要3根K线才能识别第一个分型
   - 分型数量过少可能是数据不足或市场波动小

3. **笔段识别**：
   - 需要至少2个不同类型的分型才能形成第一笔
   - 笔的数量受分型数量限制

4. **筛选规则**：
   - 筛选会减少分型数量
   - 过度筛选可能导致分型过少
   - 可根据需要调整筛选参数

5. **初始方向**：
   - 初始方向由极值修剪时确定
   - 影响后续所有处理步骤

## 🐛 常见问题

### Q1: 分型数量为0

**原因**：
- 数据量不足
- 数据波动小
- 筛选过严

**解决方法**：
- 增加时间范围
- 调整筛选参数
- 选择更活跃的股票

### Q2: 笔数量很少

**原因**：
- 分型数量少
- 分型不满足交叉原则

**解决方法**：
- 减少分型筛选
- 增加数据范围
- 检查分型识别是否正确

### Q3: 初始方向不正确

**原因**：
- 极值点选择不当
- 数据异常

**解决方法**：
- 检查数据质量
- 调整修剪策略
- 手动设定初始方向

### Q4: 分型关系验证取消太多分型

**原因**：
- 分型关系不满足缠论规则
- 数据波动异常

**解决方法**：
- 跳过关系验证步骤
- 调整验证规则
- 检查数据质量

## 📚 相关概念

### 缠论基础概念

1. **K线包含**：一根K线完全包含另一根K线
2. **顶分型**：中间K线高点最高的连续3根K线
3. **底分型**：中间K线低点最低的连续3根K线
4. **缠论K线**：基于包含关系合并后的K线
5. **笔**：由相邻的顶分型和底分型组成的线段
6. **上升笔**：从底分型到顶分型
7. **下降笔**：从顶分型到底分型

## 📚 相关文档

- [BaoStock分析主程序](baostock_chanlun.md)
- [Mootdx分析主程序](mootdx_chanlun.md)
- [Plotly可视化工具](plotly_visualizer.md)
- [Matplotlib可视化工具](enhanced_visualizer.md)
