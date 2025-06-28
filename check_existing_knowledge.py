#!/usr/bin/env python3

"""
检查现有知识条目的详细内容
"""

import json
from notion_knowledge_db import NotionKnowledgeDB

def main():
    print("🔍 检查现有知识条目")
    print("=" * 40)
    
    # 加载配置
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    knowledge_db = NotionKnowledgeDB(config)
    
    # 测试不同的关键词搜索
    test_keywords = [
        ["AI效率中心"],
        ["部门职能"],
        ["团队建设"],
        ["业务理解"],
        ["在线教育"],
        ["用户转化"]
    ]
    
    for keywords in test_keywords:
        print(f"\n🔍 搜索关键词: {keywords}")
        print("-" * 30)
        
        try:
            results = knowledge_db.search_knowledge_by_keywords(keywords)
            
            if results:
                print(f"✅ 找到 {len(results)} 个结果:")
                
                for i, result in enumerate(results, 1):
                    print(f"\n📄 结果 {i}:")
                    print(f"   标题: {result.get('title', 'N/A')}")
                    print(f"   分类: {result.get('category', 'N/A')}")
                    print(f"   子类: {result.get('subcategory', 'N/A')}")
                    print(f"   关键词: {result.get('keywords', [])}")
                    
                    # 显示内容片段
                    content = result.get('content', '')
                    if content:
                        snippet = content[:200] + "..." if len(content) > 200 else content
                        print(f"   内容片段: {snippet}")
            else:
                print("❌ 未找到结果")
                
        except Exception as e:
            print(f"❌ 搜索出错: {e}")

if __name__ == "__main__":
    main() 