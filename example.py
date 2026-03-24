from qa_system import CyberSecurityQASystem

def main():
    print("=" * 60)
    print("网络安全知识问答助手 - 使用示例")
    print("=" * 60)
    
    # 创建系统实例
    qa_system = CyberSecurityQASystem()
    
    # 初始化系统
    print("\n[1/3] 正在初始化系统...")
    try:
        qa_system.initialize(force_rebuild=False)
        print("✓ 系统初始化成功")
    except Exception as e:
        print(f"✗ 初始化失败: {str(e)}")
        return
    
    # 示例查询列表
    example_queries = [
        "什么是SQL注入？请解释其原理和防御措施。",
        "OWASP Top 10中包含哪些安全风险？",
        "解释NIST网络安全框架的五个核心功能。",
        "XSS漏洞有哪些类型？如何防御？",
        "什么是CSRF攻击？如何防止？"
    ]
    
    print("\n[2/3] 执行示例查询...")
    print("=" * 60)
    
    for i, query in enumerate(example_queries, 1):
        print(f"\n【示例 {i}】")
        print(f"问题: {query}")
        print("-" * 60)
        
        result = qa_system.query(query)
        
        if result['success']:
            print(f"✓ 查询成功")
        else:
            print(f"✗ 查询失败: {result['error']}")
    
    print("\n[3/3] 获取系统状态...")
    print("=" * 60)
    
    status = qa_system.get_system_status()
    print(f"\n系统状态:")
    print(f"  - 初始化状态: {'已初始化' if status['is_initialized'] else '未初始化'}")
    print(f"  - 文档数量: {status['vector_store'].get('document_count', 0)}")
    print(f"  - 可用工具数: {len(status['tools'])}")
    print(f"\n可用工具:")
    for tool in status['tools']:
        print(f"  - {tool['name']}: {tool['description']}")
    
    print("\n" + "=" * 60)
    print("示例执行完成！")
    print("=" * 60)
    
    # 交互式模式
    print("\n进入交互式模式（输入 'quit' 退出）...")
    print("=" * 60)
    
    while True:
        try:
            question = input("\n您的问题: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', '退出']:
                print("感谢使用，再见！")
                break
            
            result = qa_system.query(question)
            
            if not result['success']:
                print(f"\n错误: {result['error']}")
        
        except KeyboardInterrupt:
            print("\n\n感谢使用，再见！")
            break
        except Exception as e:
            print(f"\n发生错误: {str(e)}")

if __name__ == "__main__":
    main()