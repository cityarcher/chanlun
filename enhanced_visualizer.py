"""
增强版缠论K线可视化工具
支持鼠标悬停交互和完整的笔绘制功能
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
from datetime import datetime

# 设置中文字体
try:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
except:
    pass

class EnhancedChanlunVisualizer:
    """增强版缠论可视化器"""
    
    def __init__(self):
        self.fig = None
        self.ax = None
        self.data = None
        self.cursor = None
        self.annotation = None
        
    def plot_chanlun_with_interaction(self, data, start_idx=0, bars_to_show=100, data_type='daily', show_plot=True):
        """
        绘制带交互功能的缠论K线图
        
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
            return
        
        # 保存数据引用
        self.data = plot_data
        self.start_idx = start_idx
        
        # 创建图表
        self.fig, self.ax = plt.subplots(figsize=(16, 9))
        
        # 根据数据类型设置标题
        if data_type == 'daily':
            data_type_name = "日线"
        elif data_type.startswith('minute_'):
            freq = data_type.split('_')[1]
            data_type_name = f"{freq}分钟线"
        else:
            data_type_name = "分钟线"
        
        self.fig.suptitle(f'缠论K线分析图表（增强版）- {data_type_name}', fontsize=16, fontweight='bold')
        
        # 绘制K线
        self.plot_candlesticks()
        
        # 标记分型
        if 'is_fractal' in plot_data.columns:
            self.mark_fractals()
        
        # 绘制笔
        if 'is_segment' in plot_data.columns:
            self.draw_segments()
        
        # 设置图表样式
        self.setup_chart_style(end_idx)
        
        # 添加鼠标交互
        self.setup_mouse_interaction()
        
        # 显示图表
        plt.tight_layout()
        if show_plot:
            plt.show()
    
    def plot_candlesticks(self):
        """绘制K线"""
        for i, (idx, row) in enumerate(self.data.iterrows()):
            # 计算颜色
            color = 'red' if row['close'] >= row['open'] else 'green'
            
            # 绘制影线
            self.ax.plot([i, i], [row['low'], row['high']], 
                        color='black', linewidth=0.5, alpha=0.7)
            
            # 绘制实体
            body_height = abs(row['close'] - row['open'])
            body_bottom = min(row['close'], row['open'])
            
            rect = plt.Rectangle((i - 0.3, body_bottom), 0.6, body_height,
                               facecolor=color, edgecolor='black', 
                               linewidth=0.5, alpha=0.8)
            self.ax.add_patch(rect)
        
        # 设置x轴
        x_ticks = range(0, len(self.data), max(1, len(self.data) // 10))
        x_labels = [self.data.iloc[i]['datetime'].strftime('%m-%d') for i in x_ticks]
        self.ax.set_xticks(x_ticks)
        self.ax.set_xticklabels(x_labels, rotation=45)
    
    def mark_fractals(self):
        """标记分型"""
        if 'fractal_type' not in self.data.columns:
            return
            
        fractals = self.data[self.data['is_fractal'] & self.data['fractal_type'].notna()]
        
        for i, (idx, fractal) in enumerate(fractals.iterrows()):
            x_pos = idx - self.start_idx
            
            if fractal['fractal_type'] == 'top':
                # 顶分型
                self.ax.scatter(x_pos, fractal['high'], marker='v', s=150, 
                              color='red', zorder=5, alpha=0.9, label='顶分型' if i == 0 else '')
            else:
                # 底分型
                self.ax.scatter(x_pos, fractal['low'], marker='^', s=150, 
                              color='green', zorder=5, alpha=0.9, label='底分型' if i == 0 else '')
    
    def draw_segments(self):
        """绘制笔"""
        if 'segment_id' not in self.data.columns:
            return
            
        segments = self.data[self.data['is_segment'] & self.data['segment_id'].notna()]
        
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
                start_x = start_point.name - self.start_idx
                start_y = start_point['high'] if start_point.get('fractal_type') == 'top' else start_point['low']
                
                # 笔的终点
                if len(segment_data) > 1:
                    end_point = segment_data.iloc[-1]
                else:
                    # 如果只有一个点，找下一个相反的分型作为终点
                    end_point = self.find_opposite_fractal(start_point)
                
                if end_point is not None:
                    end_x = end_point.name - self.start_idx
                    end_y = end_point['high'] if end_point.get('fractal_type') == 'top' else end_point['low']
                    
                    # 确保在可视范围内
                    if 0 <= start_x < len(self.data) and 0 <= end_x < len(self.data):
                        direction = 'up' if start_y < end_y else 'down'
                        # 上涨笔用红色，下跌笔用绿色
                        color = 'red' if direction == 'up' else 'green'
                        
                        self.ax.plot([start_x, end_x], [start_y, end_y], 
                                   color=color, linewidth=2.5, alpha=0.8,
                                   label='笔' if segment_id == segments['segment_id'].min() else '')
    
    def find_opposite_fractal(self, start_point):
        """查找相反的分型作为笔的终点"""
        start_type = start_point.get('fractal_type')
        opposite_type = 'bottom' if start_type == 'top' else 'top'
        
        # 在后续数据中找到第一个相反类型的分型
        for i in range(start_point.name + 1, len(self.data) + self.start_idx):
            if i < len(self.data.index):
                row = self.data.loc[self.data.index[i - self.start_idx]] if i - self.start_idx < len(self.data) else None
                if row is not None and row.get('is_fractal') and row.get('fractal_type') == opposite_type:
                    return row
        return None
    
    def setup_chart_style(self, end_idx):
        """设置图表样式"""
        self.ax.set_title(f'缠论K线图 (显示 {self.start_idx+1}-{end_idx} 根K线)', 
                         fontsize=14, fontweight='bold')
        self.ax.set_xlabel('时间', fontsize=12)
        self.ax.set_ylabel('价格', fontsize=12)
        
        # 网格
        self.ax.grid(True, alpha=0.3)
        
        # y轴格式
        self.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.2f}'))
        
        # 图例
        handles, labels = self.ax.get_legend_handles_labels()
        if handles:
            # 去重
            unique = []
            seen = set()
            for handle, label in zip(handles, labels):
                if label and label not in seen:
                    unique.append((handle, label))
                    seen.add(label)
            
            if unique:
                handles, labels = zip(*unique)
                self.ax.legend(handles, labels, loc='upper left', fontsize=10)
        
        # 信息框
        price_min = self.data['low'].min()
        price_max = self.data['high'].max()
        
        info_text = (f"价格区间: {price_min:.2f} - {price_max:.2f}\n"
                    f"K线数量: {len(self.data)} 根\n"
                    f"时间范围: {self.data['datetime'].min().strftime('%Y-%m-%d')} - "
                    f"{self.data['datetime'].max().strftime('%Y-%m-%d')}")
        
        self.ax.text(0.02, 0.98, info_text, transform=self.ax.transAxes,
                    fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    def setup_mouse_interaction(self):
        """设置鼠标交互功能"""
        # 创建十字光标
        self.cursor = Cursor(self.ax, useblit=True, color='red', linewidth=1)
        
        # 添加鼠标移动事件
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        
        # 创建注解对象
        self.annotation = self.ax.annotate('', xy=(0, 0), xytext=(10, 10), 
                                         textcoords='offset points',
                                         bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.7),
                                         arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        self.annotation.set_visible(False)
    
    def on_mouse_move(self, event):
        """鼠标移动事件处理"""
        if event.inaxes != self.ax:
            self.annotation.set_visible(False)
            return
        
        # 获取最近的K线索引
        xdata = event.xdata
        if xdata is None:
            return
        
        # 找到最近的K线
        idx = int(round(xdata))
        if 0 <= idx < len(self.data):
            # 获取K线数据
            row = self.data.iloc[idx]
            original_idx = self.data.index[idx]
            
            # 构建信息文本
            info_text = (f"时间: {row['datetime'].strftime('%Y-%m-%d %H:%M')}\n"
                        f"开盘: {row['open']:.2f}\n"
                        f"最高: {row['high']:.2f}\n"
                        f"最低: {row['low']:.2f}\n"
                        f"收盘: {row['close']:.2f}\n"
                        f"涨跌: {row['close'] - row['open']:+.2f}")
            
            # 添加分型信息
            if row.get('is_fractal') and row.get('fractal_type'):
                fractal_type_cn = "顶分型" if row['fractal_type'] == 'top' else "底分型"
                info_text += f"\n🎯 {fractal_type_cn}"
            
            # 添加笔信息
            if row.get('is_segment') and row.get('segment_id') is not None:
                info_text += f"\n📏 笔{row['segment_id']}"
            
            # 更新注解
            self.annotation.set_text(info_text)
            self.annotation.xy = (idx, row['close'])
            self.annotation.set_visible(True)
        else:
            self.annotation.set_visible(False)
        
        # 重绘
        self.fig.canvas.draw_idle()

def enhanced_chanlun_visualization(data, start_idx=0, bars_to_show=100, data_type='daily', save_html=None):
    """
    增强版缠论K线可视化函数（兼容原版本）
    
    Args:
        data: 包含缠论数据的DataFrame
        start_idx: 起始索引
        bars_to_show: 显示的K线数量
        data_type: K线类型 ('daily' 或 'minute')
        save_html: HTML文件路径，如果提供则保存为HTML文件
    
    Returns:
        bool: 如果保存HTML成功则返回True，否则返回False
    """
    visualizer = EnhancedChanlunVisualizer()
    # 如果只是保存HTML，不显示图形
    show_plot = save_html is None
    visualizer.plot_chanlun_with_interaction(data, start_idx, bars_to_show, data_type, show_plot=show_plot)
    
    if save_html:
        try:
            # 将matplotlib图形保存为HTML
            import mpld3
            html_str = mpld3.fig_to_html(visualizer.fig)
            with open(save_html, 'w', encoding='utf-8') as f:
                f.write(html_str)
            return True
        except ImportError:
            print("⚠️  需要安装 mpld3 库来保存matplotlib图为HTML文件")
            print("   安装命令: pip install mpld3")
            return False
        except Exception as e:
            print(f"❌ 保存HTML文件失败: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🎯 缠论K线可视化工具（增强版）")
    print("=" * 50)
    
    # 查找Excel文件演示
    import os
    excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    
    if excel_files:
        print(f"🔍 使用最新的Excel文件: {excel_files[-1]}")
        data = pd.read_excel(excel_files[-1])
        enhanced_chanlun_visualization(data, start_idx=0, bars_to_show=100)
    else:
        print("❌ 没有找到Excel文件，请先运行 real_data_example.py 生成数据")