# 缠论K线分析工具 (Chanlun K-Line Analysis Tool)

基于Python实现的缠论K线分析工具，支持多市场数据获取、分型识别、笔段分析和交互式可视化。

## 🎯 项目简介

本项目是一个完整的缠论技术分析系统，提供从数据获取到可视化分析的全流程支持。支持A股、ETF、港股、指数等多市场数据，基于缠论理论实现分型识别、笔段分析等核心功能，并提供多种可视化方案。项目包含命令行工具和现代化的Web图形界面。

## ✨ 主要特性

### 📊 多市场支持
- **A股市场**：沪深交易所（sh./sz.前缀）
- **ETF基金**：科创板ETF、创业板ETF等
- **港股市场**：港股日线和分钟K线数据
- **指数数据**：上证指数、深证成指等

### 🔧 双数据源支持
- **BaoStock**：稳定可靠的免费数据源（baostock_data_fetcher.py）
- **Mootdx**：通达信数据接口，支持更丰富的市场（mootdx_data_fetcher.py）

### 📈 缠论核心算法
- **分型识别**：顶分型、底分型自动识别
- **K线合并**：基于包含关系的K线合并
- **笔段分析**：自动识别上升笔、下降笔
- **多重筛选**：极值筛选、连续分型筛选、关系验证等

### 🎨 交互式可视化
- **Plotly版本**：丰富的交互功能（拖拽缩放、hover信息、Y轴调节）
- **Matplotlib版本**：鼠标悬停交互，支持导出HTML
- **Web图形界面**：基于Streamlit的现代化GUI，实时显示分析结果

### 🚀 高级特性
- **分批次数据获取**：支持长时间跨度的分钟数据获取，每批固定800条
- **智能数据缓存**：本地缓存机制，提升数据加载速度
- **多服务器支持**：自动测试并选择最优通达信服务器
- **错误重试机制**：自动处理网络异常和API错误

## 📁 项目结构

```
chanlun/
├── baostock_chanlun.py          # BaoStock版缠论分析主程序
├── baostock_data_fetcher.py      # BaoStock数据获取器
├── mootdx_chanlun.py             # Mootdx版缠论分析主程序
├── mootdx_data_fetcher.py        # Mootdx数据获取器（支持分批次获取）
├── chanlun_processor.py          # 缠论核心算法处理器
├── enhanced_visualizer.py        # Matplotlib可视化工具
├── plotly_visualizer.py          # Plotly可视化工具
├── requirements.txt               # Python依赖包
├── app/                          # Streamlit Web图形界面
│   ├── main.py                   # 主应用入口
│   ├── config.py                 # 应用配置
│   ├── utils.py                  # 工具函数集合
│   └── README.md                 # Web界面使用说明
├── docs/                         # 文档目录
│   ├── README.md                 # 详细文档
│   └── mootdx.md                 # Mootdx说明文档
├── results/                      # 分析结果输出目录
│   └── *.html                    # 生成的HTML图表文件
└── best_server.json              # Mootdx最优服务器配置
```

## 🚀 快速开始

### 环境安装

```bash
# 克隆项目
git clone <repository-url>
cd chanlun

# 安装依赖
pip install -r requirements.txt
```

### 使用方式

#### 方式一：命令行工具

**1. BaoStock版本（推荐A股分析）**

```bash
python baostock_chanlun.py
```

**2. Mootdx版本（支持多市场）**

```bash
python mootdx_chanlun.py
```

**3. 运行测试**

```bash
# 测试BaoStock数据获取
python baostock_data_fetcher.py

# 测试Mootdx数据获取
python mootdx_data_fetcher.py

# 测试缠论处理算法
python chanlun_processor.py
```

#### 方式二：Web图形界面（推荐）

基于Streamlit的现代化Web界面，提供直观的可视化操作体验：

```bash
# 启动Web应用
streamlit run app/main.py
```

浏览器将自动打开 http://localhost:8501，你可以：
- 在左侧边栏输入参数（股票代码、日期范围、数据源等）
- 实时查看顶部的分析结果和交互式图表
- 支持拖拽缩放、悬停查看详情等交互功能

## 📝 使用说明

### 方式一：交互式命令行

运行程序后会提示输入参数：

```
请输入分析参数（直接回车使用默认值）：
股票代码（支持A股/ETF/指数/港股，默认 600000）:
开始日期（默认 2024-01-01）:
结束日期（默认 2025-12-29）:

数据类型选择：
1. 日线数据（默认）
2. 分钟线数据
请选择 (1-2):
```

### 方式二：Web图形界面

启动Web界面后：

1. **左侧参数配置**
   - 股票代码：输入6位数字代码（如600000）
   - 日期范围：选择开始和结束日期
   - 数据源：选择mootdx或baostock
   - 数据类型：日线或分钟线
   - 分钟周期：5/15/30/60分钟

2. **开始分析**
   - 点击"🚀 开始分析"按钮
   - 等待数据加载和处理完成

3. **查看结果**
   - 顶部统计卡片显示关键指标
   - 中间交互式图表展示K线和缠论分析
   - 支持拖拽缩放、悬停查看详情

4. **保存结果**
   - HTML文件自动保存到`results/`目录
   - 可在浏览器中打开离线查看

### 支持的股票代码格式

| 市场类型 | 代码示例 | 说明 |
|---------|---------|------|
| A股（沪市） | `600000` 或 `sh.600000` | 浦发银行 |
| A股（深市） | `000001` 或 `sz.000001` | 平安银行 |
| ETF基金 | `588000` 或 `159915` | 科创ETF、创业板ETF |
| 指数 | `000001` 或 `399001` | 上证指数、深证成指 |
| 港股 | `00700` 或 `00700.HK` | 腾讯控股 |
| 北交所 | `830799` 或 `bj.830799` | 安达科技 |

### API使用示例

#### BaoStock版本

```python
from baostock_data_fetcher import AStockDataFetcher
from chanlun_processor import ChanlunProcessor

# 获取数据
with AStockDataFetcher() as fetcher:
    data = fetcher.get_daily_data(
        stock_code="sh.600000",
        start_date="2024-01-01",
        end_date="2025-12-29"
    )

# 缠论分析
processor = ChanlunProcessor()
result = processor.process_klines(data)
summary = processor.get_processing_summary()

print(f"缠论K线: {summary['chanlun_count']} 根")
print(f"顶分型: {summary['top_fractal_count']} 个")
print(f"底分型: {summary['bottom_fractal_count']} 个")
```

#### Mootdx版本（多市场）

```python
from mootdx_data_fetcher import MootdxDataFetcher
from chanlun_processor import ChanlunProcessor

with MootdxDataFetcher() as fetcher:
    # 获取港股数据
    data = fetcher.get_hk_stock_data(
        stock_code="00700",
        start_date="2024-01-01",
        end_date="2025-12-29",
        data_type='daily'
    )

# 缠论分析（与BaoStock版本相同）
processor = ChanlunProcessor()
result = processor.process_klines(data)
```

### 可视化使用

```python
from plotly_visualizer import plotly_chanlun_visualization

# 显示交互式图表
plotly_chanlun_visualization(
    data=result,
    start_idx=0,
    bars_to_show=100,
    data_type='daily'
)
```

## 🔬 核心算法说明

### 1. 数据预处理
- **极值修剪**：根据最高价和最低价修剪K线数据
- **K线合并**：基于包含关系合并K线生成缠论K线
- **方向判断**：根据趋势确定上升/下降方向
- **分批次获取**：支持长时间跨度数据的多批次获取，每批固定800条

### 2. 分型识别
- **顶分型**：中间K线的高点是连续3根中最高的
- **底分型**：中间K线的低点是连续3根中最低的
- **多重筛选**：
  - 极值筛选（11根K线窗口）
  - 连续分型筛选
  - 分型关系验证
  - 接近分型筛选

### 3. 笔段分析
- **交叉原则**：顶分型与底分型交替出现
- **上升笔**：从底分型到顶分型
- **下降笔**：从顶分型到底分型

### 4. 数据获取优化
- **智能缓存**：本地缓存机制，TTL为1小时，避免重复获取
- **分批次获取**：按时间计算总K线数量，分批次每批800条
- **错误重试**：连续空批检测（最多2次），自动处理异常
- **多服务器支持**：自动测试并选择最优通达信服务器

## 📦 依赖包说明

| 包名 | 版本要求 | 用途 |
|-----|---------|------|
| pandas | >=1.5.0 | 数据处理 |
| numpy | >=1.21.0 | 数值计算 |
| plotly | >=5.0.0 | 交互式可视化 |
| matplotlib | >=3.5.0 | 基础可视化 |
| mpld3 | >=0.5.0 | Matplotlib转HTML |
| streamlit | >=1.28.0 | Web图形界面 |
| baostock | >=0.8.8 | BaoStock数据源 |
| pytdx | >=1.72 | 通达信接口 |
| mootdx | >=0.4.6 | Mootdx数据源 |

## 🎯 功能对比

| 功能特性 | BaoStock版本 | Mootdx版本 | Web图形界面 |
|---------|-------------|-----------|-----------|
| A股日线数据 | ✅ | ✅ | ✅ |
| A股分钟数据 | ✅ | ✅ | ✅ |
| ETF数据 | ❌ | ✅ | ✅ |
| 港股数据 | ❌ | ✅ | ✅ |
| 指数数据 | ❌ | ✅ | ✅ |
| 北交所数据 | ❌ | ✅ | ✅ |
| 分批次获取 | ❌ | ✅ | ✅ |
| 数据缓存 | ❌ | ✅ | ✅ |
| 交互式图表 | ✅ | ✅ | ✅ |
| Web界面 | ❌ | ❌ | ✅ |
| 数据稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 数据延迟 | 高 | 低 | 低 |
| 推荐场景 | 稳定A股分析 | 多市场实时分析 | 快速可视化分析 |

## 📊 输出说明

### 控制台输出示例

```
📊 正在分析 sh.600000 (A股 日线)...
正在获取 sh.600000 的日K线数据 (2024-01-01 至 2025-12-29)...
数据清洗完成：原始数据 492 行，清洗后 492 行
✅ 获取数据 492 根K线
数据修剪完成:
  - 最高价: 52.31 发生时间: 2024-05-06 00:00:00
  - 最低价: 7.53 发生时间: 2025-02-06 00:00:00
  - 选择较早的最低价时间点: 2025-02-06 00:00:00
  - 原始数据: 492 行
  - 修剪后数据: 225 行
  - 丢弃数据: 267 行
K线合并完成：原始 225 根K线合并为 158 根缠论K线
分型识别完成:
  - 顶分型数量: 8
  - 底分型数量: 7
  - 总分型数量: 15
🎯 缠论K线: 158 根
🔺 顶分型: 8 个
🔻 底分型: 7 个
✅ HTML文件已保存: results/sh.600000_2024-01-01_2025-12-29_daily.html
✅ Plotly交互图表显示成功
```

### 结果文件

分析完成后，在`results/`目录生成HTML文件：
- 文件命名格式：`{前缀}_{股票代码}_{开始日期}_{结束日期}_{数据类型}.html`
- 支持在浏览器中打开查看交互式图表

## ⚙️ 配置说明

### Mootdx最佳线路配置

程序会自动测试通达信服务器并保存最优线路到`best_server.json`：
- 配置文件格式：
```json
{
  "optimal_server": "114.80.63.12:7709",
  "latency_ms": 45.23,
  "last_updated": "2025-12-29T10:30:00"
}
```
- 配置有效期：7天，过期后自动重新测试

### 数据清洗规则

- **价格异常值**：剔除偏离超过3个标准差的数据
- **成交量异常值**：剔除偏离超过5个标准差的数据
- **价格逻辑检查**：确保 high ≥ low，high ≥ open/close，low ≤ open/close

## ⚙️ 配置说明

### Mootdx最佳线路配置

程序会自动测试通达信服务器并保存最优线路到`best_server.json`：
- 配置文件格式：
```json
{
  "optimal_server": "114.80.63.12:7709",
  "latency_ms": 45.23,
  "last_updated": "2025-12-29T10:30:00"
}
```
- 配置有效期：7天，过期后自动重新测试

### 数据缓存配置

Web界面使用本地缓存机制提升数据加载速度：
- 缓存目录：`.cache/stock_data/`
- 缓存TTL：1小时
- 自动清理：超过7天的缓存文件

### 数据清洗规则

- **价格异常值**：剔除偏离超过3个标准差的数据
- **成交量异常值**：剔除偏离超过5个标准差的数据
- **价格逻辑检查**：确保 high ≥ low，high ≥ open/close，low ≤ open/close

### 分批次获取配置

| 市场类型 | 每批数量 | 交易时长 | 复权支持 |
|---------|---------|---------|---------|
| A股分钟 | 800 | 4小时 | ✅ |
| 港股 | 700 | 5.5小时 | ✅ |
| ETF | 800 | 4小时 | ❌ |
| 指数 | 800 | 4小时 | ✅ |

- 最大连续空批次数：2次
- 批次间延迟：1秒
- 自动停止条件：满足所需数量或连续空批2次

## 🐛 常见问题

### Q1: Mootdx连接失败怎么办？

A: 检查网络连接，或手动删除`best_server.json`让程序重新测试线路。

### Q2: 港股数据获取失败？

A: 确保股票代码格式正确（如00700），并检查网络是否可以访问港股服务器。

### Q3: 分钟数据获取为空？

A: 程序已实现分批次获取功能，支持长时间跨度的分钟数据。如果仍然获取失败，建议：
- 缩短时间范围
- 检查网络连接
- 尝试切换数据源（mootdx/baostock）

### Q4: Web界面启动失败？

A: 确保已安装streamlit：
```bash
pip install streamlit
```
然后启动应用：
```bash
streamlit run app/main.py
```

### Q5: 可视化图表无法显示？

A: 确保安装了plotly或matplotlib，并检查浏览器是否支持HTML显示。

## 📚 详细文档

- [BaoStock版本使用说明](docs/baostock_chanlun.md)
- [Mootdx版本使用说明](docs/mootdx_chanlun.md)
- [Web图形界面使用说明](app/README.md)
- [缠论核心算法文档](docs/chanlun_processor.md)
- [可视化工具文档](docs/visualization.md)

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 开发流程
1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 加入讨论组

## 🎉 致谢

感谢以下开源项目：
- BaoStock - 提供免费A股数据
- Mootdx - 通达信数据接口
- Plotly - 交互式可视化库
- Matplotlib - 基础可视化库
- Streamlit - Web应用框架

---

**注意**：本工具仅供学习和研究使用，不构成任何投资建议。投资有风险，入市需谨慎。
