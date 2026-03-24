import os
from typing import Dict, List, Optional, Any
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from data_loader import DocumentLoader
from vector_store import VectorStore
from agent_config import (
    AgentConfig, 
    mask_sensitive_info, 
    format_answer_with_sources,
    explain_technical_terms
)
import config

class CyberSecurityQASystem:
    def __init__(self):
        self.document_loader = DocumentLoader()
        self.vector_store = VectorStore()
        self.agent_config = None
        self.chunks = []
        self.llm = ChatOpenAI(
            model=config.MODEL_CONFIG["llm_model"],
            temperature=config.MODEL_CONFIG["temperature"],
            max_tokens=config.MODEL_CONFIG["max_tokens"],
            openai_api_key=config.OPENAI_API_KEY
        )
        self.is_initialized = False

    def initialize(self, force_rebuild: bool = False) -> None:
        print("=" * 60)
        print("正在初始化网络安全知识问答系统...")
        print("=" * 60)
        
        try:
            print("\n[步骤 1/4] 加载文档...")
            self._load_documents()
            
            print("\n[步骤 2/4] 创建向量存储...")
            self._create_vectorstore()
            
            print("\n[步骤 3/4] 初始化Agent...")
            self._initialize_agent()
            
            print("\n[步骤 4/4] 系统初始化完成!")
            print("=" * 60)
            
            self.is_initialized = True
            self._print_system_info()
        
        except Exception as e:
            print(f"\n初始化失败: {str(e)}")
            raise

    def _load_documents(self) -> None:
        documents_path = config.DOCUMENT_CONFIG["documents_path"]
        
        if not os.path.exists(documents_path):
            print(f"警告: 文档目录不存在: {documents_path}")
            print("警告: 将创建空文档目录...")
            os.makedirs(documents_path, exist_ok=True)
            return
        
        documents = self.document_loader.load_and_split(directory=documents_path)
        
        if not documents:
            print("警告: 未找到任何文档")
            return
        self.chunks = documents
        stats = self.document_loader.get_document_stats(documents)
        print(f"文档统计:")
        print(f"  - 总文档块数: {stats['total_documents']}")
        print(f"  - 总字符数: {stats['total_characters']}")
        print(f"  - 平均块大小: {stats['average_chunk_size']:.2f}")
        print(f"  - 来源文件数: {len(stats['sources'])}")

    def _create_vectorstore(self) -> None:
        
        
        chunks = self.chunks
        if not self.chunks:
            print("警告: 没有分割后的chunks可用于创建向量存储")
            return
        
        self.vector_store.create_vectorstore(chunks)
        
        stats = self.vector_store.get_collection_stats()
        print(f"向量存储统计:")
        print(f"  - 文档数量: {stats['document_count']}")
        print(f"  - 存储位置: {stats['persist_directory']}")



    def _initialize_agent(self) -> None:
        retriever = self.vector_store.get_retriever()
        config.set_retriever(retriever)
        self.agent_config = AgentConfig(retriever=retriever, llm=self.llm)
        self.agent_config.create_agent()
        
        tools_info = self.agent_config.get_tools_info()
        print(f"Agent工具:")
        for tool_info in tools_info:
            print(f"  - {tool_info['name']}: {tool_info['description']}")

    def _print_system_info(self) -> None:
        print("\n系统信息:")
        print(f"  - LLM模型: {config.MODEL_CONFIG['llm_model']}")
        print(f"  - Embedding模型: {config.MODEL_CONFIG['embedding_model']}")
        print(f"  - 向量存储: ChromaDB")
        print(f"  - Agent类型: ReAct Agent")
        print(f"  - 支持的文档格式: {', '.join(config.DOCUMENT_CONFIG['supported_formats'])}")

    def query(self, question: str, include_sources: bool = True, use_web_search: bool = True) -> Dict[str, Any]:
        if not self.is_initialized:
            return {
                "success": False,
                "error": "系统未初始化，请先调用 initialize() 方法",
                "answer": None
            }
        
        if not question or not question.strip():
            return {
                "success": False,
                "error": "问题不能为空",
                "answer": None
            }
        
        print(f"\n{'=' * 60}")
        print(f"用户问题: {question}")
        print(f"{'=' * 60}")
        
        try:
            answer = self.agent_config.run_agent(question, use_web_search=use_web_search)
            
            if not answer:
                return {
                    "success": False,
                    "error": "未能生成答案",
                    "answer": None
                }
            
            answer = explain_technical_terms(answer)
            answer = mask_sensitive_info(answer)
            
            if include_sources:
                sources = self.vector_store.similarity_search(question, k=3)
                answer = format_answer_with_sources(answer, sources)
            
            print(f"\n回答:\n{answer}")
            print(f"{'=' * 60}\n")
            
            return {
                "success": True,
                "error": None,
                "answer": answer
            }
        
        except Exception as e:
            error_msg = f"查询处理失败: {str(e)}"
            print(f"\n错误: {error_msg}")
            print(f"{'=' * 60}\n")
            
            return {
                "success": False,
                "error": error_msg,
                "answer": None
            }

    def add_documents(self, file_path: str = None, directory: str = None) -> Dict[str, Any]:
        try:
            print(f"\n正在添加文档...")
            
            documents = self.document_loader.load_and_split(
                file_path=file_path,
                directory=directory
            )
            
            if not documents:
                return {
                    "success": False,
                    "error": "未找到任何文档",
                    "added_count": 0
                }
            
            self.vector_store.add_documents(documents)
            
            retriever = self.vector_store.get_retriever()
            self.agent_config.update_retriever(retriever)
            
            print(f"成功添加 {len(documents)} 个文档块")
            
            return {
                "success": True,
                "error": None,
                "added_count": len(documents)
            }
        
        except Exception as e:
            error_msg = f"添加文档失败: {str(e)}"
            print(f"错误: {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "added_count": 0
            }

    def get_status(self) -> Dict[str, Any]:
        status = {
            "is_initialized": self.is_initialized,
            "vector_store": self.vector_store.get_collection_stats(),
            "tools": self.agent_config.get_tools_info() if self.agent_config else []
        }
        return status

    def get_system_status(self) -> Dict[str, Any]:
        return self.get_status()

    def reset_system(self) -> None:        
        print("\n正在重置系统...")
        self.vector_store.reset_vectorstore()
        self.agent_config = None
        self.is_initialized = False
        print("系统已重置")

def main():    
    qa_system = CyberSecurityQASystem()
    
    print("网络安全知识问答助手")
    print("=" * 60)
    
    try:
        qa_system.initialize(force_rebuild=False)
    except Exception as e:
        print(f"初始化失败: {str(e)}")
        print("\n提示: 请确保:")
        print("1. 已设置 OPENAI_API_KEY 环境变量")
        print("2. 已安装所有依赖包 (pip install -r requirements.txt)")
        print("3. 文档目录存在且包含支持的文档文件")
        return
    
    print("\n系统已就绪! 输入您的问题，或输入 'quit' 退出。\n")
    
    while True:
        try:
            question = input("您的问题: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', '退出']:
                print("感谢使用网络安全知识问答助手，再见!")
                break
            
            if question.lower() in ['status', '状态']:
                status = qa_system.get_system_status()
                print(f"\n系统状态:")
                print(f"  - 初始化状态: {'已初始化' if status['is_initialized'] else '未初始化'}")
                print(f"  - 文档数量: {status['vector_store'].get('document_count', 0)}")
                print(f"  - 可用工具: {len(status['tools'])}")
                continue
            
            result = qa_system.query(question)
            
            if not result['success']:
                print(f"\n抱歉，处理您的问题时遇到错误:")
                print(f"{result['error']}")
        
        except KeyboardInterrupt:
            print("\n\n感谢使用网络安全知识问答助手，再见!")
            break
        except Exception as e:
            print(f"\n发生错误: {str(e)}")

if __name__ == "__main__":
    main()

