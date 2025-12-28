# API 模块说明

## 概述

API模块是FuFuRobot后端的核心组件，负责处理前端请求并与数据库和AI模型交互。该模块基于FastAPI框架构建，提供RESTful API接口。

## 目录结构

```
backend/api/
├── __init__.py     # 包初始化文件
├── routers.py      # API路由定义
└── schemas.py      # 数据模型定义
```

## 主要功能

### 1. 路由端点

#### `/api/health`
- **方法**: GET
- **功能**: 健康检查端点
- **返回**: 系统状态、版本、时间戳、聊天历史长度和数据库连接状态

#### `/api/system-info`
- **方法**: GET
- **功能**: 获取系统信息
- **返回**: API配置信息、聊天历史长度、环境信息和系统特性

#### `/api/db-info`
- **方法**: GET
- **功能**: 获取数据库信息
- **返回**: 数据库表结构和相关信息

#### `/api/test-api`
- **方法**: POST
- **功能**: 测试DeepSeek API连接
- **参数**: 测试消息
- **返回**: API测试结果

#### `/api/execute-sql`
- **方法**: POST
- **功能**: 直接执行SQL语句
- **参数**: SQL语句
- **返回**: SQL执行结果

#### `/api/clear-history`
- **方法**: POST
- **功能**: 清除聊天历史
- **参数**: 确认标志
- **返回**: 清除操作结果

#### `/api/chat/stream`
- **方法**: POST
- **功能**: 流式输出接口（仅支持"focus"模式）
- **参数**: 聊天请求
- **返回**: 流式响应

#### `/api/chat`
- **方法**: POST
- **功能**: 主要聊天接口，支持多种模式
- **参数**: 聊天请求
- **返回**: 聊天响应

## Text2SQL 模式详解

### 概述

Text2SQL模式是系统中的一个核心功能，它允许用户使用自然语言查询数据库，系统会自动将自然语言转换为SQL查询并执行，然后以表格或图表形式展示结果。

### 工作流程

#### 1. 请求接收与验证

```python
user_input = request.message.strip()
mode = request.mode
```

系统首先接收用户的输入和请求模式，并进行基本的输入验证。如果输入为空，会返回错误信息。

#### 2. SQL生成

```python
response = get_db_response(user_input)
sql_query = response["raw"]
```

使用AI模型（通过`get_db_response`函数）将用户的自然语言输入转换为SQL查询语句。

#### 3. SQL执行

```python
sql_result = execute_safe_sql(sql_query)
```

系统使用`execute_safe_sql`函数执行生成的SQL查询。这个函数负责安全地执行SQL并返回结果。

#### 4. 结果处理

根据SQL执行的结果类型，系统会进行不同的处理：

##### 4.1 SQL执行失败处理

如果SQL执行失败，系统会：
- 将结果标记为失败
- 返回错误信息
- 仍然显示生成的SQL（用于调试）

##### 4.2 SQL执行成功处理

如果SQL执行成功，系统会：
- 保存SQL查询语句
- 保存查询结果数据
- 显示SQL查询

#### 5. 根据SQL类型进行后续处理

系统会根据SQL的类型（SELECT、INSERT、UPDATE、DELETE）进行不同的处理：

##### 5.1 SELECT查询处理

对于SELECT查询，系统会：

1. **数据转换**：
   ```python
   df = pd.DataFrame(sql_result["data"]) if sql_result["data"] else pd.DataFrame()
   ```
   将查询结果转换为Pandas DataFrame以便后续处理。

2. **图表分析**：
   ```python
   chart_info = analyze_data_for_chart(df, sql_query, user_input)
   ```
   调用AI分析函数，根据数据、SQL查询和用户输入决定最适合的图表类型。

3. **生成文本总结**：
   - 统计记录数量
   - 根据图表类型生成说明
   - 如果用户明确指定了图表类型，会说明已按要求生成
   - 如果系统自动推荐了图表，会说明推荐原因

4. **构建响应**：
   - 设置图表类型和配置
   - 生成文本总结
   - 构建HTML响应

##### 5.2 INSERT/UPDATE/DELETE操作处理

对于增删改操作，系统会：

1. **提取操作结果**：
   ```python
   operation_data = sql_result["data"][0] if sql_result["data"] else {}
   result["operation_result"] = operation_data
   ```

2. **根据操作类型生成反馈信息**：
   - INSERT: "插入成功！"
   - UPDATE: "更新成功！"
   - DELETE: "删除成功！"

3. **构建HTML响应**：
   - 显示操作结果
   - 显示操作类型

#### 6. 异常处理

系统使用try-except块捕获所有异常，并在发生错误时返回适当的错误信息。

### 数据模型

Text2SQL模式使用以下数据模型（在schemas.py中定义）：

```python
class ChatResponse(BaseModel):
    success: bool
    text: str
    html: str
    sql: Optional[str] = None
    data: list = []
    chart_config: dict = {}
    chart_type: str = "none"
    operation_result: Optional[dict] = None
    mode: str
```

### 关键函数

#### `get_db_response(user_input)`

- **功能**: 将用户自然语言输入转换为SQL查询
- **输入**: 用户输入文本
- **输出**: 包含SQL查询的响应对象

#### `execute_safe_sql(sql_query)`

- **功能**: 安全执行SQL查询
- **输入**: SQL查询语句
- **输出**: 包含执行结果的对象，包括成功状态、数据、SQL类型等

#### `analyze_data_for_chart(df, sql_query, user_input)`

- **功能**: 分析数据并确定最适合的图表类型
- **输入**: DataFrame、SQL查询、用户输入
- **输出**: 包含图表类型和配置的对象

### 图表类型支持

系统支持以下图表类型：

- 柱状图 (bar_chart)
- 折线图 (line_chart)
- 饼图 (pie_chart)
- 散点图 (scatter_chart)
- 多系列柱状图 (multi_bar_chart)
- 表格 (table)
- 无图表 (none)

## 使用示例

### 查询示例

用户输入：
```
显示所有学生的成绩分布情况
```

系统处理流程：
1. 将自然语言转换为SQL: `SELECT score, COUNT(*) FROM students GROUP BY score`
2. 执行SQL获取数据
3. 分析数据并推荐使用柱状图
4. 返回包含数据和图表配置的响应

### 增删改示例

用户输入：
```
添加一个新学生，姓名是张三，年龄是18岁
```

系统处理流程：
1. 将自然语言转换为SQL: `INSERT INTO students (name, age) VALUES ('张三', 18)`
2. 执行SQL
3. 返回操作结果

## 注意事项

1. Text2SQL模式依赖于AI模型生成SQL，可能存在生成不准确SQL的风险
2. 系统使用`execute_safe_sql`函数执行SQL，提供了一定的安全保障
3. 对于复杂的查询，建议用户明确指定查询条件
4. 图表推荐基于AI分析，可能不总是符合用户预期，用户可以明确指定图表类型
