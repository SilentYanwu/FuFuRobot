# backend/api/schemas.py
from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    mode: str  # 'chat' or 'text2sql'

class ClearHistoryRequest(BaseModel):
    confirm: bool = True

class TestAPIRequest(BaseModel):
    test_message: str = "你好，请介绍一下你自己"

class TTSRequest(BaseModel):
    text: str
    mode: str = "chat" # chat or focus

class SQLExecuteRequest(BaseModel):
    sql: str

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str
    chat_history_length: int
    database: str

class SystemInfoResponse(BaseModel):
    deepseek_api_configured: bool
    chat_history_messages: int
    environment: str
    database: str
    features: list

class GobangIntent(BaseModel):
    mentioned: bool = False
    should_open: bool = False
    confidence: float = 0.0
    reason: str = ""

class ChatResponse(BaseModel):
    success: bool
    text: str
    html: Optional[str] = None
    sql: Optional[str] = None
    data: list = []
    chart_config: dict = {}
    chart_type: str = "none"
    operation_result: Optional[dict] = None
    gobang: Optional[GobangIntent] = None
    mode: str

class ConfigSettings(BaseModel):
    DEEPSEEK_API_KEY: str
    DEEPSEEK_API_URL: str
    DEEPSEEK_MODEL: str
    DB_NAME: str
    BACKEND_HOST: str
    BACKEND_PORT: int
    FRONTEND_HOST: str
    FRONTEND_PORT: int

class ConfigResponse(BaseModel):
    success: bool
    config: ConfigSettings

class ConfigRequest(BaseModel):
    config: ConfigSettings
