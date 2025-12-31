"""
Streamlit应用工具函数
包含缓存装饰器、辅助函数等
"""

from functools import wraps
import streamlit as st
from datetime import datetime, timedelta


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
    """获取默认结束日期：如果今天是工作日则用今天，否则用上一个工作日"""
    today = datetime.now()
    if is_workday(today):
        return today.date()
    else:
        return get_previous_workday().date()


def normalize_stock_code(code: str) -> str:
    """
    标准化股票代码，自动添加交易所前缀

    Args:
        code: 用户输入的股票代码，可以是完整格式(sh.600000)或仅数字(600000)

    Returns:
        标准化后的股票代码，格式: sh.600000 / sz.000001 / bj.830799 / 00700
    """
    # 去除空白字符并转为大写
    code = str(code).strip().upper()

    # 港股代码处理
    if code.isdigit() and len(code) <= 5:
        # 港股数字代码，如00700 -> 00700
        return code
    elif '.' in code and 'HK' in code.upper():
        # 港股代码格式，如 00700.HK
        return code

    # 如果已经是完整格式(包含点)，直接返回
    if "." in code:
        return code.lower()

    # 如果不是6位数字，保持原样(可能是其他格式)
    if not code.isdigit() or len(code) != 6:
        return code

    # 根据首位数字判断交易所
    first_digit = code[0]

    if first_digit == "6":
        # 上海交易所: 6xxxxx
        return f"sh.{code}"
    elif first_digit in ["0", "3"]:
        # 深圳交易所: 0xxxxx, 3xxxxx
        return f"sz.{code}"
    elif first_digit == "5":
        # 上海ETF: 5xxxxx
        return f"sh.{code}"
    elif first_digit == "1" and len(code) == 6 and code.startswith("15"):
        # 深圳ETF: 15xxxx (如159开头的ETF)
        return f"sz.{code}"
    elif first_digit in ["8", "9", "4"]:
        # 北京交易所: 8xxxxx, 4xxxxx, 9xxxxx
        return f"bj.{code}"
    else:
        # 未知格式，保持原样并提示
        return code


def get_market_type(stock_code: str) -> str:
    """
    根据股票代码判断市场类型

    Args:
        stock_code: 股票代码

    Returns:
        市场类型: 'stock', 'etf', 'index', 'hk'
    """
    code = str(stock_code).strip().upper()

    # 港股代码识别
    if '.' in code and 'HK' in code.upper():
        return 'hk'
    elif code.isdigit() and len(code) <= 5:
        # 港股数字代码，如00700
        return 'hk'

    # 如果包含交易所前缀，提取纯数字部分进行判断
    if '.' in code:
        code = code.split('.')[1]

    # ETF代码识别
    if code.startswith('5') or (code.startswith('15') and len(code) == 6):
        return 'etf'

    # 指数代码识别
    if code.startswith('000') or code.startswith('399') or code.startswith('880'):
        return 'index'

    # A股代码
    return 'stock'


def display_error(message: str):
    """显示错误信息"""
    st.error(f"❌ {message}")


def display_success(message: str):
    """显示成功信息"""
    st.success(f"✅ {message}")


def display_info(message: str):
    """显示提示信息"""
    st.info(f"💡 {message}")


def display_warning(message: str):
    """显示警告信息"""
    st.warning(f"⚠️ {message}")


def display_metric(label: str, value, delta=None):
    """显示指标卡片"""
    st.metric(label, value, delta)
