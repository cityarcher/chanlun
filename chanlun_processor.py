"""
缠论K线处理器
实现缠论相关的K线数据处理和分析功能
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional


class ChanlunProcessor:
    """缠论K线处理器"""
    
    def __init__(self):
        """初始化缠论处理器"""
        self.original_data = None
        self.trimmed_data = None
        self.chanlun_data = None
        self.initial_direction = None
        
    def trim_data_by_extremes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        根据极值点修剪K线数据
        
        步骤：
        1. 找到所有K线中的最高价及其对应的datetime
        2. 找到所有K线中的最低价及其对应的datetime  
        3. 取这两个datetime中较小的一个
        4. 丢弃该K线之前的所有数据
        
        Args:
            df: 原始K线数据，必须包含datetime, high, low列
            
        Returns:
            修剪后的DataFrame
        """
        if df.empty:
            print("输入数据为空")
            return pd.DataFrame()
            
        # 检查必需的列
        required_columns = ['datetime', 'high', 'low']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            print(f"缺少必需的列: {missing_cols}")
            return df.copy()
        
        # 复制数据避免修改原数据
        result_df = df.copy()
        
        # 找到最高价的K线及其datetime
        max_high_idx = df['high'].idxmax()
        max_high_datetime = df.loc[max_high_idx, 'datetime']
        max_high_value = df.loc[max_high_idx, 'high']
        
        # 找到最低价的K线及其datetime
        min_low_idx = df['low'].idxmin()
        min_low_datetime = df.loc[min_low_idx, 'datetime']
        min_low_value = df.loc[min_low_idx, 'low']
        
        # 取两个datetime中较小的一个
        earlier_datetime = min(max_high_datetime, min_low_datetime)
        earlier_type = "最高价" if earlier_datetime == max_high_datetime else "最低价"
        
        # 确定初始方向
        if earlier_type == "最高价":
            self.initial_direction = "down"
        else:
            self.initial_direction = "up"
        
        # 找到该datetime对应的索引
        earlier_idx = df[df['datetime'] == earlier_datetime].index[0]
        
        # 丢弃该K线之前的所有数据
        if earlier_idx > 0:
            trimmed_df = df.iloc[earlier_idx:].copy()
            original_count = len(df)
            trimmed_count = len(trimmed_df)
            dropped_count = original_count - trimmed_count
            
            print(f"数据修剪完成:")
            print(f"  - 最高价: {max_high_value} 发生时间: {max_high_datetime}")
            print(f"  - 最低价: {min_low_value} 发生时间: {min_low_datetime}")
            print(f"  - 选择较早的{earlier_type}时间点: {earlier_datetime}")
            print(f"  - 原始数据: {original_count} 行")
            print(f"  - 修剪后数据: {trimmed_count} 行")
            print(f"  - 丢弃数据: {dropped_count} 行")
            
            return trimmed_df
        else:
            print("最早的数据点就是极值点，无需修剪")
            # 确定初始方向
            if earlier_type == "最高价":
                self.initial_direction = "down"
            else:
                self.initial_direction = "up"
            return df.copy()
    
    def check_inclusion(self, k1, k2):
        """
        检查两根K线是否存在包含关系
        
        Args:
            k1, k2: K线数据，包含high, low列
            
        Returns:
            (has_inclusion, included_kline, including_kline)
            has_inclusion: 是否存在包含关系
            included_kline: 被包含的K线
            including_kline: 包含其他K线的K线
        """
        # 判断包含关系
        if (k1['high'] >= k2['high'] and k1['low'] <= k2['low']):
            # k1包含k2
            has_inclusion = True
            included_kline = k2
            including_kline = k1
        elif (k2['high'] >= k1['high'] and k2['low'] <= k1['low']):
            # k2包含k1
            has_inclusion = True
            included_kline = k1
            including_kline = k2
        else:
            # 无包含关系
            has_inclusion = False
            included_kline = None
            including_kline = None
        
        return has_inclusion, included_kline, including_kline
    
    def determine_direction(self, chanlun_klines):
        """
        根据已处理好的缠论K线的最后2根来判断方向
        
        规则：
        - 如果只有0根或1根缠论K线，使用初始方向
        - 如果最后2根K线中，后一根K线高价更高，则方向向上
        - 如果最后2根K线中，后一根K线低价更低，则方向向下
        - 否则保持方向不变
        
        Args:
            chanlun_klines: 已处理的缠论K线列表
            
        Returns:
            方向字符串: "up" 或 "down"
        """
        if len(chanlun_klines) == 0:
            # 没有已处理的K线，使用初始方向
            return getattr(self, 'initial_direction', 'up')
        elif len(chanlun_klines) == 1:
            # 只有1根K线，使用初始方向
            return getattr(self, 'initial_direction', 'up')
        else:
            # 有2根或以上K线，比较最后2根
            last_kline = chanlun_klines[-1]
            second_last_kline = chanlun_klines[-2]
            
            if last_kline['high'] > second_last_kline['high']:
                return "up"
            elif last_kline['low'] < second_last_kline['low']:
                return "down"
            else:
                # 如果高价没有更高，低价也没有更低，保持当前方向
                return chanlun_klines[-1].get('direction', 'up')
    
    def merge_klines(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        基于包含关系合并K线生成缠论K线
        
        规则：
        1. 只有存在包含关系的K线才合并
        2. 包含关系：一根K线完全包含另一根K线（即高低价都包含另一根的高低价）
        3. 方向判断：根据已经处理好的缠论K线的最后2根来判断方向
           - 如果后一根K线高价更高，方向向上
           - 如果后一根K线低价更低，方向向下
        4. 合并规则：
           - 向上时：高价取高者，低价取高者
           - 向下时：高价取低者，低价取低者
        5. 缠论K线的开盘价为第一根K线开盘价，收盘价为最后一根K线收盘价
        
        Args:
            df: 修剪后的K线数据
            
        Returns:
            合并后的缠论K线DataFrame
        """
        if df.empty or len(df) < 2:
            print("数据不足，无法合并")
            return df.copy()
        
        required_columns = ['datetime', 'open', 'high', 'low', 'close']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            print(f"缺少必需的列: {missing_cols}")
            return df.copy()
        
        # 检查volume和amount列，如果不存在则创建默认值
        if 'volume' not in df.columns:
            df = df.copy()
            df['volume'] = 0
            print("警告：缺少volume列，使用默认值0")
        
        if 'amount' not in df.columns:
            df = df.copy()
            df['amount'] = 0
            print("警告：缺少amount列，使用默认值0")
        
        print(f"开始基于包含关系合并K线...")
        
        chanlun_klines = []
        i = 0
        
        while i < len(df):
            current_kline = df.iloc[i]
            chanlun_group = [current_kline]
            j = i + 1
            
            # 尝试合并后续有包含关系的K线
            while j < len(df):
                next_kline = df.iloc[j]
                
                # 检查当前合并组的最后一根K线与下一根K线是否有包含关系
                last_in_group = chanlun_group[-1]
                has_inclusion, included, including = self.check_inclusion(last_in_group, next_kline)
                
                if has_inclusion:
                    # 有包含关系，判断方向
                    current_direction = self.determine_direction(chanlun_klines)
                    
                    # 根据方向合并
                    if current_direction == "up":
                        merged_high = max(including['high'], included['high'])
                        merged_low = max(including['low'], included['low'])
                    else:  # down
                        merged_high = min(including['high'], included['high'])
                        merged_low = min(including['low'], included['low'])
                    
                    # 计算合并后的成交量和成交额（累加所有参与合并的K线）
                    merged_volume = sum(kline['volume'] for kline in chanlun_group + [next_kline] if pd.notna(kline.get('volume', 0)))
                    merged_amount = sum(kline['amount'] for kline in chanlun_group + [next_kline] if pd.notna(kline.get('amount', 0)))
                    
                    # 创建合并后的K线
                    merged_kline = pd.Series({
                        'datetime': chanlun_group[0]['datetime'],  # ✅ 正确：使用第一根的时间
                        'open': chanlun_group[0]['open'],
                        'high': merged_high,
                        'low': merged_low,
                        'close': next_kline['close'],
                        'volume': merged_volume,
                        'amount': merged_amount
                    })
                    
                    # 用合并后的K线替换最后一根K线
                    chanlun_group[-1] = merged_kline
                    j += 1
                else:
                    # 无包含关系，停止合并
                    break
            
            # 将合并组的第一根K线作为缠论K线
            if len(chanlun_group) > 0:
                final_kline = chanlun_group[-1]
                
                # 确定这根缠论K线的方向
                direction = self.determine_direction(chanlun_klines)
                
                # 计算整个合并组的成交量和成交额之和
                total_volume = sum(kline.get('volume', 0) for kline in chanlun_group if pd.notna(kline.get('volume', 0)))
                total_amount = sum(kline.get('amount', 0) for kline in chanlun_group if pd.notna(kline.get('amount', 0)))
                
                chanlun_kline = {
                    'datetime': chanlun_group[0]['datetime'],
                    'open': chanlun_group[0]['open'],
                    'high': final_kline['high'],
                    'low': final_kline['low'],
                    'close': final_kline['close'],
                    'volume': total_volume,
                    'amount': total_amount,
                    'direction': direction
                }
                
                chanlun_klines.append(chanlun_kline)
            
            i = j
        
        chanlun_df = pd.DataFrame(chanlun_klines)
        print(f"K线合并完成：原始 {len(df)} 根K线合并为 {len(chanlun_df)} 根缠论K线")
        
        return chanlun_df
    
    def check_top_fractal(self, klines, index):
        """
        检查顶分型
        
        规则：
        - 需要连续3根K线：第1、2、3根K线
        - 第2根K线的高点必须是3根中最高的
        - 第1根和第3根K线的高点都低于第2根
        
        Args:
            klines: 缠论K线列表
            index: 要检查的中间K线的索引
            
        Returns:
            bool: 是否为顶分型
        """
        if index < 1 or index >= len(klines) - 1:
            return False
        
        k1 = klines[index - 1]  # 左边K线
        k2 = klines[index]      # 中间K线
        k3 = klines[index + 1]  # 右边K线
        
        # 顶分型条件：中间K线的高点是3根中最高的
        return (k2['high'] > k1['high'] and k2['high'] > k3['high'])
    
    def check_bottom_fractal(self, klines, index):
        """
        检查底分型
        
        规则：
        - 需要连续3根K线：第1、2、3根K线
        - 第2根K线的低点必须是3根中最低的
        - 第1根和第3根K线的低点都高于第2根
        
        Args:
            klines: 缠论K线列表
            index: 要检查的中间K线的索引
            
        Returns:
            bool: 是否为底分型
        """
        if index < 1 or index >= len(klines) - 1:
            return False
        
        k1 = klines[index - 1]  # 左边K线
        k2 = klines[index]      # 中间K线
        k3 = klines[index + 1]  # 右边K线
        
        # 底分型条件：中间K线的低点是3根中最低的
        return (k2['low'] < k1['low'] and k2['low'] < k3['low'])
    
    def identify_fractals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        识别缠论K线中的顶分型和底分型
        
        规则：
        1. 对于第1根缠论K线：
           - 如果初始方向为向下，则标记为顶分型
           - 如果初始方向为向上，则标记为底分型
        2. 对于后续K线：
           - 顶分型：中间K线的高点是连续3根K线中最高的
           - 底分型：中间K线的低点是连续3根K线中最低的
        
        Args:
            df: 缠论K线DataFrame
            
        Returns:
            添加了分型标记的DataFrame
        """
        if df.empty:
            print("K线数据为空")
            return df.copy()
        
        print("开始识别顶分型和底分型...")
        
        # 将DataFrame转换为字典列表以便处理
        klines = df.to_dict('records')
        
        # 为结果DataFrame添加分型列
        result_df = df.copy()
        result_df['fractal_type'] = None
        result_df['is_fractal'] = False
        
        # 识别分型
        fractals = []
        
        # 处理第1根K线：根据初始方向标记分型
        if len(klines) > 0 and self.initial_direction is not None:
            first_idx = 0
            if self.initial_direction == 'down':
                # 初始方向向下，第1根K线标记为顶分型
                fractals.append({
                    'index': first_idx,
                    'datetime': klines[first_idx]['datetime'],
                    'type': 'top',
                    'high': klines[first_idx]['high'],
                    'low': klines[first_idx]['low']
                })
                print(f"  - 第1根K线({klines[first_idx]['datetime']})：初始方向向下，标记为顶分型")
            elif self.initial_direction == 'up':
                # 初始方向向上，第1根K线标记为底分型
                fractals.append({
                    'index': first_idx,
                    'datetime': klines[first_idx]['datetime'],
                    'type': 'bottom',
                    'high': klines[first_idx]['high'],
                    'low': klines[first_idx]['low']
                })
                print(f"  - 第1根K线({klines[first_idx]['datetime']})：初始方向向上，标记为底分型")
        
        # 处理后续K线：识别顶分型和底分型
        for i in range(1, len(klines)):  # 从第2根K线开始
            is_top = self.check_top_fractal(klines, i)
            is_bottom = self.check_bottom_fractal(klines, i)
            
            if is_top:
                fractals.append({
                    'index': i,
                    'datetime': klines[i]['datetime'],
                    'type': 'top',
                    'high': klines[i]['high'],
                    'low': klines[i]['low']
                })
            elif is_bottom:
                fractals.append({
                    'index': i,
                    'datetime': klines[i]['datetime'],
                    'type': 'bottom',
                    'high': klines[i]['high'],
                    'low': klines[i]['low']
                })
        
        # 标记分型
        for fractal in fractals:
            idx = fractal['index']
            result_df.loc[idx, 'fractal_type'] = fractal['type']
            result_df.loc[idx, 'is_fractal'] = True
        
        # 统计信息
        top_count = len([f for f in fractals if f['type'] == 'top'])
        bottom_count = len([f for f in fractals if f['type'] == 'bottom'])
        
        print(f"分型识别完成:")
        print(f"  - 顶分型数量: {top_count}")
        print(f"  - 底分型数量: {bottom_count}")
        print(f"  - 总分型数量: {len(fractals)}")
        
        # 显示分型详细信息
        if fractals:
            print(f"\n分型详细信息:")
            for fractal in fractals[:10]:  # 只显示前10个
                print(f"  - {fractal['type']}: {fractal['datetime']} High:{fractal['high']:.2f} Low:{fractal['low']:.2f}")
            if len(fractals) > 10:
                print(f"  ... 还有 {len(fractals) - 10} 个分型")
        
        return result_df
    
    def filter_fractals_by_extremes(self, df: pd.DataFrame, window: int = 4) -> pd.DataFrame:
        """
        根据极值筛选分型
        
        规则：
        - 对于标记为底分型的K线，如果其低价不是前面4根K线以及后面4根K线（合计9根K线）中低价最低的，则取消其底分型标记
        - 对于标记为顶分型的K线，如果其高价不是前面4根K线以及后面4根K线（合计9根K线）中高价最高的，则取消其顶分型标记
        
        Args:
            df: 包含分型标记的DataFrame
            window: 前后K线的数量，默认为4（总共检查9根K线）
            
        Returns:
            筛选后的DataFrame
        """
        if df.empty or 'is_fractal' not in df.columns:
            print("没有分型数据需要筛选")
            return df
        
        print(f"开始根据{window*2+1}根K线窗口筛选分型...")
        
        result_df = df.copy()
        klines = df.to_dict('records')
        n = len(klines)
        
        removed_count = 0
        
        # 筛选每个分型
        for i in range(n):
            if not result_df.loc[i, 'is_fractal']:
                continue
                
            fractal_type = result_df.loc[i, 'fractal_type']
            if fractal_type is None:
                continue
            
            # 确定窗口范围
            start_idx = max(0, i - window)
            end_idx = min(n - 1, i + window)
            
            # 获取窗口内的所有K线
            window_klines = klines[start_idx:end_idx + 1]
            
            if fractal_type == 'top':
                # 顶分型：检查当前K线的高价是否是窗口内最高的
                current_high = klines[i]['high']
                max_high_in_window = max(k['high'] for k in window_klines)
                
                if current_high < max_high_in_window:
                    # 不是最高的，取消顶分型标记
                    result_df.loc[i, 'fractal_type'] = None
                    result_df.loc[i, 'is_fractal'] = False
                    removed_count += 1
                    
            elif fractal_type == 'bottom':
                # 底分型：检查当前K线的低价是否是窗口内最低的
                current_low = klines[i]['low']
                min_low_in_window = min(k['low'] for k in window_klines)
                
                if current_low > min_low_in_window:
                    # 不是最低的，取消底分型标记
                    result_df.loc[i, 'fractal_type'] = None
                    result_df.loc[i, 'is_fractal'] = False
                    removed_count += 1
        
        # 统计筛选后的结果
        remaining_fractals = result_df[result_df['is_fractal']]
        top_count = len(remaining_fractals[remaining_fractals['fractal_type'] == 'top'])
        bottom_count = len(remaining_fractals[remaining_fractals['fractal_type'] == 'bottom'])
        
        print(f"分型筛选完成:")
        print(f"  - 窗口大小: {window*2+1} 根K线")
        print(f"  - 取消分型标记: {removed_count} 个")
        print(f"  - 保留顶分型: {top_count} 个")
        print(f"  - 保留底分型: {bottom_count} 个")
        print(f"  - 总保留分型: {len(remaining_fractals)} 个")
        
        return result_df
    
    def filter_consecutive_fractals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        筛选连续的同类型分型
        
        规则：
        - 对于连续的顶分型（指顶分型与顶分型之间没有底分型的），仅保留高价大于这些顶分型中其他顶分型高价的那个顶分型，取消其他顶分型的标记
        - 对于连续的底分型（指底分型与底分型之间没有顶分型的），仅保留低价小于这些底分型中其他底分型低价的那个底分型，取消其他底分型的标记
        
        Args:
            df: 包含分型标记的DataFrame
            
        Returns:
            筛选后的DataFrame
        """
        if df.empty or 'is_fractal' not in df.columns:
            print("没有分型数据需要筛选")
            return df
        
        print("开始筛选连续同类型分型...")
        
        result_df = df.copy()
        klines = df.to_dict('records')
        n = len(klines)
        
        removed_count = 0
        
        # 找出所有连续的同类型分型组
        i = 0
        while i < n:
            if not result_df.loc[i, 'is_fractal']:
                i += 1
                continue
            
            current_type = result_df.loc[i, 'fractal_type']
            if current_type is None:
                i += 1
                continue
            
            # 找出连续的同类型分型
            consecutive_group = []
            j = i
            
            while j < n:
                if result_df.loc[j, 'is_fractal'] :
                    if result_df.loc[j, 'fractal_type'] == current_type:
                        consecutive_group.append(j)
                    else:
                        break
                j += 1
            
            # 如果连续组只有1个，不需要筛选
            if len(consecutive_group) <= 1:
                i = j
                continue
            
            # 筛选连续组
            if current_type == 'top':
                # 顶分型：保留高价最高的
                max_high = -float('inf')
                max_high_idx = -1
                
                for idx in consecutive_group:
                    if klines[idx]['high'] > max_high:
                        max_high = klines[idx]['high']
                        max_high_idx = idx
                
                # 取消其他顶分型标记
                for idx in consecutive_group:
                    if idx != max_high_idx:
                        result_df.loc[idx, 'fractal_type'] = None
                        result_df.loc[idx, 'is_fractal'] = False
                        removed_count += 1
                        
            elif current_type == 'bottom':
                # 底分型：保留低价最低的
                min_low = float('inf')
                min_low_idx = -1
                
                for idx in consecutive_group:
                    if klines[idx]['low'] < min_low:
                        min_low = klines[idx]['low']
                        min_low_idx = idx
                
                # 取消其他底分型标记
                for idx in consecutive_group:
                    if idx != min_low_idx:
                        result_df.loc[idx, 'fractal_type'] = None
                        result_df.loc[idx, 'is_fractal'] = False
                        removed_count += 1
            
            i = j
        
        # 统计筛选后的结果
        remaining_fractals = result_df[result_df['is_fractal']]
        top_count = len(remaining_fractals[remaining_fractals['fractal_type'] == 'top'])
        bottom_count = len(remaining_fractals[remaining_fractals['fractal_type'] == 'bottom'])
        
        print(f"连续分型筛选完成:")
        print(f"  - 取消分型标记: {removed_count} 个")
        print(f"  - 保留顶分型: {top_count} 个")
        print(f"  - 保留底分型: {bottom_count} 个")
        print(f"  - 总保留分型: {len(remaining_fractals)} 个")
        
        return result_df
    
    def validate_fractal_relationships(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        验证分型之间的关系（第六步）
        
        规则：
        - 除第一个分型外，如果一个分型是底分型，那么它的低点必须小于它前一个顶分型的高点，也必须低于它后一个顶分型的高点
        - 如果不满足这个条件，那么取消这个底分型的标记
        - 同样的，如果一个分型是顶分型，那么它的高点必须大于它前一个底分型的低点，也必须高于它后一个底分型的低点
        - 如果不满足这个条件，那么取消这个顶分型的标记
        - 如果这一步有取消任何分型标记，那么这一步后要重新第五步连续分型的筛选
        
        Args:
            df: 包含分型标记的DataFrame
            
        Returns:
            验证后的DataFrame
        """
        if df.empty or 'is_fractal' not in df.columns:
            print("没有分型数据需要验证")
            return df
        
        print("开始验证分型之间的关系...")
        
        result_df = df.copy()
        klines = df.to_dict('records')
        n = len(klines)
        
        # 获取所有分型的索引
        fractal_indices = []
        for i in range(n):
            if result_df.loc[i, 'is_fractal']:
                fractal_indices.append(i)
        
        if len(fractal_indices) <= 1:
            print("分型数量不足，跳过关系验证")
            return result_df
        
        removed_count = 0
        
        # 验证每个分型（跳过第一个）
        for i in range(1, len(fractal_indices)):
            current_idx = fractal_indices[i]
            current_fractal_type = result_df.loc[current_idx, 'fractal_type']
            
            if current_fractal_type is None:
                continue
            
            # 找到前一个和后一个相反类型的分型
            prev_opposite_idx = None
            next_opposite_idx = None
            
            # 查找前一个相反类型的分型
            for j in range(i - 1, -1, -1):
                prev_idx = fractal_indices[j]
                prev_type = result_df.loc[prev_idx, 'fractal_type']
                if prev_type is not None and prev_type != current_fractal_type:
                    prev_opposite_idx = prev_idx
                    break
            
            # 查找后一个相反类型的分型
            for j in range(i + 1, len(fractal_indices)):
                next_idx = fractal_indices[j]
                next_type = result_df.loc[next_idx, 'fractal_type']
                if next_type is not None and next_type != current_fractal_type:
                    next_opposite_idx = next_idx
                    break
            
            # 验证分型关系
            if current_fractal_type == 'bottom':
                # 底分型：低点必须小于前一个顶分型的高点和后一个顶分型的高点
                current_low = klines[current_idx]['low']
                valid = True
                
                if prev_opposite_idx is not None:
                    prev_high = klines[prev_opposite_idx]['high']
                    if current_low >= prev_high:
                        valid = False
                        print(f"  - 底分型{current_idx}低点{current_low:.2f}不小于前一个顶分型{prev_opposite_idx}高点{prev_high:.2f}")
                
                if valid and next_opposite_idx is not None:
                    next_high = klines[next_opposite_idx]['high']
                    if current_low >= next_high:
                        valid = False
                        print(f"  - 底分型{current_idx}低点{current_low:.2f}不小于后一个顶分型{next_opposite_idx}高点{next_high:.2f}")
                
                if not valid:
                    result_df.loc[current_idx, 'fractal_type'] = None
                    result_df.loc[current_idx, 'is_fractal'] = False
                    removed_count += 1
                    
            elif current_fractal_type == 'top':
                # 顶分型：高点必须大于前一个底分型的低点和后一个底分型的低点
                current_high = klines[current_idx]['high']
                valid = True
                
                if prev_opposite_idx is not None:
                    prev_low = klines[prev_opposite_idx]['low']
                    if current_high <= prev_low:
                        valid = False
                        print(f"  - 顶分型{current_idx}高点{current_high:.2f}不大于前一个底分型{prev_opposite_idx}低点{prev_low:.2f}")
                
                if valid and next_opposite_idx is not None:
                    next_low = klines[next_opposite_idx]['low']
                    if current_high <= next_low:
                        valid = False
                        print(f"  - 顶分型{current_idx}高点{current_high:.2f}不大于后一个底分型{next_opposite_idx}低点{next_low:.2f}")
                
                if not valid:
                    result_df.loc[current_idx, 'fractal_type'] = None
                    result_df.loc[current_idx, 'is_fractal'] = False
                    removed_count += 1
        
        print(f"分型关系验证完成:")
        print(f"  - 取消分型标记: {removed_count} 个")
        
        # 如果有取消分型标记，需要重新执行第五步连续分型筛选
        if removed_count > 0:
            print("  - 检测到分型被取消，重新执行第五步连续分型筛选...")
            result_df = self.filter_consecutive_fractals(result_df)
        
        # 统计最终结果
        final_fractals = result_df[result_df['is_fractal']]
        top_count = len(final_fractals[final_fractals['fractal_type'] == 'top'])
        bottom_count = len(final_fractals[final_fractals['fractal_type'] == 'bottom'])
        
        print(f"  - 最终保留顶分型: {top_count} 个")
        print(f"  - 最终保留底分型: {bottom_count} 个")
        print(f"  - 最终保留分型: {len(final_fractals)} 个")
        
        return result_df
    
    def filter_close_fractals(self, df: pd.DataFrame, min_gap: int = 4) -> pd.DataFrame:
        """
        筛选过于接近的分型对（第六步新增）
        
        规则：
        - 如果一个顶分型An后面出现了一个底分型Bn且索引差小于min_gap，则需要特殊处理
        - 如果一个底分型An后面出现了一个顶分型Bn且索引差小于min_gap，则需要特殊处理
        
        处理逻辑：
        1. 顶分型→底分型情况（索引差<min_gap）：
           - 找到Bn后面的顶分型An+1，比较An+1和An的高价，保留高价更高的
           - 根据保留的顶分型，处理相关的底分型
        
        2. 底分型→顶分型情况（索引差<min_gap）：
           - 找到Bn后面的底分型An+1，比较An+1和An的低价，保留低价更低的
           - 根据保留的底分型，处理相关的顶分型
        
        Args:
            df: 包含分型标记的DataFrame
            min_gap: 最小索引间隔，默认为4
            
        Returns:
            筛选后的DataFrame
        """
        if df.empty or 'is_fractal' not in df.columns:
            print("没有分型数据需要筛选")
            return df
        
        print(f"开始筛选间隔小于{min_gap}的接近分型...")
        
        result_df = df.copy()
        klines = df.to_dict('records')
        n = len(klines)
        
        # 获取所有分型的索引和类型
        fractal_indices = []
        for i in range(n):
            if result_df.loc[i, 'is_fractal']:
                fractal_indices.append({
                    'index': i,
                    'type': result_df.loc[i, 'fractal_type']
                })
        
        if len(fractal_indices) <= 2:
            print("分型数量不足，跳过接近分型筛选")
            return result_df
        
        removed_count = 0
        processed_pairs = set()  # 避免重复处理同一对分型
        
        # 遍历所有相邻的分型对
        for i in range(len(fractal_indices) - 1):
            current = fractal_indices[i]
            next_fractal = fractal_indices[i + 1]
            
            # 检查是否已经处理过这对分型
            pair_key = (current['index'], next_fractal['index'])
            if pair_key in processed_pairs:
                continue
            
            # 检查索引间隔
            index_gap = next_fractal['index'] - current['index']
            if index_gap >= min_gap:
                continue
            
            processed_pairs.add(pair_key)
            
            # 情况1：顶分型→底分型
            if current['type'] == 'top' and next_fractal['type'] == 'bottom':
                An_idx = current['index']
                Bn_idx = next_fractal['index']
                
                # 找到Bn后面的顶分型An+1
                An1_idx = None
                for j in range(i + 2, len(fractal_indices)):
                    if fractal_indices[j]['type'] == 'top':
                        An1_idx = fractal_indices[j]['index']
                        break
                
                if An1_idx is not None:
                    # 比较An和An+1的高价
                    An_high = klines[An_idx]['high']
                    An1_high = klines[An1_idx]['high']
                    
                    if An1_high > An_high:
                        # 保留An+1，取消An
                        result_df.loc[An_idx, 'fractal_type'] = None
                        result_df.loc[An_idx, 'is_fractal'] = False
                        removed_count += 1
                        print(f"  - 顶分型{An_idx}高价{An_high:.2f}低于后续顶分型{An1_idx}高价{An1_high:.2f}，取消{An_idx}")
                        
                        # 找到An前面的底分型Bn-1
                        Bn1_idx = None
                        for j in range(i - 1, -1, -1):
                            if fractal_indices[j]['type'] == 'bottom':
                                Bn1_idx = fractal_indices[j]['index']
                                break
                        
                        if Bn1_idx is not None:
                            # 比较Bn-1和Bn的低价
                            Bn1_low = klines[Bn1_idx]['low']
                            Bn_low = klines[Bn_idx]['low']
                            
                            if Bn_low < Bn1_low:
                                # 保留Bn，取消Bn-1
                                result_df.loc[Bn1_idx, 'fractal_type'] = None
                                result_df.loc[Bn1_idx, 'is_fractal'] = False
                                removed_count += 1
                                print(f"  - 底分型{Bn1_idx}低价{Bn1_low:.2f}高于后续底分型{Bn_idx}低价{Bn_low:.2f}，取消{Bn1_idx}")
                            else:
                                # 保留Bn-1，取消Bn
                                result_df.loc[Bn_idx, 'fractal_type'] = None
                                result_df.loc[Bn_idx, 'is_fractal'] = False
                                removed_count += 1
                                print(f"  - 底分型{Bn_idx}低价{Bn_low:.2f}不低于前底分型{Bn1_idx}低价{Bn1_low:.2f}，取消{Bn_idx}")
                    else:
                        # 保留An，取消An+1
                        result_df.loc[An1_idx, 'fractal_type'] = None
                        result_df.loc[An1_idx, 'is_fractal'] = False
                        removed_count += 1
                        print(f"  - 顶分型{An1_idx}高价{An1_high:.2f}不高于前顶分型{An_idx}高价{An_high:.2f}，取消{An1_idx}")
                        
                        # 找到An+1后面的底分型Bn+1
                        Bn1_idx = None
                        for j in range(i + 3, len(fractal_indices)):  # 跳过An和Bn
                            if fractal_indices[j]['type'] == 'bottom':
                                Bn1_idx = fractal_indices[j]['index']
                                break
                        
                        if Bn1_idx is not None:
                            # 比较Bn+1和Bn的低价
                            Bn1_low = klines[Bn1_idx]['low']
                            Bn_low = klines[Bn_idx]['low']
                            
                            if Bn_low < Bn1_low:
                                # 保留Bn，取消Bn+1
                                result_df.loc[Bn1_idx, 'fractal_type'] = None
                                result_df.loc[Bn1_idx, 'is_fractal'] = False
                                removed_count += 1
                                print(f"  - 底分型{Bn1_idx}低价{Bn1_low:.2f}不低于前底分型{Bn_idx}低价{Bn_low:.2f}，取消{Bn1_idx}")
                            else:
                                # 保留Bn+1，取消Bn
                                result_df.loc[Bn_idx, 'fractal_type'] = None
                                result_df.loc[Bn_idx, 'is_fractal'] = False
                                removed_count += 1
                                print(f"  - 底分型{Bn_idx}低价{Bn_low:.2f}不低于后续底分型{Bn1_idx}低价{Bn1_low:.2f}，取消{Bn_idx}")
            
            # 情况2：底分型→顶分型
            elif current['type'] == 'bottom' and next_fractal['type'] == 'top':
                An_idx = current['index']
                Bn_idx = next_fractal['index']
                
                # 找到Bn后面的底分型An+1
                An1_idx = None
                for j in range(i + 2, len(fractal_indices)):
                    if fractal_indices[j]['type'] == 'bottom':
                        An1_idx = fractal_indices[j]['index']
                        break
                
                if An1_idx is not None:
                    # 比较An和An+1的低价
                    An_low = klines[An_idx]['low']
                    An1_low = klines[An1_idx]['low']
                    
                    if An1_low < An_low:
                        # 保留An+1，取消An
                        result_df.loc[An_idx, 'fractal_type'] = None
                        result_df.loc[An_idx, 'is_fractal'] = False
                        removed_count += 1
                        print(f"  - 底分型{An_idx}低价{An_low:.2f}高于后续底分型{An1_idx}低价{An1_low:.2f}，取消{An_idx}")
                        
                        # 找到An前面的顶分型Bn-1
                        Bn1_idx = None
                        for j in range(i - 1, -1, -1):
                            if fractal_indices[j]['type'] == 'top':
                                Bn1_idx = fractal_indices[j]['index']
                                break
                        
                        if Bn1_idx is not None:
                            # 比较Bn-1和Bn的高价
                            Bn1_high = klines[Bn1_idx]['high']
                            Bn_high = klines[Bn_idx]['high']
                            
                            if Bn_high > Bn1_high:
                                # 保留Bn，取消Bn-1
                                result_df.loc[Bn1_idx, 'fractal_type'] = None
                                result_df.loc[Bn1_idx, 'is_fractal'] = False
                                removed_count += 1
                                print(f"  - 顶分型{Bn1_idx}高价{Bn1_high:.2f}低于后续顶分型{Bn_idx}高价{Bn_high:.2f}，取消{Bn1_idx}")
                            else:
                                # 保留Bn-1，取消Bn
                                result_df.loc[Bn_idx, 'fractal_type'] = None
                                result_df.loc[Bn_idx, 'is_fractal'] = False
                                removed_count += 1
                                print(f"  - 顶分型{Bn_idx}高价{Bn_high:.2f}不高于前顶分型{Bn1_idx}高价{Bn1_high:.2f}，取消{Bn_idx}")
                    else:
                        # 保留An，取消An+1
                        result_df.loc[An1_idx, 'fractal_type'] = None
                        result_df.loc[An1_idx, 'is_fractal'] = False
                        removed_count += 1
                        print(f"  - 底分型{An1_idx}低价{An1_low:.2f}不低于前底分型{An_idx}低价{An_low:.2f}，取消{An1_idx}")
                        
                        # 找到An+1后面的顶分型Bn+1
                        Bn1_idx = None
                        for j in range(i + 3, len(fractal_indices)):  # 跳过An和Bn
                            if fractal_indices[j]['type'] == 'top':
                                Bn1_idx = fractal_indices[j]['index']
                                break
                        
                        if Bn1_idx is not None:
                            # 比较Bn+1和Bn的高价
                            Bn1_high = klines[Bn1_idx]['high']
                            Bn_high = klines[Bn_idx]['high']
                            
                            if Bn_high > Bn1_high:
                                # 保留Bn，取消Bn+1
                                result_df.loc[Bn1_idx, 'fractal_type'] = None
                                result_df.loc[Bn1_idx, 'is_fractal'] = False
                                removed_count += 1
                                print(f"  - 顶分型{Bn1_idx}高价{Bn1_high:.2f}不高于前顶分型{Bn_idx}高价{Bn_high:.2f}，取消{Bn1_idx}")
                            else:
                                # 保留Bn+1，取消Bn
                                result_df.loc[Bn_idx, 'fractal_type'] = None
                                result_df.loc[Bn_idx, 'is_fractal'] = False
                                removed_count += 1
                                print(f"  - 顶分型{Bn_idx}高价{Bn_high:.2f}不高于后续顶分型{Bn1_idx}高价{Bn1_high:.2f}，取消{Bn_idx}")
        
        print(f"接近分型筛选完成:")
        print(f"  - 取消分型标记: {removed_count} 个")
        
        # 如果有取消分型标记，需要重新执行第五步连续分型筛选
        if removed_count > 0:
            print("  - 检测到分型被取消，重新执行第五步连续分型筛选...")
            result_df = self.filter_consecutive_fractals(result_df)
        
        # 统计最终结果
        final_fractals = result_df[result_df['is_fractal']]
        top_count = len(final_fractals[final_fractals['fractal_type'] == 'top'])
        bottom_count = len(final_fractals[final_fractals['fractal_type'] == 'bottom'])
        
        print(f"  - 最终保留顶分型: {top_count} 个")
        print(f"  - 最终保留底分型: {bottom_count} 个")
        print(f"  - 最终保留分型: {len(final_fractals)} 个")
        
        return result_df
    
    def process_fractals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        处理分型识别的入口方法
        
        Args:
            df: 缠论K线DataFrame
            
        Returns:
            包含分型信息的DataFrame
        """
        # 第一步：识别分型（第三步）
        fractals_df = self.identify_fractals(df)
        
        # 保存原始分型统计
        original_fractals = fractals_df[fractals_df['is_fractal']]
        original_top_count = len(original_fractals[original_fractals['fractal_type'] == 'top'])
        original_bottom_count = len(original_fractals[original_fractals['fractal_type'] == 'bottom'])
        
        # 第二步：根据极值筛选分型（第四步）
        extreme_filtered_df = self.filter_fractals_by_extremes(fractals_df)
        extreme_filtered_fractals = extreme_filtered_df[extreme_filtered_df['is_fractal']]
        extreme_filtered_top_count = len(extreme_filtered_fractals[extreme_filtered_fractals['fractal_type'] == 'top'])
        extreme_filtered_bottom_count = len(extreme_filtered_fractals[extreme_filtered_fractals['fractal_type'] == 'bottom'])
        
        # 第三步：筛选连续分型（第五步）
        consecutive_filtered_df = self.filter_consecutive_fractals(extreme_filtered_df)
        consecutive_filtered_fractals = consecutive_filtered_df[consecutive_filtered_df['is_fractal']]
        consecutive_filtered_top_count = len(consecutive_filtered_fractals[consecutive_filtered_fractals['fractal_type'] == 'top'])
        consecutive_filtered_bottom_count = len(consecutive_filtered_fractals[consecutive_filtered_fractals['fractal_type'] == 'bottom'])
        
        # 第四步：验证分型之间的关系（第六步）
        relationship_filtered_df1 = self.validate_fractal_relationships(consecutive_filtered_df)
        # relationship_filtered_fractals1 = relationship_filtered_df1[relationship_filtered_df1['is_fractal']]
        # relationship_filtered_top_count1 = len(relationship_filtered_fractals1[relationship_filtered_fractals1['fractal_type'] == 'top'])
        # relationship_filtered_bottom_count1 = len(relationship_filtered_fractals1[relationship_filtered_fractals1['fractal_type'] == 'bottom'])
        
        # 第五步：筛选接近分型（第七步）
        final_df0 = self.filter_close_fractals(relationship_filtered_df1)
        
        # 第六步：再次验证分型之间的关系（第八步）
        relationship_filtered_df = self.validate_fractal_relationships(final_df0)
        relationship_filtered_fractals = relationship_filtered_df[relationship_filtered_df['is_fractal']]
        relationship_filtered_top_count = len(relationship_filtered_fractals[relationship_filtered_fractals['fractal_type'] == 'top'])
        relationship_filtered_bottom_count = len(relationship_filtered_fractals[relationship_filtered_fractals['fractal_type'] == 'bottom'])

        # 第七步：筛选接近分型（第九步）
        final_df = self.filter_close_fractals(relationship_filtered_df)

        # 保存最终统计
        final_fractals = final_df[final_df['is_fractal']]
        final_top_count = len(final_fractals[final_fractals['fractal_type'] == 'top'])
        final_bottom_count = len(final_fractals[final_fractals['fractal_type'] == 'bottom'])
        
        # 保存筛选统计信息
        self.fractal_filter_stats = {
            'original_fractal_count': len(original_fractals),
            'original_top_count': original_top_count,
            'original_bottom_count': original_bottom_count,
            'extreme_filtered_fractal_count': len(extreme_filtered_fractals),
            'extreme_filtered_top_count': extreme_filtered_top_count,
            'extreme_filtered_bottom_count': extreme_filtered_bottom_count,
            'extreme_removed_count': len(original_fractals) - len(extreme_filtered_fractals),
            'consecutive_filtered_fractal_count': len(consecutive_filtered_fractals),
            'consecutive_filtered_top_count': consecutive_filtered_top_count,
            'consecutive_filtered_bottom_count': consecutive_filtered_bottom_count,
            'consecutive_removed_count': len(extreme_filtered_fractals) - len(consecutive_filtered_fractals),
            'relationship_filtered_fractal_count': len(relationship_filtered_fractals),
            'relationship_filtered_top_count': relationship_filtered_top_count,
            'relationship_filtered_bottom_count': relationship_filtered_bottom_count,
            'relationship_removed_count': len(consecutive_filtered_fractals) - len(relationship_filtered_fractals),
            'close_removed_count': len(relationship_filtered_fractals) - len(final_fractals),
            'final_fractal_count': len(final_fractals),
            'final_top_count': final_top_count,
            'final_bottom_count': final_bottom_count,
            'total_removed_count': len(original_fractals) - len(final_fractals)
        }
        
        return final_df
    
    def process_klines(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        处理K线数据的主入口
        
        Args:
            df: 原始K线数据
            
        Returns:
            处理后的K线数据（包含分型和笔信息）
        """
        self.original_data = df.copy()
        
        # 第一步：根据极值修剪数据
        trimmed_df = self.trim_data_by_extremes(df)
        self.trimmed_data = trimmed_df
        
        # 第二步：合并K线生成缠论K线
        chanlun_df = self.merge_klines(trimmed_df)
        self.chanlun_data = chanlun_df
        
        # 第三步：识别顶分型和底分型
        fractals_df = self.process_fractals(chanlun_df)
        self.fractals_data = fractals_df
        
        # 第四步：识别笔
        segments_df = self.identify_segments(fractals_df)
        self.segments_data = segments_df
        
        return segments_df
    
    def identify_segments(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        识别笔（由分型组成的连续交叉序列）
        
        规则：
        - 第一个分型是顶分型：按照顶分型、底分型、顶分型、底分型、……这样交叉的原则
        - 第一个分型是底分型：按照底分型、顶分型、底分型、顶分型、……这样交叉的原则
        - 一笔由一个顶分型和一个底分型组成
        - 笔与笔之间是连续的
        
        Args:
            df: 包含分型标记的DataFrame
            
        Returns:
            添加了笔标记的DataFrame
        """
        if df.empty or 'is_fractal' not in df.columns:
            print("没有分型数据，无法识别笔")
            return df.copy()
        
        print("开始识别笔...")
        
        result_df = df.copy()
        klines = df.to_dict('records')
        
        # 获取所有有效的分型
        fractals = []
        for i in range(len(klines)):
            if result_df.loc[i, 'is_fractal'] and result_df.loc[i, 'fractal_type'] is not None:
                fractals.append({
                    'index': i,
                    'datetime': klines[i]['datetime'],
                    'type': result_df.loc[i, 'fractal_type'],
                    'high': klines[i]['high'],
                    'low': klines[i]['low']
                })
        
        if len(fractals) < 2:
            print("分型数量不足，无法形成笔")
            result_df['segment_id'] = None
            result_df['is_segment'] = False
            return result_df
        
        # 添加笔相关列
        result_df['segment_id'] = None
        result_df['is_segment'] = False
        result_df['segment_start_idx'] = None
        result_df['segment_end_idx'] = None
        result_df['segment_start_type'] = None
        result_df['segment_end_type'] = None
        
        # 按照交叉原则筛选分型
        filtered_fractals = []
        if len(fractals) > 0:
            # 第一个分型
            filtered_fractals.append(fractals[0])
            expected_type = None
            
            # 根据第一个分型类型确定期望的下一个类型
            if fractals[0]['type'] == 'top':
                expected_type = 'bottom'
            else:
                expected_type = 'top'
            
            # 寻找符合交叉模式的分型
            for i in range(1, len(fractals)):
                if fractals[i]['type'] == expected_type:
                    filtered_fractals.append(fractals[i])
                    # 交换期望类型
                    expected_type = 'top' if expected_type == 'bottom' else 'bottom'
                else:
                    print(f"  - 跳过分型{fractals[i]['index']}({fractals[i]['datetime']})：类型{fractals[i]['type']}不符合期望类型{expected_type}")
        
        print(f"  - 原始分型: {len(fractals)} 个")
        print(f"  - 符合交叉模式的分型: {len(filtered_fractals)} 个")
        
        # 形成笔
        segments = []
        for i in range(len(filtered_fractals) - 1):
            start_fractal = filtered_fractals[i]
            end_fractal = filtered_fractals[i + 1]
            
            segment = {
                'id': i,
                'start_idx': start_fractal['index'],
                'end_idx': end_fractal['index'],
                'start_datetime': start_fractal['datetime'],
                'end_datetime': end_fractal['datetime'],
                'start_type': start_fractal['type'],
                'end_type': end_fractal['type'],
                'start_price': start_fractal['high'] if start_fractal['type'] == 'top' else start_fractal['low'],
                'end_price': end_fractal['high'] if end_fractal['type'] == 'top' else end_fractal['low'],
                'direction': 'down' if start_fractal['type'] == 'top' else 'up'
            }
            segments.append(segment)
        
        # 标记笔
        for segment in segments:
            start_idx = segment['start_idx']
            end_idx = segment['end_idx']
            
            # 标记笔的起点和终点
            result_df.loc[start_idx, 'segment_id'] = segment['id']
            result_df.loc[start_idx, 'is_segment'] = True
            result_df.loc[start_idx, 'segment_start_idx'] = start_idx
            result_df.loc[start_idx, 'segment_end_idx'] = end_idx
            result_df.loc[start_idx, 'segment_start_type'] = segment['start_type']
            result_df.loc[start_idx, 'segment_end_type'] = segment['end_type']
            
            result_df.loc[end_idx, 'segment_id'] = segment['id']
            result_df.loc[end_idx, 'is_segment'] = True
            result_df.loc[end_idx, 'segment_start_idx'] = start_idx
            result_df.loc[end_idx, 'segment_end_idx'] = end_idx
            result_df.loc[end_idx, 'segment_start_type'] = segment['start_type']
            result_df.loc[end_idx, 'segment_end_type'] = segment['end_type']
        
        # 统计信息
        up_segments = [s for s in segments if s['direction'] == 'up']
        down_segments = [s for s in segments if s['direction'] == 'down']
        
        print(f"笔识别完成:")
        print(f"  - 总笔数: {len(segments)}")
        print(f"  - 上升笔: {len(up_segments)}")
        print(f"  - 下降笔: {len(down_segments)}")
        
        # 显示笔详细信息
        if segments:
            print(f"\n笔详细信息:")
            for segment in segments[:10]:  # 只显示前10个
                direction_text = "上升" if segment['direction'] == 'up' else "下降"
                print(f"  - 笔{segment['id']} {direction_text}: {segment['start_type']}{segment['start_idx']}→{segment['end_type']}{segment['end_idx']} "
                      f"{segment['start_price']:.2f}→{segment['end_price']:.2f}")
            if len(segments) > 10:
                print(f"  ... 还有 {len(segments) - 10} 个笔")
        
        # 保存笔数据
        self.segments = segments
        
        return result_df
    
    def get_processing_summary(self) -> dict:
        """
        获取数据处理摘要信息
        
        Returns:
            包含处理信息的字典
        """
        if self.original_data is None:
            return {"status": "尚未处理数据"}
        
        summary = {
            "status": "已完成",
            "original_count": len(self.original_data),
            "initial_direction": self.initial_direction,
        }
        
        if self.trimmed_data is not None:
            summary.update({
                "trimmed_count": len(self.trimmed_data),
                "first_datetime_trimmed": self.trimmed_data['datetime'].min(),
                "last_datetime_trimmed": self.trimmed_data['datetime'].max(),
                "dropped_count": len(self.original_data) - len(self.trimmed_data)
            })
        
        if hasattr(self, 'chanlun_data') and self.chanlun_data is not None:
            summary.update({
                "chanlun_count": len(self.chanlun_data),
                "first_datetime_chanlun": self.chanlun_data['datetime'].min(),
                "last_datetime_chanlun": self.chanlun_data['datetime'].max(),
                "merged_count": len(self.trimmed_data) - len(self.chanlun_data) if self.trimmed_data is not None else 0
            })
        
        if hasattr(self, 'fractals_data') and self.fractals_data is not None:
            fractals = self.fractals_data[self.fractals_data['is_fractal']]
            top_fractals = fractals[fractals['fractal_type'] == 'top']
            bottom_fractals = fractals[fractals['fractal_type'] == 'bottom']
            
            summary.update({
                "fractal_count": len(fractals),
                "top_fractal_count": len(top_fractals),
                "bottom_fractal_count": len(bottom_fractals)
            })
        
        # 添加笔统计信息
        if hasattr(self, 'segments'):
            up_segments = [s for s in self.segments if s['direction'] == 'up']
            down_segments = [s for s in self.segments if s['direction'] == 'down']
            
            summary.update({
                "segment_count": len(self.segments),
                "up_segment_count": len(up_segments),
                "down_segment_count": len(down_segments)
            })
        
        # 添加分型筛选统计信息
        if hasattr(self, 'fractal_filter_stats'):
            summary.update(self.fractal_filter_stats)
        
        return summary


# 使用示例
if __name__ == "__main__":
    # 创建示例数据
    dates = pd.date_range('2024-01-01 09:00:00', periods=100, freq='5min')
    
    # 生成随机OHLC数据，中间设置一个明显的最高点和最低点
    np.random.seed(42)
    base_price = 10
    price_changes = np.random.normal(0, 0.1, 100)
    prices = base_price + np.cumsum(price_changes)
    
    # 在中间位置人为设置最高点和最低点
    prices[30] = 15  # 最高价
    prices[70] = 5   # 最低价
    
    sample_data = pd.DataFrame({
        'datetime': dates,
        'open': prices - np.random.uniform(0, 0.1, 100),
        'high': prices + np.random.uniform(0, 0.1, 100),
        'low': prices - np.random.uniform(0.1, 0.2, 100),
        'close': prices + np.random.uniform(-0.05, 0.05, 100),
        'volume': np.random.randint(1000, 10000, 100)
    })
    
    # 确保价格逻辑正确
    sample_data['high'] = np.maximum(sample_data['high'], sample_data[['open', 'close']].max(axis=1))
    sample_data['low'] = np.minimum(sample_data['low'], sample_data[['open', 'close']].min(axis=1))
    
    print("原始数据样例:")
    print(sample_data.head(10))
    print(f"\n原始数据范围: {sample_data['datetime'].min()} 到 {sample_data['datetime'].max()}")
    print(f"最高价: {sample_data['high'].max()}，最低价: {sample_data['low'].min()}")
    
    # 使用缠论处理器
    processor = ChanlunProcessor()
    chanlun_data = processor.process_klines(sample_data)
    
    print(f"\n缠论K线数据样例:")
    print(chanlun_data.head(10))
    print(f"\n缠论K线范围: {chanlun_data['datetime'].min()} 到 {chanlun_data['datetime'].max()}")
    
    # 显示方向分布
    if 'direction' in chanlun_data.columns:
        direction_counts = chanlun_data['direction'].value_counts()
        print(f"\n方向分布: {direction_counts.to_dict()}")
    
    # 获取处理摘要
    summary = processor.get_processing_summary()
    print(f"\n处理摘要: {summary}")