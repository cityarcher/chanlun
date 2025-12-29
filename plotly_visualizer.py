"""
基于Plotly的缠论K线可视化工具
支持丰富的交互功能：拖拽缩放、hover信息、Y轴调节等
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

class PlotlyChanlunVisualizer:
    """基于Plotly的缠论可视化器"""
    
    def __init__(self):
        self.data = None
        self.fig = None
    
    def _is_trading_time(self, dt):
        """判断是否为交易时间"""
        if pd.isna(dt):
            return False
        
        # 提取时间部分
        time = dt.time()
        
        # A股交易时间：
        # 上午：9:30-11:30
        # 下午：13:00-15:00
        morning_start = pd.Timestamp('09:30:00').time()
        morning_end = pd.Timestamp('11:30:00').time()
        afternoon_start = pd.Timestamp('13:00:00').time()
        afternoon_end = pd.Timestamp('15:00:00').time()
        
        return ((morning_start <= time <= morning_end) or 
                (afternoon_start <= time <= afternoon_end))
        
    def plot_chanlun_with_interaction(self, data, start_idx=0, bars_to_show=100, data_type='daily', show_plot=True):
        """
        绘制带丰富交互功能的缠论K线图
        
        Args:
            data: 包含缠论数据的DataFrame
            start_idx: 起始索引
            bars_to_show: 显示的K线数量
            data_type: K线类型 ('daily' 或 'minute')
            show_plot: 是否显示图形
        """
        # 数据验证
        required_columns = ['datetime', 'open', 'high', 'low', 'close']
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"数据缺少必要列: {col}")
        
        # 确保datetime是datetime类型
        if not pd.api.types.is_datetime64_any_dtype(data['datetime']):
            data['datetime'] = pd.to_datetime(data['datetime'])
        
        # 计算显示范围
        end_idx = min(start_idx + bars_to_show, len(data))
        plot_data = data.iloc[start_idx:end_idx].copy()
        
        if len(plot_data) == 0:
            print("没有数据可以显示")
            return None
        
        # 保存数据引用
        self.data = plot_data
        

        
        # 计算Y轴范围
        yaxis_min = plot_data['low'].min() * 0.98  # 留2%边距
        yaxis_max = plot_data['high'].max() * 1.02  # 留2%边距
        
        # 根据数据类型设置X轴配置
        if data_type == 'daily':
            xaxis_config = dict(
                title='日期',
                type='date',
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            )
            height = 900
        elif data_type.startswith('minute_'):
            freq = data_type.split('_')[1]
            
            # 调试：显示分钟数据的时间范围
            print(f"📊 {freq}分钟K线时间范围:")
            print(f"  - 开始时间: {plot_data['datetime'].min()}")
            print(f"  - 结束时间: {plot_data['datetime'].max()}")
            print(f"  - 数据点数: {len(plot_data)}")
            
            # 设置时间标签
            n_points = len(plot_data)
            if n_points <= 10:
                # 少量数据，显示所有时间点
                tick_positions = list(range(n_points))
                tick_labels = [dt.strftime('%H:%M') for dt in plot_data['datetime']]
            else:
                # 大量数据，选择关键时间点
                step = max(1, n_points // 8)  # 最多8个刻度
                tick_positions = list(range(0, n_points, step))
                tick_labels = [plot_data['datetime'].iloc[i].strftime('%H:%M') for i in tick_positions]
            
            # 分钟K线：使用数值轴，自定义时间标签
            xaxis_config = dict(
                title=f'K线序号 ({freq}分钟)',
                type='linear',  # 使用线性轴而不是日期轴
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                # 自定义刻度标签显示实际时间
                tickmode='array',
                tickvals=tick_positions,
                ticktext=tick_labels
            )
            height = 900
        else:
            xaxis_config = dict(
                title='时间',
                type='date',
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            )
            height = 900
        
        # 创建子图 - 主体图占更大比例
        self.fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,  # 减小间距
            subplot_titles=('K线图', '成交量'),
            row_heights=[0.9, 0.1]  # K线图占85%，成交量图占15%
        )
        
        # 为分钟K线使用数值索引作为横坐标
        if data_type.startswith('minute_'):
            # 使用数值索引，但保留时间信息用于hover
            x_values = list(range(len(plot_data)))
            hover_text = [f"时间: {dt}<br>开: {o:.2f}<br>高: {h:.2f}<br>低: {l:.2f}<br>收: {c:.2f}" 
                        for dt, o, h, l, c in zip(plot_data['datetime'], plot_data['open'], 
                                                  plot_data['high'], plot_data['low'], plot_data['close'])]
            
            candlestick = go.Candlestick(
                x=x_values,
                open=plot_data['open'],
                high=plot_data['high'],
                low=plot_data['low'],
                close=plot_data['close'],
                name='K线',
                increasing_line_color='red',      # 上涨K线为红色
                decreasing_line_color='green',      # 下跌K线为绿色
                hovertext=hover_text,
                hoverinfo='text'
            )
        else:
            # 日线使用datetime
            candlestick = go.Candlestick(
                x=plot_data['datetime'],
                open=plot_data['open'],
                high=plot_data['high'],
                low=plot_data['low'],
                close=plot_data['close'],
                name='K线',
                increasing_line_color='red',      # 上涨K线为红色
                decreasing_line_color='green'      # 下跌K线为绿色
            )
        
        self.fig.add_trace(candlestick, row=1, col=1)
        
        # 标记分型
        if 'is_fractal' in plot_data.columns and 'fractal_type' in plot_data.columns:
            self._add_fractals(plot_data, data_type)
        
        # 绘制笔
        if 'is_segment' in plot_data.columns:
            self._draw_segments(plot_data, data_type)
        
        # 添加成交量
        if 'volume' in plot_data.columns:
            # 计算颜色
            colors = ['red' if close >= open else 'green' 
                     for close, open in zip(plot_data['close'], plot_data['open'])]
            
            if data_type.startswith('minute_'):
                # 分钟K线使用数值索引
                x_values = list(range(len(plot_data)))
                hover_text = [f"时间: {dt}<br>成交量: {v:.2f}" 
                            for dt, v in zip(plot_data['datetime'], plot_data['volume'])]
                
                volume = go.Bar(
                    x=x_values,
                    y=plot_data['volume'],
                    name='成交量',
                    marker_color=colors,
                    opacity=0.7,
                    hovertext=hover_text,
                    hoverinfo='text'
                )
            else:
                # 日线使用datetime
                volume = go.Bar(
                    x=plot_data['datetime'],
                    y=plot_data['volume'],
                    name='成交量',
                    marker_color=colors,
                    opacity=0.7
                )
            
            self.fig.add_trace(volume, row=2, col=1)
        
        # 设置标题
        if data_type == 'daily':
            title = '缠论K线分析图表（Plotly版）- 日线'
        elif data_type.startswith('minute_'):
            freq = data_type.split('_')[1]
            title = f'缠论K线分析图表（Plotly版）- {freq}分钟线'
        else:
            title = '缠论K线分析图表（Plotly版）'
        
        # 更新布局 - 增加坐标调节功能，优化主体图高度
        self.fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=16)
            ),
            height=height,
            showlegend=True,
            xaxis_rangeslider_visible=False,
            dragmode='zoom',  # 允许拖拽缩放
            hovermode='x unified',  # 统一hover模式
            margin=dict(t=50, b=30, l=50, r=30),  # 优化边距，为内容留更多空间
            
            # X轴设置（根据数据类型动态配置）
            xaxis=xaxis_config,
            
            # 主图Y轴设置（带坐标调节）
            yaxis=dict(
                title='价格',
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                zeroline=False,
                range=[yaxis_min, yaxis_max],  # 使用计算的范围
                autorange=False  # 禁用自动范围，使用手动设置
            )
        )
        
        # 如果显示成交量，设置成交量图的Y轴和X轴
        if 'volume' in plot_data.columns:
            # 为成交量图设置X轴格式，确保与K线图一致
            if data_type.startswith('minute_'):
                # 使用与K线图相同的刻度设置
                n_points = len(plot_data)
                if n_points <= 10:
                    tick_positions = list(range(n_points))
                    tick_labels = [dt.strftime('%H:%M') for dt in plot_data['datetime']]
                else:
                    step = max(1, n_points // 8)
                    tick_positions = list(range(0, n_points, step))
                    tick_labels = [plot_data['datetime'].iloc[i].strftime('%H:%M') for i in tick_positions]
                
                self.fig.update_xaxes(
                    title=f'成交量序号',
                    tickmode='array',
                    tickvals=tick_positions,
                    ticktext=tick_labels,
                    row=2, col=1
                )
            
            self.fig.update_layout(
                yaxis2=dict(
                    title='成交量',
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray',
                    zeroline=False
                )
            )
        
        # 添加缩放和重置按钮
        self.fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    buttons=list([
                        dict(
                            args=[{"yaxis.range": [yaxis_min, yaxis_max]}],
                            label="重置Y轴",
                            method="relayout"
                        ),
                        dict(
                            args=[{"yaxis.autorange": True}],
                            label="自动Y轴",
                            method="relayout"
                        )
                    ]),
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.01,
                    xanchor="left",
                    y=1.02,
                    yanchor="top"
                ),
            ]
        )
        
        return self.fig
    
    def _add_fractals(self, plot_data, data_type='daily'):
        """添加分型标记"""
        fractals = plot_data[plot_data['is_fractal'] & plot_data['fractal_type'].notna()]
        
        for idx, fractal in fractals.iterrows():
            # 根据数据类型确定x坐标
            price_value = fractal['high'] if fractal['fractal_type'] == 'top' else fractal['low']
            if data_type.startswith('minute_'):
                # 分钟K线使用数值索引
                x_pos = idx - plot_data.index[0]  # 转换为相对位置
                hover_text = f"时间: {fractal['datetime']}<br>类型: {'顶分型' if fractal['fractal_type'] == 'top' else '底分型'}<br>价格: {price_value:.2f}"
            else:
                # 日线使用datetime
                x_pos = fractal['datetime']
                hover_text = f"时间: {fractal['datetime']}<br>类型: {'顶分型' if fractal['fractal_type'] == 'top' else '底分型'}<br>价格: {price_value:.2f}"
            
            if fractal['fractal_type'] == 'top':
                # 顶分型
                marker = go.Scatter(
                    x=[x_pos],
                    y=[fractal['high']],
                    mode='markers',
                    marker=dict(
                        symbol='triangle-down',
                        size=6,  # 减小到原来的一半
                        color='red'
                    ),
                    name='顶分型' if idx == fractals.index[0] else '',
                    showlegend=bool(idx == fractals.index[0]),
                    hovertext=hover_text,
                    hoverinfo='text'
                )
            else:
                # 底分型
                marker = go.Scatter(
                    x=[x_pos],
                    y=[fractal['low']],
                    mode='markers',
                    marker=dict(
                        symbol='triangle-up',
                        size=6,  # 减小到原来的一半
                        color='green'
                    ),
                    name='底分型' if idx == fractals.index[0] else '',
                    showlegend=bool(idx == fractals.index[0]),
                    hovertext=hover_text,
                    hoverinfo='text'
                )
            
            self.fig.add_trace(marker, row=1, col=1)
    
    def _draw_segments(self, plot_data, data_type='daily'):
        """绘制笔"""
        if 'segment_id' not in plot_data.columns:
            return
            
        segments = plot_data[plot_data['is_segment'] & plot_data['segment_id'].notna()]
        
        if len(segments) == 0:
            print("没有找到笔数据")
            return
        
        # 找到所有笔的端点
        segment_points = []
        for segment_id in segments['segment_id'].unique():
            segment_data = segments[segments['segment_id'] == segment_id]
            if len(segment_data) >= 1:
                # 笔的起点
                start_point = segment_data.iloc[0]
                if data_type.startswith('minute_'):
                    start_x = start_point.name - plot_data.index[0]  # 转换为相对位置
                else:
                    start_x = start_point['datetime']
                start_y = start_point['high'] if start_point.get('fractal_type') == 'top' else start_point['low']
                
                # 笔的终点
                if len(segment_data) > 1:
                    end_point = segment_data.iloc[-1]
                else:
                    # 如果只有一个点，找下一个相反的分型作为终点
                    end_point = self._find_opposite_fractal(start_point, plot_data)
                
                if end_point is not None:
                    if data_type.startswith('minute_'):
                        end_x = end_point.name - plot_data.index[0]  # 转换为相对位置
                    else:
                        end_x = end_point['datetime']
                    end_y = end_point['high'] if end_point.get('fractal_type') == 'top' else end_point['low']
                    
                    direction = 'up' if start_y < end_y else 'down'
                    # 上涨笔用红色，下跌笔用绿色
                    color = 'red' if direction == 'up' else 'green'
                    
                    segment_line = go.Scatter(
                        x=[start_x, end_x],
                        y=[start_y, end_y],
                        mode='lines',
                        line=dict(
                            color=color,
                            width=2.5
                        ),
                        name='笔' if segment_id == segments['segment_id'].min() else '',
                        showlegend=bool(segment_id == segments['segment_id'].min())
                    )
                    
                    self.fig.add_trace(segment_line, row=1, col=1)
    
    def _find_opposite_fractal(self, start_point, plot_data):
        """查找相反的分型作为笔的终点"""
        start_type = start_point.get('fractal_type')
        opposite_type = 'bottom' if start_type == 'top' else 'top'
        
        # 在后续数据中找到第一个相反类型的分型
        for i in range(len(plot_data)):
            if i < len(plot_data):
                row = plot_data.iloc[i]
                if (row.get('is_fractal') and 
                    row.get('fractal_type') == opposite_type and
                    row['datetime'] > start_point['datetime']):
                    return row
        return None
    
    def show(self):
        """显示图表"""
        if self.fig is not None:
            self.fig.show()
        else:
            print("没有可显示的图表")


def plotly_chanlun_visualization(data, start_idx=0, bars_to_show=100, data_type='daily', return_fig=False):
    """
    基于Plotly的缠论K线可视化函数
    
    Args:
        data: 包含缠论数据的DataFrame
        start_idx: 起始索引
        bars_to_show: 显示的K线数量
        data_type: K线类型 ('daily' 或 'minute')
        return_fig: 是否返回Figure对象而不显示
    
    Returns:
        Plotly Figure对象 (当return_fig=True时)
    """
    visualizer = PlotlyChanlunVisualizer()
    # 如果只是返回图形对象，不显示图形
    show_plot = not return_fig
    fig = visualizer.plot_chanlun_with_interaction(data, start_idx, bars_to_show, data_type, show_plot=show_plot)
    
    if return_fig:
        return fig
    else:
        visualizer.show()
        return fig


if __name__ == "__main__":
    print("🎯 缠论K线可视化工具（Plotly版）")
    print("=" * 50)
    
    # 查找Excel文件演示
    import os
    excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    
    if excel_files:
        print(f"🔍 使用最新的Excel文件: {excel_files[-1]}")
        data = pd.read_excel(excel_files[-1])
        plotly_chanlun_visualization(data, start_idx=0, bars_to_show=100)
    else:
        print("❌ 没有找到Excel文件，请先运行分析程序生成数据")