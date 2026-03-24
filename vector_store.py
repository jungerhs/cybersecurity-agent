from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import config
import os

class VectorStore:
    def __init__(self):
        self.persist_directory = config.VECTOR_STORE_CONFIG["persist_directory"]
        self.collection_name = config.VECTOR_STORE_CONFIG["collection_name"]
        self.embedding_model = config.VECTOR_STORE_CONFIG["embedding_model"]
        self.top_k = config.RETRIEVAL_CONFIG["top_k"]
        self.score_threshold = config.RETRIEVAL_CONFIG["score_threshold"]
        
        self._ensure_directory_exists()
        
        self.embeddings = OpenAIEmbeddings(
            model=self.embedding_model,
            openai_api_key=config.OPENAI_API_KEY
        )
        
        self.vectorstore = None
        self.retriever = None

    def _ensure_directory_exists(self):
        os.makedirs(self.persist_directory, exist_ok=True)

    def create_vectorstore(self, documents: List[Document]) -> Chroma:
        if not documents:
            raise ValueError("文档列表为空，无法创建向量存储")
        
        print(f"正在创建向量存储，共 {len(documents)} 个文档块...")
        
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=self.collection_name,
            persist_directory=self.persist_directory
        )
        
        
        print(f"向量存储已创建并保存到: {self.persist_directory}")
        
        return self.vectorstore

    def get_retriever(self, search_type: str = "similarity", **kwargs) -> Any:
        if self.vectorstore is None:
            raise ValueError("向量存储未初始化。请先创建或加载向量存储。")
        
        search_kwargs = {
            "k": kwargs.get("k", self.top_k)
        }
        
        if search_type == "similarity_score_threshold":
            search_kwargs["score_threshold"] = kwargs.get(
                "score_threshold", 
                self.score_threshold
            )
        
        self.retriever = self.vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs=search_kwargs
        )
        
        return self.retriever

    def similarity_search(self, query: str, k: int = None, search_type: str = "similarity") -> List[Document]:
        if self.vectorstore is None:
            raise ValueError("向量存储未初始化。请先创建或加载向量存储。")
        
        k = k or self.top_k
        
        if search_type == "mmr":
            results = self.vectorstore.max_marginal_relevance_search(query, k=k)
        else:
            results = self.vectorstore.similarity_search(query, k=k)
        
        return results

    def similarity_search_with_score(self, query: str, k: int = None) -> List[tuple]:
        if self.vectorstore is None:
            raise ValueError("向量存储未初始化。请先创建或加载向量存储。")
        
        k = k or self.top_k
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        
        return results

    def add_documents(self, documents: List[Document]) -> None:
        if self.vectorstore is None:
            raise ValueError("向量存储未初始化。请先创建或加载向量存储。")
        
        print(f"正在添加 {len(documents)} 个新文档到向量存储...")
        
        self.vectorstore.add_documents(documents)
        self.vectorstore.persist()
        
        print("文档添加成功")

    def delete_collection(self) -> None:
        if self.vectorstore is None:
            print("向量存储未初始化，无需删除")
            return
        
        print(f"正在删除集合: {self.collection_name}")
        
        self.vectorstore.delete_collection()
        self.vectorstore = None
        self.retriever = None
        
        print("集合删除成功")

    def get_collection_stats(self) -> Dict[str, Any]:
        if self.vectorstore is None:
            return {"status": "未初始化", "document_count": 0}
        
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            
            return {
                "status": "已初始化",
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            return {
                "status": "错误",
                "error": str(e)
            }

    def reset_vectorstore(self) -> None:
        self.delete_collection()
        self._ensure_directory_exists()
        print("向量存储已重置")
