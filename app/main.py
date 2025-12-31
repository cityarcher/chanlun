"""
Streamlit GUI for Chanlun K-Line Analysis Tool
缠论K线分析工具 - Streamlit图形界面
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加父目录到路径以导入现有模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chanlun_processor import ChanlunProcessor
from mootdx_data_fetcher import MootdxDataFetcher
from baostock_data_fetcher import AStockDataFetcher
from plotly_visualizer import plotly_chanlun_visualization

# 页面配置
st.set_page_config(
    page_title="缠论K线分析工具",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def get_previous_workday():
    """获取上一个工作日"""
    today = datetime.now()
    offset = 1
    while True:
        previous_day = today - timedelta(days=offset)
        if previous_day.weekday() < 5:
            return previous_day
        offset += 1


def is_workday(date=None):
    """判断是否为工作日"""
    if date is None:
        date = datetime.now()
    return date.weekday() < 5


def get_default_end_date():
    """获取默认结束日期"""
    today = datetime.now()
    if is_workday(today):
        return today.date()
    else:
        return get_previous_workday().date()


def normalize_stock_code(code: str) -> str:
    """标准化股票代码"""
    code = str(code).strip().upper()

    # 港股代码处理
    if code.isdigit() and len(code) <= 5:
        return code
    elif '.' in code and 'HK' in code.upper():
        return code

    # 如果已经是完整格式,直接返回
    if "." in code:
        return code.lower()

    # 如果不是6位数字,保持原样
    if not code.isdigit() or len(code) != 6:
        return code

    # 根据首位数字判断交易所
    first_digit = code[0]

    if first_digit == "6":
        return f"sh.{code}"
    elif first_digit in ["0", "3"]:
        return f"sz.{code}"
    elif first_digit == "5":
        return f"sh.{code}"
    elif first_digit == "1" and len(code) == 6 and code.startswith("15"):
        return f"sz.{code}"
    elif first_digit in ["8", "9", "4"]:
        return f"bj.{code}"
    else:
        return code


def get_market_type(stock_code: str) -> str:
    """根据股票代码判断市场类型"""
    code = str(stock_code).strip().upper()

    if '.' in code and 'HK' in code.upper():
        return 'hk'
    elif code.isdigit() and len(code) <= 5:
        return 'hk'

    if '.' in code:
        code = code.split('.')[1]

    if code.startswith('5') or (code.startswith('15') and len(code) == 6):
        return 'etf'

    if code.startswith('000') or code.startswith('399') or code.startswith('880'):
        return 'index'

    return 'stock'


def analyze_stock_with_mootdx(stock_code, start_date, end_date, data_type='daily', frequency='30'):
    """使用mootdx分析股票"""
    market_type = get_market_type(stock_code)
    data_type_name = "日线" if data_type == 'daily' else f"{frequency}分钟线"

    # 获取数据
    with MootdxDataFetcher() as fetcher:
        try:
            if market_type == 'hk':
                data = fetcher.get_hk_stock_data(
                    stock_code=stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    data_type=data_type,
                    frequency=frequency
                )
            elif market_type == 'etf':
                data = fetcher.get_etf_data(
                    etf_code=stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    data_type=data_type,
                    frequency=frequency
                )
            elif market_type == 'index':
                data = fetcher.get_index_data(
                    index_code=stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    data_type=data_type,
                    frequency=frequency
                )
            else:
                if data_type == 'daily':
                    data = fetcher.get_daily_data(
                        stock_code=stock_code,
                        start_date=start_date,
                        end_date=end_date,
                        frequency="d",
                        adjustflag="2"
                    )
                else:
                    data = fetcher.get_minute_data(
                        stock_code=stock_code,
                        start_date=start_date,
                        end_date=end_date,
                        frequency=frequency,
                        adjustflag="2"
                    )
        except Exception as e:
            raise Exception(f"获取{stock_code}数据时出错: {str(e)}")

    if data.empty:
        raise Exception(f"未能获取到{stock_code}的数据")

    # 执行缠论分析
    processor = ChanlunProcessor()
    result = processor.process_klines(data)
    summary = processor.get_processing_summary()

    return result, summary


def analyze_stock_with_baostock(stock_code, start_date, end_date, data_type='daily', frequency='30'):
    """使用baostock分析股票"""
    # 获取数据
    with AStockDataFetcher() as fetcher:
        try:
            if data_type == 'daily':
                data = fetcher.get_daily_data(
                    stock_code=stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    frequency="d",
                    adjustflag="2"
                )
            else:
                data = fetcher.get_minute_data(
                    stock_code=stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    frequency=frequency,
                    adjustflag="2"
                )
        except Exception as e:
            raise Exception(f"获取{stock_code}数据时出错: {str(e)}")

    if data.empty:
        raise Exception(f"未能获取到{stock_code}的数据")

    # 执行缠论分析
    processor = ChanlunProcessor()
    result = processor.process_klines(data)
    summary = processor.get_processing_summary()

    return result, summary


@st.cache_data(ttl=3600)
def cached_analysis(stock_code, start_date, end_date, data_source, data_type, frequency):
    """缓存的分析函数"""
    if data_source == "mootdx":
        return analyze_stock_with_mootdx(stock_code, start_date, end_date, data_type, frequency)
    else:
        return analyze_stock_with_baostock(stock_code, start_date, end_date, data_type, frequency)


def main():
    """主函数"""
    # 标题
    st.markdown('<div class="main-title">📊 缠论K线分析工具</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #4B5563; margin-bottom: 2rem;">支持A股、ETF、港股、指数的多市场缠论分析</p>', unsafe_allow_html=True)

    # 侧边栏参数配置
    with st.sidebar:
        st.markdown("### ⚙️ 参数配置")

        # 股票代码
        stock_code_input = st.text_input(
            "股票代码",
            value="600000",
            help="支持格式: 600000, sh.600000, 00700, 00700.HK 等"
        )

        # 日期范围
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "开始日期",
                value=datetime(2024, 1, 1).date(),
                help="数据获取的起始日期"
            )
        with col2:
            end_date = st.date_input(
                "结束日期",
                value=get_default_end_date(),
                help="数据获取的结束日期"
            )

        # 数据源选择
        data_source = st.selectbox(
            "数据源",
            ["mootdx", "baostock"],
            help="mootdx支持更多市场,baostock更稳定"
        )

        # 数据类型
        data_type = st.radio(
            "数据类型",
            ["daily", "minute"],
            format_func=lambda x: "日线" if x == "daily" else "分钟线",
            horizontal=True
        )

        # 分钟周期
        frequency = "30"
        if data_type == "minute":
            frequency = st.selectbox(
                "分钟周期",
                ["5", "15", "30", "60"],
                index=2,
                help="选择分钟K线的周期"
            )

        # 分析按钮
        analyze_button = st.button("🚀 开始分析", use_container_width=True)

        # 帮助信息
        with st.expander("📖 使用说明"):
            st.markdown("""
            **支持的股票代码格式:**
            - A股: 600000 或 sh.600000
            - 深股: 000001 或 sz.000001
            - ETF: 588000 或 159915
            - 指数: 000001 或 399001
            - 港股: 00700 或 00700.HK

            **数据源说明:**
            - **mootdx**: 支持A股、ETF、港股、指数,数据更新快
            - **baostock**: 仅支持A股,数据更稳定

            **注意事项:**
            - 港股和指数只能使用mootdx数据源
            - 分钟数据可能有限制,建议优先使用日线
            """)

    # 主内容区
    if analyze_button or ('last_analyzed' in st.session_state and st.session_state.last_analyzed == stock_code_input):

        if analyze_button:
            st.session_state.last_analyzed = stock_code_input

        # 标准化股票代码
        stock_code = normalize_stock_code(stock_code_input)

        # 参数校验
        if start_date > end_date:
            st.error("❌ 开始日期不能晚于结束日期!")
            return

        if stock_code.startswith("hk.") or stock_code.endswith(".HK"):
            if data_source == "baostock":
                st.error("❌ Baostock不支持港股数据,请切换到mootdx数据源!")
                return

        # 显示加载状态
        with st.spinner(f"🔄 正在分析 {stock_code}..."):
            try:
                # 调用缓存的分析函数
                result, summary = cached_analysis(
                    stock_code,
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d'),
                    data_source,
                    data_type,
                    frequency
                )

                # 显示成功消息
                st.success(f"✅ 分析完成! 共获取 {len(result)} 根K线")

                # 显示统计信息
                data_type_name = "日线" if data_type == 'daily' else f"{frequency}分钟线"
                st.markdown("### 📊 分析统计")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("K线数量", summary['chanlun_count'])
                with col2:
                    if 'top_fractal_count' in summary:
                        st.metric("顶分型", summary['top_fractal_count'])
                with col3:
                    if 'bottom_fractal_count' in summary:
                        st.metric("底分型", summary['bottom_fractal_count'])

                # 生成图表
                st.markdown("### 📈 缠论K线图表")
                st.markdown(f'<div class="chart-container">', unsafe_allow_html=True)

                data_type_with_freq = data_type if data_type == 'daily' else f"minute_{frequency}"
                chart_obj = plotly_chanlun_visualization(
                    result,
                    start_idx=0,
                    bars_to_show=len(result),
                    data_type=data_type_with_freq,
                    return_fig=True,
                    stock_code=stock_code
                )

                if chart_obj is not None:
                    # 转换为HTML并显示
                    html_string = chart_obj.to_html(include_plotlyjs='cdn', full_html=False)
                    st.components.v1.html(html_string, height=800, scrolling=True)
                else:
                    st.error("❌ 图表生成失败!")

                st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ 分析失败: {str(e)}")
                st.info("💡 提示: 请检查网络连接或尝试切换数据源")


if __name__ == "__main__":
    main()
