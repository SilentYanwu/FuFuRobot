# backend/llm/db_mode.py
from typing import Dict
from .sql_generator import generate_sql_with_ai
from backend.utils import create_sql_html

def get_db_response(user_input: str) -> Dict[str, str]:
    """
    获取数据库模式响应（文本转SQL）
    """
    # 使用AI生成SQL
    sql = generate_sql_with_ai(user_input)
    
    return {
        "raw": sql
    }