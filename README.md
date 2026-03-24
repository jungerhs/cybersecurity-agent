# 网络安全知识问答助手

基于LangChain框架构建的企业级网络安全知识问答系统，采用RAG（检索增强生成）和Agent（智能代理）技术，为用户提供准确、实时的网络安全知识解答。

## 核心特性

- **多格式文档支持**：支持PDF、Markdown、TXT等格式的文档加载与检索
- **智能Agent**：基于ReAct模式的智能代理，自动选择最佳工具
- **实时网络搜索**：集成DuckDuckGo搜索引擎，获取最新安全信息
- **多轮对话**：支持复杂查询和上下文理解
- **知识来源引用**：答案自动引用文档来源
- **技术术语解释**：自动解释网络安全专业术语
- **敏感信息过滤**：自动脱敏处理敏感信息

## 技术架构

### 技术栈
- **框架**：LangChain (v1.0+)
- **向量存储**：ChromaDB
- **Embedding模型**：OpenAI text-embedding-ada-002
- **LLM**：OpenAI gpt-4o
- **Agent类型**：create_agent (LangChain 1.0+ 标准)

### 选择ChromaDB的理由
- 开源免费，易于部署
- 支持持久化存储
- 提供丰富的API接口
- 与LangChain深度集成
- 支持元数据过滤

### ReAct Agent适用性
ReAct（Reasoning + Acting）模式特别适合网络安全问答场景：
- **推理能力**：能够分析问题并选择合适的工具
- **行动能力**：可以执行文档检索、网络搜索等操作
- **观察反馈**：根据工具返回结果调整策略
- **多轮交互**：支持复杂的多步骤问题解决

## 项目结构

```
.
├── config.py                    # 配置文件
├── data_loader.py               # 文档加载模块
├── vector_store.py              # 向量存储模块
├── agent_config.py              # Agent配置模块
├── qa_system.py                 # 主流程模块
├── app.py                       # Flask后端API服务
├── requirements.txt             # Python依赖包列表
├── frontend/                    # React前端项目
│   ├── src/
│   │   ├── App.tsx             # 主应用组件
│   │   ├── App.css             # 主样式
│   │   ├── api.ts              # API调用封装
│   │   └── components/
│   │       └── ChatInterface.tsx  # 聊天界面组件
│   ├── package.json            # 前端依赖
│   └── index.html              # HTML入口
├── documents/                   # 文档目录
│   ├── OWASP_Top_10.md
│   ├── NIST_Cybersecurity_Framework.md
│   └── Common_Vulnerabilities.md
└── vector_db/                   # 向量数据库（自动生成）
```

## 快速开始

### 环境要求

**Python版本：** 推荐使用Python 3.9-3.13
- Python 3.14+可能遇到Pydantic兼容性问题
- LangChain 1.0+需要Python 3.8+

**Node.js版本：** 18+ (用于前端)

### 1. 安装Python依赖

**重要提示：** 推荐使用Python 3.9-3.13版本，避免Python 3.14+的兼容性问题。

```bash
pip install -r requirements.txt
```

如果遇到导入错误，请查看 [LANGCHAIN_INSTALL.md](LANGCHAIN_INSTALL.md) 获取详细的安装和迁移指南。

### 2. 安装前端依赖

```bash
cd frontend
npm install
cd ..
```

### 3. 配置API密钥

设置OpenAI API密钥环境变量：

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-api-key-here"

# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
```

或者在代码中直接修改 [config.py](config.py) 中的 `OPENAI_API_KEY`。

### 4. 准备文档

将网络安全相关的文档（PDF、Markdown、TXT格式）放入 `documents/` 目录。

已包含示例文档：
- OWASP Top 10 安全风险
- NIST网络安全框架
- 常见网络安全漏洞详解

### 5. 运行系统

#### 方式一：使用Web界面（推荐）

```bash
# 终端1：启动Flask后端
python app.py

# 终端2：启动React前端
cd frontend
npm run dev
```

然后在浏览器中访问 `http://localhost:5173`

#### 方式二：命令行界面

```bash
python qa_system.py
```

首次运行时，系统会自动：
1. 加载文档目录中的所有文档
2. 创建向量存储
3. 初始化Agent
4. 启动交互式问答界面

## 使用示例

### Web界面使用

1. **初始化系统**
   - 打开浏览器访问 `http://localhost:5173`
   - 点击"初始化系统"按钮
   - 等待系统初始化完成

2. **开始提问**
   - 在输入框中输入您的问题
   - 点击发送按钮或按Enter键
   - 系统会返回详细的答案

3. **示例问题**
   - "什么是SQL注入？"
   - "OWASP Top 10包含哪些安全风险？"
   - "解释XSS漏洞的攻击链和防御措施"
   - "NIST网络安全框架的五个核心功能是什么？"

4. **系统管理**
   - 点击右上角设置按钮查看系统状态
   - 可以刷新状态或重置系统

### 命令行界面使用

#### 基本查询

```
您的问题: 什么是SQL注入？
```

系统会从文档库中检索相关信息，并解释SQL注入的原理和防御措施。

#### 复杂查询

```
您的问题: 解释XSS漏洞的攻击链，并给出防御建议
```

Agent会：
1. 使用文档检索工具查找XSS相关信息
2. 分析攻击链的各个阶段
3. 提供具体的防御措施
4. 引用知识来源

#### 实时信息查询

```
您的问题: 查找最新的CVE漏洞信息
```

Agent会使用网络搜索工具获取最新的安全公告。

### 计算相关查询

```
您的问题: 计算风险等级：影响程度8 × 可能性0.5
```

Agent会使用计算工具进行数值计算。

## 核心功能详解

### 1. 文档加载与分块

[data_loader.py](data_loader.py) 提供了智能文档加载功能：

- **支持格式**：PDF、Markdown、TXT
- **分块策略**：使用 `RecursiveCharacterTextSplitter`
- **参数配置**：chunk_size=500，overlap=50
- **上下文保留**：按章节和段落分割，保留语义完整性

### 2. 向量存储

[vector_store.py](vector_store.py) 实现了高效的向量检索：

- **持久化存储**：自动保存和加载向量数据库
- **相似度搜索**：支持多种搜索模式
- **动态更新**：支持添加新文档
- **元数据管理**：记录文档来源、页码等信息

### 3. Agent工具

[agent_config.py](agent_config.py) 定义了三个核心工具：

#### DocRetrievalTool
- 功能：从本地文档库检索信息
- 适用场景：已知安全概念、标准文档查询

#### SearchTool
- 功能：网络搜索最新信息
- 适用场景：最新漏洞、安全新闻、实时数据

#### CalculatorTool
- 功能：数学计算
- 适用场景：风险评分、概率计算、数值分析

### 4. Web界面

#### 前端技术栈
- **框架**：React 18 + TypeScript
- **构建工具**：Vite
- **样式**：CSS3 + CSS Variables
- **HTTP客户端**：Axios
- **Markdown渲染**：react-markdown

#### 后端API接口

##### 健康检查
```http
GET /api/health
```

##### 初始化系统
```http
POST /api/init
Content-Type: application/json

{
  "force_rebuild": false
}
```

##### 查询问题
```http
POST /api/query
Content-Type: application/json

{
  "question": "什么是SQL注入？",
  "include_sources": true
}
```

##### 获取系统状态
```http
GET /api/status
```

##### 添加文档
```http
POST /api/add-documents
Content-Type: application/json

{
  "file_path": "path/to/file.pdf",
  "directory": "path/to/directory"
}
```

##### 重置系统
```http
POST /api/reset
```

### 4. 主流程

[qa_system.py](qa_system.py) 实现了完整的问答流程：

1. **初始化**：加载文档、创建向量存储、初始化Agent
2. **查询处理**：接收用户问题
3. **Agent执行**：ReAct循环（思考-行动-观察）
4. **答案生成**：整合检索结果，生成答案
5. **后处理**：术语解释、敏感信息过滤、来源引用

### 5. Web界面流程

[app.py](app.py) 提供了Flask后端API服务：

1. **启动服务**：Flask服务器监听5000端口
2. **API路由**：提供RESTful API接口
3. **CORS支持**：允许前端跨域访问
4. **静态文件**：提供前端构建后的静态文件

[frontend/src/App.tsx](frontend/src/App.tsx) 实现了React前端界面：

1. **状态管理**：管理系统初始化状态、消息列表
2. **API调用**：通过Axios调用后端API
3. **UI渲染**：展示聊天界面和系统状态
4. **交互处理**：处理用户输入和系统响应

## 配置说明

### 模型配置

在 [config.py](config.py) 中可以调整：

```python
MODEL_CONFIG = {
    "llm_model": "gpt-4o",           # LLM模型
    "temperature": 0.7,              # 生成温度
    "max_tokens": 2000,              # 最大token数
    "embedding_model": "text-embedding-ada-002"  # Embedding模型
}
```

### 文档配置

```python
DOCUMENT_CONFIG = {
    "documents_path": "documents",    # 文档目录
    "chunk_size": 500,               # 分块大小
    "chunk_overlap": 50,             # 重叠大小
    "supported_formats": [".pdf", ".md", ".txt"]  # 支持格式
}
```

### 检索配置

```python
RETRIEVAL_CONFIG = {
    "top_k": 5,                      # 返回结果数
    "score_threshold": 0.7           # 相似度阈值
}
```

### 前端配置

在 [frontend/src/api.ts](frontend/src/api.ts) 中可以调整API基础URL：

```typescript
const API_BASE_URL = 'http://localhost:5000/api';
```

## 高级用法

### 命令行编程方式使用

```python
from qa_system import CyberSecurityQASystem

# 初始化系统
qa_system = CyberSecurityQASystem()
qa_system.initialize()

# 查询
result = qa_system.query("什么是SQL注入？")
print(result['answer'])

# 添加新文档
qa_system.add_documents(directory="new_documents")

# 获取系统状态
status = qa_system.get_system_status()
print(status)
```

### 自定义工具

可以在 [agent_config.py](agent_config.py) 中添加自定义工具：

```python
class CustomTool:
    def __init__(self):
        self.name = "custom_tool"
        self.description = "自定义工具描述"
    
    def run(self, query: str) -> str:
        # 实现自定义逻辑
        return "结果"
```

## 替代方案

### 本地模型替代

如果不想使用OpenAI API，可以使用本地模型：

1. **Embedding模型**：HuggingFace的 `all-MiniLM-L6-v2`
2. **LLM模型**：`Llama3-8B`、`Qwen` 等

需要修改 [config.py](config.py) 中的模型配置，并使用相应的LangChain集成。

### 向量存储替代

如果不想使用ChromaDB，可以使用FAISS：

- 优点：性能更高，适合大规模数据
- 缺点：不支持持久化，需要手动管理

需要修改 [vector_store.py](vector_store.py) 中的向量存储实现。

## 安全注意事项

1. **API密钥保护**：不要将API密钥提交到版本控制系统
2. **敏感信息过滤**：系统已内置敏感信息脱敏功能
3. **输入验证**：所有用户输入都经过验证
4. **权限控制**：建议在生产环境中添加用户认证

## 故障排除

### 问题：向量存储创建失败

**解决方案**：
- 检查文档目录是否存在
- 确认文档格式是否支持
- 检查API密钥是否正确

### 问题：Agent执行超时

**解决方案**：
- 增加 `max_iterations` 参数
- 检查网络连接
- 优化文档分块大小

### 问题：检索结果不准确

**解决方案**：
- 调整 `chunk_size` 和 `chunk_overlap`
- 增加 `top_k` 参数
- 优化文档内容质量

## 扩展建议

1. **添加更多文档**：持续更新安全知识库
2. **集成更多工具**：如漏洞扫描、威胁情报等
3. **用户界面**：开发Web或移动端界面
4. **多语言支持**：添加多语言翻译功能
5. **日志分析**：记录查询日志，优化系统性能

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交Issue和Pull Request！
