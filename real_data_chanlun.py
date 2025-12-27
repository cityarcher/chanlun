"""
缠论K线分析工具 - 互动式版本
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from chanlun_processor import ChanlunProcessor
from data_fetcher import AStockDataFetcher

# 优先使用matplotlib可视化，fallback到Plotly版本
try:
    from enhanced_visualizer import enhanced_chanlun_visualization
    VISUALIZATION_AVAILABLE = True
    VISUALIZATION_TYPE = "matplotlib"
except ImportError:
    try:

        from plotly_visualizer import plotly_chanlun_visualization
        VISUALIZATION_AVAILABLE = True
        VISUALIZATION_TYPE = "plotly"
    except ImportError:
        VISUALIZATION_AVAILABLE = False
        VISUALIZATION_TYPE = None


def get_previous_workday():
    """获取上一个工作日"""
    today = datetime.now()
    offset = 1
    while True:
        previous_day = today - timedelta(days=offset)
        # 判断是否为工作日（周一到周五）
        if previous_day.weekday() < 5:  # 0-4 表示周一到周五
            return previous_day.strftime('%Y-%m-%d')
        offset += 1


def analyze_stock(stock_code, start_date, end_date, data_type='daily', frequency='30'):
    """分析单只股票的缠论数据"""
    data_type_name = "日线" if data_type == 'daily' else f"{frequency}分钟线"
    print(f"📊 正在分析 {stock_code} ({data_type_name})...")
    
    # 获取数据
    with AStockDataFetcher() as fetcher:
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
    
    if data.empty:
        print(f"❌ 未能获取到 {stock_code} 的数据")
        return None
    
    print(f"✅ 获取数据 {len(data)} 根K线")
    
    # 执行缠论分析
    processor = ChanlunProcessor()
    result = processor.process_klines(data)
    summary = processor.get_processing_summary()
    
    # 显示简要结果
    print(f"🎯 缠论K线: {summary['chanlun_count']} 根")
    if 'fractal_count' in summary:
        print(f"🔺 顶分型: {summary['top_fractal_count']} 个")
        print(f"🔻 底分型: {summary['bottom_fractal_count']} 个")
    
    # 保存结果
    # filename = f"{stock_code}_chanlun.xlsx"
    # result.to_excel(filename, index=False)
    # print(f"💾 已保存: {filename}")
    
    return result


def get_user_input():
    """获取用户输入"""
    print("\n📝 请输入分析参数（直接回车使用默认值）：")
    
    # 股票代码默认值
    stock_code = input("股票代码（默认 sh.600000）: ").strip()
    if not stock_code:
        stock_code = "sh.600000"
    
    # 开始日期默认值
    start_date = input("开始日期（默认 2024-01-01）: ").strip()
    if not start_date:
        start_date = "2024-01-01"
    
    # 结束日期默认值
    default_end_date = get_previous_workday()
    end_date = input(f"结束日期（默认 {default_end_date}）: ").strip()
    if not end_date:
        end_date = default_end_date
    
    print("\n数据类型选择：")
    print("1. 日线数据（默认）")
    print("2. 分钟线数据")
    data_type_choice = input("请选择 (1-2): ").strip()
    data_type = "minute" if data_type_choice == "2" else "daily"
    
    # 如果选择分钟线，询问frequency
    frequency = "30"
    if data_type == "minute":
        frequency_input = input("分钟K线周期（默认30分钟）: ").strip()
        if frequency_input:
            frequency = frequency_input
    
    return stock_code, start_date, end_date, data_type, frequency


def show_chart(result, stock_code, data_type):
    """显示图表"""
    if not VISUALIZATION_AVAILABLE:
        print("⚠️  可视化模块不可用")
        return
    
    try:
        if VISUALIZATION_TYPE == "plotly":
            # 使用Plotly版本（支持丰富交互功能）
            plotly_chanlun_visualization(result, start_idx=0, bars_to_show=len(result), data_type=data_type)
            print("✅ Plotly交互图表显示成功")
            print("💡 功能说明：")
            print("   - 拖拽缩放：鼠标拖拽可以缩放图表")
            print("   - Hover信息：鼠标悬停显示详细数据")
            print("   - Y轴调节：使用按钮重置或自动调节Y轴")
            print("   - 成交量显示：底部显示成交量柱状图")
        else:
            # 使用matplotlib版本
            enhanced_chanlun_visualization(result, start_idx=0, bars_to_show=len(result), data_type=data_type)
            print("✅ K线图表显示成功")
    except Exception as e:
        print(f"❌ 图表显示失败: {e}")


def main():
    """主函数"""
    print("🎯 缠论K线分析工具")
    print("=" * 40)
    
    if not VISUALIZATION_AVAILABLE:
        print("💡 提示：安装 plotly 或 matplotlib 可启用图表显示")
        print("   - 推荐安装 plotly：pip install plotly pandas")
        print("   - 或安装 matplotlib：pip install matplotlib pandas")
    else:
        viz_type = "Plotly" if VISUALIZATION_TYPE == "plotly" else "Matplotlib"
        print(f"💡 可视化引擎：{viz_type}")
    
    while True:
        try:
            # 获取用户输入
            params = get_user_input()
            if params is None:
                continue
                
            stock_code, start_date, end_date, data_type, frequency = params
            
            # 执行分析
            print(f"\n{'='*50}")
            result = analyze_stock(stock_code, start_date, end_date, data_type, frequency)
            
            if result is not None:
                # 显示图表选项
                data_type_with_freq = data_type if data_type == 'daily' else f"minute_{frequency}"
                show_chart(result, stock_code, data_type_with_freq)
                
                # 显示详细统计
                if 'fractal_type' in result.columns:
                    fractals = result[result['is_fractal']]
                    top_count = len(fractals[fractals['fractal_type'] == 'top'])
                    bottom_count = len(fractals[fractals['fractal_type'] == 'bottom'])
                    print(f"\n📊 分型统计：顶分型{top_count}个，底分型{bottom_count}个")
            
            # 询问是否继续
            continue_choice = input(f"\n{'='*50}\n是否继续分析其他股票？(y/n): ").strip().lower()
            if continue_choice not in ['y', 'yes', '是', '']:
                break
                
        except KeyboardInterrupt:
            print("\n👋 程序退出")
            break
        except Exception as e:
            print(f"❌ 程序出错: {e}")
            continue
    
    print("\n🎉 分析完成！")


if __name__ == "__main__":
    main()