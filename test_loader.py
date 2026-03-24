import os
from pathlib import Path
from data_loader import DocumentLoader

def test_document_loader():
    print("=" * 60)
    print("文档加载器测试")
    print("=" * 60)
    
    loader = DocumentLoader()
    
    documents_dir = "documents"
    
    if not os.path.exists(documents_dir):
        print(f"错误: 文档目录不存在: {documents_dir}")
        return
    
    print(f"\n文档目录: {os.path.abspath(documents_dir)}")
    print(f"支持的格式: {loader.supported_formats}")
    
    print("\n" + "-" * 60)
    print("扫描文档文件...")
    print("-" * 60)
    
    files_found = []
    for file_path in Path(documents_dir).rglob("*"):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext in loader.supported_formats:
                files_found.append(str(file_path))
                print(f"  ✓ {file_path}")
    
    print(f"\n找到 {len(files_found)} 个支持的文件")
    
    if not files_found:
        print("\n警告: 没有找到支持的文档文件")
        return
    
    print("\n" + "-" * 60)
    print("逐个测试文件加载...")
    print("-" * 60)
    
    all_documents = []
    
    for file_path in files_found:
        
            print(f"\n测试文件: {file_path}")
            documents = loader.load_document(file_path)
            print(f"  ✓ 成功加载 {len(documents)} 个文档")
            
            for i, doc in enumerate(documents):
                print(f"    - 文档 {i+1}: {len(doc.page_content)} 字符")
                print(f"      元数据: {doc.metadata}")
            
            all_documents.extend(documents)
            
        
    
    print("\n" + "-" * 60)
    print("测试分块...")
    print("-" * 60)
    
    if all_documents:
        split_docs = loader.split_documents(all_documents)
        print(f"分块完成: {len(all_documents)} 个原始文档 -> {len(split_docs)} 个文档块")
        
        print("\n前3个文档块示例:")
        for i, doc in enumerate(split_docs[:3]):
            print(f"\n  文档块 {i+1}:")
            print(f"    内容预览: {doc.page_content[:100]}...")
            print(f"    元数据: {doc.metadata}")
        
        print("\n" + "=" * 60)
        print("测试完成!")
        print("=" * 60)
        print(f"\n统计:")
        print(f"  - 原始文档数: {len(all_documents)}")
        print(f"  - 文档块数: {len(split_docs)}")
        print(f"  - 总字符数: {sum(len(doc.page_content) for doc in all_documents)}")
    else:
        print("\n没有成功加载的文档")

if __name__ == "__main__":
    test_document_loader()
