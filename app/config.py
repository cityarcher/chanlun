"""
Streamlit应用配置文件
包含默认参数和常量定义
"""

from datetime import datetime, timedelta


# 页面配置
PAGE_CONFIG = {
    "page_title": "缠论K线分析工具",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# 默认参数
DEFAULT_PARAMS = {
    "stock_code": "600000",
    "start_date": datetime(2024, 1, 1).date(),
    "data_source": "mootdx",
    "data_type": "daily",
    "frequency": "30"
}

# 数据源信息
DATA_SOURCES = {
    "mootdx": {
        "name": "Mootdx",
        "description": "支持A股、ETF、港股、指数,数据更新快",
        "supported_markets": ["A股", "ETF", "港股", "指数"]
    },
    "baostock": {
        "name": "BaoStock",
        "description": "仅支持A股,数据更稳定",
        "supported_markets": ["A股"]
    }
}

# 数据类型选项
DATA_TYPES = {
    "daily": "日线",
    "minute": "分钟线"
}

# 分钟周期选项
MINUTE_FREQUENCIES = ["5", "15", "30", "60"]

# 市场类型映射
MARKET_TYPES = {
    "stock": "A股",
    "etf": "ETF",
    "index": "指数",
    "hk": "港股"
}

# 缓存配置
CACHE_CONFIG = {
    "ttl": 3600,  # 缓存时间(秒)
    "max_entries": 100  # 最大缓存条目数
}

# UI配置
UI_CONFIG = {
    "chart_height": 800,
    "chart_width": "100%",
    "button_width": "100%"
}
