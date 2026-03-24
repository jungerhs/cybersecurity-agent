from typing import List, Dict, Any, Optional
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document
from langchain_community.tools import DuckDuckGoSearchRun
import config
import re
import dotenv

dotenv.load_dotenv()


def extract_final_answer(text: str) -> str:
    if not text:
        return "抱歉，无法生成答案。"
    
    if "Final Answer:" in text:
        parts = text.split("Final Answer:")
        if len(parts) > 1:
            final_answer = parts[-1].strip()
            return final_answer
    
    return text


@tool
def doc_retrieval(query: str) -> str:
    """用于从本地网络安全文档库中检索相关信息。当用户询问关于网络安全、漏洞、攻击方式、防御措施等问题时使用此工具。"""
    try:
        retriever = config.get_retriever()
        if retriever is None:
            return "错误: 文档检索器未初始化，请先加载文档库。"
        
        docs = retriever.invoke(query)
        
        if not docs:
            return f"未在文档库中找到与'{query}'相关的信息。"
        
        results = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "未知来源")
            file_name = doc.metadata.get("file_name", "未知文件")
            page = doc.metadata.get("page", "未知页码")
            
            result = f"[文档片段 {i}]\n"
            result += f"来源: {file_name} (页码: {page})\n"
            result += f"内容: {doc.page_content}\n"
            results.append(result)
        
        return "\n".join(results)
    
    except Exception as e:
        return f"文档检索出错: {str(e)}"

@tool
def web_search(query: str) -> str:
    """用于在互联网上搜索最新的网络安全信息、漏洞公告、安全新闻等。当需要获取最新信息或文档库中没有的信息时使用此工具。"""
    try:
        search = DuckDuckGoSearchRun()
        results = search.run(query)
        
        if not results or "No results found" in results:
            return f"未找到与'{query}'相关的网络搜索结果。"
        
        return f"网络搜索结果:\n{results}"
    
    except Exception as e:
        return f"网络搜索出错: {str(e)}"

# @tool
# def calculator(expression: str) -> str:
#     """用于进行数学计算，如计算漏洞评分、风险等级、概率等。当需要进行数值计算时使用此工具。"""
#     try:
#         llm = ChatOpenAI(
#             model=config.MODEL_CONFIG["llm_model"],
#             temperature=config.MODEL_CONFIG["temperature"],
#             max_tokens=config.MODEL_CONFIG["max_tokens"],
#             openai_api_key=config.OPENAI_API_KEY
#         )
#         llm_math = LLMMathChain.from_llm(llm=llm, verbose=True)
#         result = llm_math.run(expression)
#         return f"计算结果: {result}"
    
#     except Exception as e:
#         return f"计算出错: {str(e)}"

class AgentConfig:
    def __init__(self, retriever=None, llm=None):
        self.retriever = retriever
        self.llm = llm or ChatOpenAI(
            model=config.MODEL_CONFIG["llm_model"],
            temperature=config.MODEL_CONFIG["temperature"],
            max_tokens=config.MODEL_CONFIG["max_tokens"]
        )
        
        self.tools = [doc_retrieval, web_search]
        self.agent = None

    def create_agent(self):
        print("正在创建Agent...")
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools
        )
        print("Agent创建成功")
        
        return self.agent

    def run_agent(self, query: str, use_web_search: bool = True) -> str:
        if self.agent is None:
            self.create_agent()
        
        print(f"开始执行Agent查询: {query}")
        print(f"使用网络搜索: {use_web_search}")
        
        try:
            if not use_web_search:
                tools_to_use = [doc_retrieval]
                print("仅使用文档检索工具")
            else:
                tools_to_use = self.tools
                print("使用所有工具（文档检索 + 网络搜索）")
            
            messages = [
                SystemMessage(content=f"你是一个专业的网络安全知识问答助手，擅长解答各种网络安全相关的问题。{'你可以使用网络搜索获取最新信息。' if use_web_search else '你只能使用本地文档库中的信息。'}"),
                HumanMessage(content=f"请使用以下格式回答问题:\n\nQuestion: {query}\nThought: 你应该思考如何回答这个问题\nAction: 要使用的工具名称\nAction Input: 工具的输入参数\nObservation: 工具返回的结果\n... (这个 Thought/Action/Action Input/Observation 可以重复 N 次)\nThought: 我现在知道最终答案了\nFinal Answer: 对原始问题的最终答案\n\n开始!")
            ]
            result = self.agent.invoke({"messages": messages, "tools": tools_to_use})
            
            if isinstance(result, dict):
                answer = result.get("output", result.get("messages", [""])[-1].content if result.get("messages") else "抱歉，无法生成答案。")
            elif hasattr(result, 'content'):
                answer = result.content
            elif isinstance(result, list) and len(result) > 0:
                answer = result[-1].content if hasattr(result[-1], 'content') else str(result[-1])
            else:
                answer = str(result) if result else "抱歉，无法生成答案。"
            
            answer = extract_final_answer(answer)
            
            print(f"Agent查询完成，返回答案长度: {len(answer)}")
            return answer
        
        except Exception as e:
            print(f"执行Agent时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"执行Agent时出错: {str(e)}"

    def update_retriever(self, retriever) -> None:
        self.retriever = retriever

    def get_tools_info(self) -> List[Dict[str, str]]:
        return [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in self.tools
        ]

def mask_sensitive_info(text: str, sensitive_keywords: List[str] = None) -> str:
    if sensitive_keywords is None:
        sensitive_keywords = config.SECURITY_CONFIG["sensitive_keywords"]
    
    mask_pattern = config.SECURITY_CONFIG["mask_pattern"]
    
    for keyword in sensitive_keywords:
        pattern = re.compile(
            rf'({keyword}["\':\s]*[^\s,，。！？\n]+)',
            re.IGNORECASE
        )
        text = pattern.sub(rf'\1{mask_pattern}', text)
    
    return text

def format_answer_with_sources(answer: str, sources: List[Document]) -> str:
    if not sources:
        return answer
    
    sources_section = "\n\n【知识来源】\n"
    for i, source in enumerate(sources, 1):
        file_name = source.metadata.get("file_name", "未知文件")
        page = source.metadata.get("page", "未知页码")
        sources_section += f"{i}. {file_name} (页码: {page})\n"
    
    return answer + sources_section

def explain_technical_terms(answer: str) -> str:
    technical_terms = {
        "SQL注入": "SQL注入是一种代码注入技术，攻击者通过在应用程序的输入字段中插入恶意SQL代码，来操纵后端数据库。这是OWASP Top 10中常见的Web应用安全漏洞。",
        "XSS": "跨站脚本攻击（XSS）是一种安全漏洞，攻击者可以在其他用户浏览的网页中注入恶意脚本。",
        "CSRF": "跨站请求伪造（CSRF）是一种攻击方式，攻击者诱导用户在已认证的Web应用上执行非预期的操作。",
        "DDoS": "分布式拒绝服务攻击（DDoS）通过大量请求使目标服务器过载，导致正常用户无法访问服务。",
        "RCE": "远程代码执行（RCE）漏洞允许攻击者在目标系统上执行任意代码。",
        "CVE": "通用漏洞披露（CVE）是公开披露的网络安全漏洞的唯一标识符。",
        "OWASP": "开放式Web应用程序安全项目（OWASP）是一个全球性的非营利组织，专注于改善软件安全。"
    }
    
    for term, explanation in technical_terms.items():
        if term in answer:
            answer = answer.replace(
                term,
                f"{term}（{explanation}）"
            )
    
    return answer