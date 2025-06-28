#!/usr/bin/env python3
"""
智能知识检索测试脚本
"""

import json
from notion_knowledge_db import NotionKnowledgeDB

def test_smart_search():
    """测试智能知识检索功能"""
    print("🧠 智能知识检索测试")
    print("=" * 40)
    
    # 加载配置
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return
    
    # 创建知识库实例
    kb = NotionKnowledgeDB(config)
    
    # 测试用例
    test_queries = [
        "AI效率中心的部门职能是什么？",
        "介绍一下组织架构",
        "业务流程是怎样的？",
        "用户转化相关的信息",
        "AI经理培养相关内容"
    ]
    
    print("🔍 开始测试智能检索...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 测试 {i}: {query}")
        print("-" * 30)
        
        # 测试关键词搜索
        try:
            # 简单关键词提取（实际应该用更智能的方法）
            keywords = []
            if "AI效率中心" in query:
                keywords.append("AI效率中心")
            if "部门" in query or "组织" in query:
                keywords.append("部门职能")
                keywords.append("组织架构")
            if "业务" in query:
                keywords.append("业务理解")
            if "用户" in query:
                keywords.append("用户转化")
            if "AI经理" in query:
                keywords.append("AI经理培养")
            
            if keywords:
                print(f"🔑 提取关键词: {keywords}")
                results = kb.search_knowledge_by_keywords(keywords)
                
                if results:
                    print(f"✅ 找到 {len(results)} 个相关知识条目:")
                    for result in results:
                        print(f"   📄 {result['title']}")
                        print(f"   🏷️  分类: {result['category']}")
                        print(f"   🔗 关键词: {', '.join(result['keywords'])}")
                        print()
                else:
                    print("❌ 未找到相关知识")
            else:
                print("⚠️  未提取到关键词")
                
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
    
    print("\n🎉 测试完成！")

def test_category_search():
    """测试分类搜索"""
    print("\n📂 分类搜索测试")
    print("=" * 40)
    
    # 加载配置
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return
    
    kb = NotionKnowledgeDB(config)
    
    # 测试不同分类
    categories = ["AI效率中心", "51Talk业务背景", "AI训战营"]
    
    for category in categories:
        print(f"\n🔍 搜索分类: {category}")
        print("-" * 20)
        
        try:
            results = kb.get_knowledge_by_category(category)
            
            if results:
                print(f"✅ 找到 {len(results)} 个知识条目:")
                for result in results:
                    print(f"   📄 {result['title']}")
                    print(f"   🔗 关键词: {', '.join(result['keywords'])}")
            else:
                print("❌ 该分类下暂无知识条目")
                
        except Exception as e:
            print(f"❌ 搜索失败: {e}")

if __name__ == "__main__":
    test_smart_search()
    test_category_search() 