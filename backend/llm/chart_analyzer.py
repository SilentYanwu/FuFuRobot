# backend/llm/chart_analyzer.py
import re
import pandas as pd
import requests
import json
from typing import Dict, Any
import warnings
from backend.config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL, DEEPSEEK_MODEL

warnings.filterwarnings('ignore', category=UserWarning, module='pandas')

def analyze_data_for_chart(df: pd.DataFrame, sql: str = "", user_input: str = "") -> Dict[str, Any]:
    """
    智能分析数据，返回图表类型和建议配置
    增强版：支持用户指令和智能推荐
    """
    return analyze_data_for_chart_with_instruction(df, sql, user_input)

def analyze_data_for_chart_with_instruction(df: pd.DataFrame, sql: str, user_input: str = "") -> Dict[str, Any]:
    """
    智能分析数据，返回图表类型和配置
    1. 如果用户明确指定图表类型/要求，优先遵循
    2. 否则根据数据特征智能推荐
    """
    if df is None or df.empty:
        return {"chart_type": "none", "config": {}}
    
    # 分析用户指令
    instruction = _extract_chart_instruction(user_input)
    
    # 数据特征分析
    numeric_cols = []
    categorical_cols = []
    datetime_cols = []
    
    for col in df.columns:
        # 1. 先检查是否已经是数值类型
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)
            continue
        
        # 2. 检查是否已经是日期时间类型
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            datetime_cols.append(col)
            continue
        
        # 3. 尝试转换为数值
        try:
            temp_numeric = pd.to_numeric(df[col], errors='coerce')
            if temp_numeric.notna().all():  # 或者使用某个比例阈值
                df[col] = temp_numeric
                numeric_cols.append(col)
                continue
        except:
            pass  # 继续尝试其他类型
        
        # 4. 尝试转换为日期时间
        try:
            temp_datetime = pd.to_datetime(df[col], errors='coerce')
            if temp_datetime.notna().mean() > 0.5:  # 超过50%能转换
                df[col] = temp_datetime
                datetime_cols.append(col)
                continue
        except:
            pass  # 继续下一步
        
        # 5. 否则作为分类数据
        categorical_cols.append(col)
    
    # 构建默认配置
    default_config = {
        "title": "数据可视化",
        "show_title": True,
        "show_legend": len(numeric_cols) > 1 or len(categorical_cols) > 1,
        "animation": True
    }
    
    # 直接智能推荐
    config = _call_deepseek_for_chart(user_input, df, sql, numeric_cols, categorical_cols, datetime_cols)
    config.update(default_config)
    
    return {
        "chart_type": config["chart_type"],
        "config": config,
        "instruction_followed": False,
        "explicit_instruction": instruction
    }
        

def _extract_chart_instruction(user_input: str) -> Dict[str, Any]:
    """
    从用户输入中提取图表指令
    返回格式: {"chart_type": "类型", "requirements": {具体要求}}
    """
    user_input_lower = user_input.lower()
    
    # 图表类型映射
    chart_keywords = {
        "柱状图": "bar_chart",
        "柱状": "bar_chart",
        "条形图": "bar_chart",
        "条形": "bar_chart",
        "折线图": "line_chart",
        "折线": "line_chart",
        "饼图": "pie_chart",
        "饼状图": "pie_chart",
        "散点图": "scatter_chart",
        "散点": "scatter_chart",
        "雷达图": "radar_chart",
        "雷达": "radar_chart",
        "热力图": "heatmap",
        "地图": "map_chart",
        "仪表盘": "gauge"
    }
    
    # 检查用户是否明确指定了图表类型
    explicit_chart_type = None
    explicit_chart_name = None
    
    for chinese_name, english_type in chart_keywords.items():
        if chinese_name in user_input:
            explicit_chart_type = english_type
            explicit_chart_name = chinese_name
            break
    
    # 检查是否有特定的绘图要求
    requirements = {}
    
    # 提取X轴要求
    x_axis_patterns = [
        r"以([^为]+)为.*[xX]轴",
        r"用([^做]+)做.*[xX]轴",
        r"[xX]轴.*用([^，。]+)",
        r"横轴.*是([^，。]+)"
    ]
    for pattern in x_axis_patterns:
        match = re.search(pattern, user_input)
        if match:
            requirements["x_axis"] = match.group(1).strip()
    
    # 提取Y轴要求
    y_axis_patterns = [
        r"以([^为]+)为.*[yY]轴",
        r"用([^做]+)做.*[yY]轴",
        r"[yY]轴.*用([^，。]+)",
        r"纵轴.*是([^，。]+)"
    ]
    for pattern in y_axis_patterns:
        match = re.search(pattern, user_input)
        if match:
            requirements["y_axis"] = match.group(1).strip()
    
    # 检查是否有其他要求
    if "排序" in user_input_lower:
        requirements["sorted"] = True
        if "升序" in user_input_lower or "从小到大" in user_input_lower:
            requirements["sort_order"] = "asc"
        elif "降序" in user_input_lower or "从大到小" in user_input_lower:
            requirements["sort_order"] = "desc"
    
    if "前" in user_input_lower and ("个" in user_input_lower or "名" in user_input_lower):
        # 提取前N个，如"前5个"
        match = re.search(r'前(\d+)(个|名)', user_input_lower)
        if match:
            requirements["limit"] = int(match.group(1))
    
    if "颜色" in user_input_lower:
        requirements["has_color_requirement"] = True
    
    if "标题" in user_input_lower:
        # 尝试提取标题
        title_match = re.search(r'标题[是：:]+([^，。]+)', user_input)
        if title_match:
            requirements["title"] = title_match.group(1).strip()
    
    return {
        "explicit_chart_type": explicit_chart_type,
        "explicit_chart_name": explicit_chart_name,
        "requirements": requirements,
        "has_chart_instruction": explicit_chart_type is not None or len(requirements) > 0
    }

def _call_deepseek_for_chart(user_input: str, df, sql, numeric_cols, categorical_cols, datetime_cols) -> dict:
    """
    调用DeepSeek API智能选择图表类型和配置
    """
    # 准备数据信息
    data_info = {
        "columns": df.columns.tolist(),
        "shape": df.shape,
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "datetime_cols": datetime_cols
    }

    # 构建系统提示 - 优化版本
    system_prompt = f"""你是一个专业而且智能的数据可视化助手。根据用户的输入、sql语句和数据特征，智能选择最适合的图表类型并返回对应的配置参数。

数据信息：
- 数据列: {data_info["columns"]}
- 数据形状: {data_info["shape"]}
- 数值列: {data_info["numeric_cols"]}
- 分类列: {data_info["categorical_cols"]}
- 日期时间列: {data_info["datetime_cols"]}

用户输入: {user_input}
使用的sql语句：{sql}

根据不同的图表类型，请返回对应的JSON配置：

1. 柱状图 (bar_chart):
{{
    "chart_type": "bar_chart",
    "x_axis": "X轴数据列名",
    "y_axis": "Y轴数据列名",
    "title": "图表标题",
    "orientation": "vertical"  # 可选: vertical或horizontal
}}

2. 折线图 (line_chart):
{{
    "chart_type": "line_chart",
    "x_axis": "X轴数据列名",
    "y_axis": "Y轴数据列名",
    "title": "图表标题",
    "smooth": true  # 可选: true或false，是否平滑曲线
}}

3. 饼图 (pie_chart):
{{
    "chart_type": "pie_chart",
    "x_axis": "对应的柱状图的X数据列名",
    "y_axis": "对应的柱状图的Y轴数据列名",
    "name_col": "分类列名（显示在饼图上的名称）",
    "value_col": "数值列名（决定扇形大小的数值）",
    "title": "图表标题"
}}

4. 散点图 (scatter_chart):
{{
    "chart_type": "scatter_chart",
    "x_axis": "X轴数据列名",
    "y_axis": "Y轴数据列名",
    "title": "图表标题",
    "size_col": "可选，决定点大小的列名",
    "color_col": "可选，决定点颜色的列名"
}}

5. 多系列柱状图 (multi_bar_chart):
{{
    "chart_type": "multi_bar_chart",
    "x_axis": "X轴数据列名",
    "y_axes": ["数值列1", "数值列2", ...],
    "title": "图表标题"
}}

图表选择规则：
1. 比较分类数据 -> 柱状图
2. 显示趋势变化 -> 折线图（特别适合时间序列）
3. 显示占比分布 -> 饼图（数据类别不超过10个）
4. 显示相关性 -> 散点图
5. 比较多个数值维度 -> 多系列柱状图

重要指导原则：
1. 如果用户在输入中明确指定了图表类型，请严格按照用户指定的类型生成配置
2. 优先使用合适的列：时间序列用datetime_cols，分类用categorical_cols，数值用numeric_cols
3. 饼图只适合显示占比，不适合精确比较
4. 散点图需要两个数值列
5. 图表标题要简洁明了，体现数据洞察

请根据数据分析结果返回JSON格式的图表配置，只返回JSON，不要其他任何内容！
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"请基于以上数据和查询，智能推荐最适合的图表配置。\n用户输入: {user_input}\n\n请只返回JSON配置:"}
    ]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "stream": False,
        "max_tokens": 800,
        "temperature": 0.1,
        "top_p": 0.9
    }

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        print("请求成功，内容为" + response.text)

        data = response.json()

        if "choices" not in data or len(data["choices"]) == 0:
            raise ValueError("API响应格式错误")

        config_str = data["choices"][0]["message"]["content"].strip()

        # 解析JSON
        try:
            # 清理可能的代码块标记
            if config_str.startswith('```json'):
                config_str = config_str[7:]
            if config_str.startswith('```'):
                config_str = config_str[3:]
            if config_str.endswith('```'):
                config_str = config_str[:-3]
            config_str = config_str.strip()

            print(f"清理后的JSON字符串: {config_str}")
            config = json.loads(config_str)
            
            # 验证配置的完整性
            config = _validate_chart_config(config, df, numeric_cols, categorical_cols, datetime_cols)
            return config
            
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {str(e)}, 使用默认智能推荐配置")
            return _get_smart_chart_config(df, sql, numeric_cols, categorical_cols, datetime_cols)

    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {str(e)}, 使用默认智能推荐配置")
        return _get_smart_chart_config(df, sql, numeric_cols, categorical_cols, datetime_cols)
    except (KeyError, IndexError, ValueError) as e:
        print(f"配置处理失败: {str(e)}, 使用默认智能推荐配置")
        return _get_smart_chart_config(df, sql, numeric_cols, categorical_cols, datetime_cols)

def _validate_chart_config(config, df, numeric_cols, categorical_cols, datetime_cols):
    """验证和修正图表配置"""
    chart_type = config.get("chart_type", "")
    
    # 验证必要的字段存在
    if chart_type == "bar_chart":
        if "x_axis" not in config or "y_axis" not in config:
            config["x_axis"] = categorical_cols[0] if categorical_cols else df.columns[0]
            config["y_axis"] = numeric_cols[0] if numeric_cols else df.columns[1] if len(df.columns) > 1 else df.columns[0]
    
    elif chart_type == "line_chart":
        if "x_axis" not in config or "y_axis" not in config:
            if datetime_cols:
                config["x_axis"] = datetime_cols[0]
            else:
                config["x_axis"] = categorical_cols[0] if categorical_cols else df.columns[0]
            config["y_axis"] = numeric_cols[0] if numeric_cols else df.columns[1] if len(df.columns) > 1 else df.columns[0]
    
    elif chart_type == "pie_chart":
        if "name_col" not in config:
            config["name_col"] = categorical_cols[0] if categorical_cols else df.columns[0]
        if "value_col" not in config:
            config["value_col"] = numeric_cols[0] if numeric_cols else df.columns[1] if len(df.columns) > 1 else df.columns[0]
    
    elif chart_type == "scatter_chart":
        if "x_axis" not in config:
            config["x_axis"] = numeric_cols[0] if numeric_cols else df.columns[0]
        if "y_axis" not in config:
            config["y_axis"] = numeric_cols[1] if len(numeric_cols) > 1 else df.columns[1] if len(df.columns) > 1 else df.columns[0]
    
    elif chart_type == "multi_bar_chart":
        if "x_axis" not in config:
            config["x_axis"] = categorical_cols[0] if categorical_cols else df.columns[0]
        if "y_axes" not in config:
            config["y_axes"] = numeric_cols[:3] if numeric_cols else [df.columns[1]] if len(df.columns) > 1 else [df.columns[0]]
    
    # 确保标题存在
    if "title" not in config:
        config["title"] = f"{chart_type.replace('_', ' ').title()} - 数据分析"
    
    return config

def _get_smart_chart_config(df, sql, numeric_cols, categorical_cols, datetime_cols):
    """智能图表推荐"""
    sql_lower = sql.lower()
    
    # 规则1: 分组统计查询 -> 柱状图
    if "group by" in sql_lower or "count(" in sql_lower:
        x_axis = categorical_cols[0] if categorical_cols else df.columns[0]
        y_axis = numeric_cols[0] if numeric_cols else df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
        return {
            "chart_type": "bar_chart",
            "x_axis": x_axis,
            "y_axis": y_axis,
            "title": f"{y_axis} 按 {x_axis} 统计",
            "chart_style": "group_by"
        }
    
    # 规则2: 有数值列，并且行数适中 -> 柱状图
    elif numeric_cols and len(df) <= 20:
        x_axis = categorical_cols[0] if categorical_cols else df.columns[0]
        y_axis = numeric_cols[0]
        
        return {
            "chart_type": "bar_chart",
            "x_axis": x_axis,
            "y_axis": y_axis,
            "title": f"{y_axis} 统计",
            "chart_style": "simple_bar"
        }
    
    # 规则3: 多个数值列 -> 多系列柱状图
    elif len(numeric_cols) >= 2 and len(df) <= 15:
        return {
            "chart_type": "multi_bar_chart",
            "x_axis": categorical_cols[0] if categorical_cols else df.columns[0],
            "y_axes": numeric_cols[:3],
            "title": "多维度数据对比",
            "chart_style": "multi_series"
        }
    
    # 规则4: 只有分类数据 -> 饼图
    elif categorical_cols and not numeric_cols and len(df) <= 10:
        return {
            "chart_type": "pie_chart",
            "name_col": categorical_cols[0],
            "value_col": categorical_cols[1] if len(categorical_cols) > 1 else categorical_cols[0],
            "title": f"{categorical_cols[0]} 分布",
            "chart_style": "distribution"
        }
    
    # 规则5: 有时间序列数据 -> 折线图
    elif datetime_cols and numeric_cols:
        return {
            "chart_type": "line_chart",
            "x_axis": datetime_cols[0],
            "y_axis": numeric_cols[0],
            "title": f"{numeric_cols[0]} 趋势",
            "smooth": True,
            "chart_style": "time_series"
        }
    
    # 默认：表格
    else:
        return {
            "chart_type": "table",
            "show_table": True,
            "message": "数据量较大，建议使用表格查看"
        }