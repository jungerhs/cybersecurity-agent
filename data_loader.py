import os
from pathlib import Path
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader
)
import config

class DocumentLoader:
    def __init__(self):
        self.chunk_size = config.DOCUMENT_CONFIG["chunk_size"]
        self.chunk_overlap = config.DOCUMENT_CONFIG["chunk_overlap"]
        self.supported_formats = config.DOCUMENT_CONFIG["supported_formats"]
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""]
        )

    def load_document(self, file_path: str) -> List[Document]:
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        if file_extension == ".pdf":
            loader = PyPDFLoader(str(file_path))
        elif file_extension == ".md":
            loader = UnstructuredMarkdownLoader(str(file_path))
        elif file_extension == ".txt":
            loader = TextLoader(str(file_path), encoding="utf-8")
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")
        
        documents = loader.load()
        
        for doc in documents:
            doc.metadata["source"] = str(file_path)
            doc.metadata["file_name"] = file_path.name
            doc.metadata["file_type"] = file_extension
        
        return documents

    def split_documents(self, documents: List[Document]) -> List[Document]:
        split_docs = self.text_splitter.split_documents(documents)
        
        for i, doc in enumerate(split_docs):
            doc.metadata["chunk_id"] = i
            doc.metadata["chunk_size"] = len(doc.page_content)
        
        return split_docs

    def load_documents_from_directory(self, directory: str) -> List[Document]:
        directory = Path(directory)
        
        if not directory.exists():
            raise FileNotFoundError(f"目录不存在: {directory}")
        
        all_documents = []
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                try:
                    documents = self.load_document(str(file_path))
                    all_documents.extend(documents)
                    print(f"成功加载文件: {file_path}")
                except Exception as e:
                    print(f"加载文件失败 {file_path}: {str(e)}")
        
        return all_documents

    def load_and_split(self, file_path: str = None, directory: str = None) -> List[Document]:
        if file_path:
            documents = self.load_document(file_path)
        elif directory:
            documents = self.load_documents_from_directory(directory)
        else:
            directory = config.DOCUMENT_CONFIG["documents_path"]
            documents = self.load_documents_from_directory(directory)
        
        if not documents:
            print("警告: 未找到任何文档")
            return []
        
        split_documents = self.split_documents(documents)
        print(f"文档分块完成: {len(documents)} 个原始文档 -> {len(split_documents)} 个文档块")
        
        return split_documents

    def get_document_stats(self, documents: List[Document]) -> Dict[str, Any]:
        if not documents:
            return {"total_documents": 0, "total_chunks": 0}
        
        total_chars = sum(len(doc.page_content) for doc in documents)
        avg_chunk_size = total_chars / len(documents)
        
        sources = {}
        for doc in documents:
            source = doc.metadata.get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1
        
        return {
            "total_documents": len(documents),
            "total_characters": total_chars,
            "average_chunk_size": avg_chunk_size,
            "sources": sources
        }
