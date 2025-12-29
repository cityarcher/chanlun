# 缠论K线分析工具

一个基于Python的缠论技术分析工具，用于股票K线数据处理、分析和可视化。

## 项目简介

本项目实现了缠论技术分析方法的核心功能，包括：
- K线数据处理（包含关系合并）
- 顶分型和底分型识别
- 笔的识别和绘制
- 交互式K线图表可视化
- 支持A股实时数据获取

## 项目结构

```
chanlun/
├── chanlun_processor.py      # 缠论核心算法处理器
├── baostock_data_fetcher.py   # A股数据获取工具
├── real_data_chanlun.py      # 主程序入口
├── enhanced_visualizer.py    # Matplotlib增强版可视化
├── plotly_visualizer.py      # Plotly交互式可视化
├── docs/                     # 文档目录
│   └── README.md            # 项目说明文档
└── __pycache__/             # Python缓存目录
```

## 核心功能

### 1. 缠论数据处理 (chanlun_processor.py)

**ChanlunProcessor类**提供完整的缠论分析功能：

- **数据预处理**：根据极值点修剪K线数据
- **K线合并**：基于包含关系合并K线生成缠论K线
- **分型识别**：识别顶分型和底分型
- **分型筛选**：多步骤筛选有效的分型点
- **笔识别**：根据分型交叉序列形成笔

#### 核心算法流程：

1. **数据修剪**：找到历史最高价和最低价，取较早时间点作为起点
2. **K线合并**：处理包含关系，生成缠论K线
3. **分型识别**：标记顶分型和底分型
4. **分型筛选**：
   - 极值筛选：移除非局部极值的分型
   - 连续分型筛选：保留连续同类型分型中的最优分型
   - 关系验证：验证分型之间的高低点关系
   - 接近分型筛选：处理间隔过小的分型对
5. **笔识别**：按交叉原则连接分型形成笔

### 2. 数据获取 (baostock_data_fetcher.py)

**AStockDataFetcher类**提供A股数据获取功能：

- 支持日K线和分钟K线获取
- 基于baostock接口
- 自动数据清洗和异常值处理

- 前复权/后复权/不复权选项

#### 主要方法：

- `get_daily_data()`: 获取日K线数据
- `get_minute_data()`: 获取分钟K线数据

- `get_stock_basic_info()`: 获取股票基本信息

### 3. 交互式分析工具 (real_data_chanlun.py)

主程序提供用户友好的交互界面：

- 参数化输入：股票代码、时间范围、数据类型
- 自动数据分析：获取数据→缠论处理→结果展示
- 可视化支持：自动检测并使用合适的可视化引擎
- 详细统计信息：分型数量、笔数量等分析结果

### 4. 可视化工具

#### 增强版可视化 (enhanced_visualizer.py)

基于Matplotlib的静态图表：
- K线蜡烛图
- 分型标记（顶分型▼，底分型▲）
- 笔绘制（上涨红色，下跌绿色）
- 鼠标悬停信息
- 十字光标定位

#### Plotly可视化 (plotly_visualizer.py)

基于Plotly的交互式图表：
- 丰富的交互功能（拖拽缩放、Hover信息）
- 成交量柱状图
- Y轴调节按钮
- 统一Hover模式
- 响应式布局

## 安装依赖

```bash
# 核心依赖
pip install pandas numpy baostock

# 可视化依赖（二选一或全部安装）
pip install matplotlib  # 增强版可视化
pip install plotly      # Plotly交互式可视化
```

## 使用方法

### 1. 基本使用

```python
# 运行交互式分析工具
python real_data_chanlun.py
```

程序会提示输入：
- 股票代码（默认：sh.600000）
- 开始日期（默认：2024-01-01）
- 结束日期（默认：上一个工作日）
- 数据类型（日线/分钟线）

### 2. 编程方式使用

```python
from chanlun_processor import ChanlunProcessor
from baostock_data_fetcher import AStockDataFetcher
from enhanced_visualizer import enhanced_chanlun_visualization

# 获取数据
with AStockDataFetcher() as fetcher:
    data = fetcher.get_daily_data(
        stock_code="sh.600000",
        start_date="2024-01-01",
        end_date="2024-12-31"
    )

# 缠论分析
processor = ChanlunProcessor()
result = processor.process_klines(data)

# 可视化
enhanced_chanlun_visualization(result)
```

### 3. 多股分析

```python
# 分别获取多只股票数据
stocks = ["sh.600000", "sz.000001", "sh.600519"]
with AStockDataFetcher() as fetcher:
    for stock_code in stocks:
        data = fetcher.get_daily_data(
            stock_code=stock_code,
            start_date="2024-01-01",
            end_date="2024-12-31"
        )
        # 处理数据...
```

## 输出说明

### 处理结果数据结构

分析结果DataFrame包含以下关键列：

- `datetime`: 时间戳
- `open, high, low, close`: OHLC价格数据
- `direction`: K线方向（up/down）
- `is_fractal`: 是否为分型
- `fractal_type`: 分型类型（top/bottom）
- `is_segment`: 是否为笔端点
- `segment_id`: 笔的ID
- `segment_start_type/segment_end_type`: 笔的起止分型类型

### 统计信息

程序会输出详细的处理统计：

```text
📊 正在分析 sh.600000 (日线)...
✅ 获取数据 244 根K线
数据修剪完成:
  - 最高价: 12.45 发生时间: 2024-03-05
  - 最低价: 8.32 发生时间: 2024-09-18
  - 选择较早的最低价时间点: 2024-09-18
  - 原始数据: 244 行
  - 修剪后数据: 73 行
  - 丢弃数据: 171 行

K线合并完成：原始 73 根K线合并为 45 根缠论K线
分型识别完成:
  - 顶分型数量: 8
  - 底分型数量: 7
  - 总分型数量: 15

🎯 缠论K线: 45 根
🔺 顶分型: 5 个
🔻 底分型: 6 个
📏 笔识别完成: 10 个笔（上升笔5个，下降笔5个）
```

## 可视化说明

### 图表元素

- **K线图**：红色上涨，绿色下跌
- **顶分型**：红色倒三角▼
- **底分型**：绿色正三角▲
- **笔**：连接分型的线段，上涨红色，下跌绿色
- **成交量**：底部柱状图（仅Plotly版本）

### 交互功能

**Plotly版本**：
- 鼠标拖拽缩放
- 悬停显示详细信息
- Y轴重置/自动调节按钮
- 响应式布局

**Matplotlib版本**：
- 十字光标定位
- 鼠标悬停信息提示
- 静态图表导出

## 技术特色

### 1. 严格遵循缠论理论

- 完整实现缠论K线合并规则
- 精确的分型识别算法
- 多重分型筛选机制
- 笔的交叉序列验证

### 2. 智能数据处理

- 自动异常值检测和清理
- 包含关系准确判断
- 方向自动识别
- 数据完整性验证

### 3. 灵活的可视化

- 双引擎支持（Matplotlib + Plotly）
- 自适应布局
- 丰富的交互功能
- 专业的金融图表样式

### 4. 易于集成

- 模块化设计
- 清晰的API接口
- 完整的文档说明
- 丰富的使用示例

## 注意事项

1. **数据源**：使用baostock免费接口，数据可能存在延迟
2. **时间范围**：建议获取足够长的时间段以保证分型识别的准确性
3. **股票选择**：优先选择流动性好的主板股票
4. **分钟数据**：分钟线数据可能不如日线稳定，建议谨慎使用

## 扩展开发

### 添加新功能

项目采用模块化设计，易于扩展：

1. **新指标**：在`chanlun_processor.py`中添加新的分析方法
2. **数据源**：在`baostock_data_fetcher.py`中添加新的数据接口
3. **可视化**：创建新的可视化模块
4. **策略**：基于缠论信号开发交易策略

### 性能优化

- 使用向量化操作提升计算效率
- 实现数据缓存机制
- 支持多线程批量处理
- 优化内存使用

## 许可证

本项目仅供学习和研究使用，不构成投资建议。

## 贡献指南

欢迎提交Issue和Pull Request来改进项目：

1. Fork本项目
2. 创建特性分支
3. 提交修改
4. 发起Pull Request

## 更新日志

### v1.0.0
- 实现完整的缠论核心算法
- 支持A股数据获取
- 提供双引擎可视化
- 交互式分析工具

---

*本工具仅用于技术分析学习，投资有风险，入市需谨慎。*