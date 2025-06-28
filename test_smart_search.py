#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG智能搜索功能测试
测试语义搜索和混合检索的实际效果
"""

import json
import time
from notion_knowledge_db import NotionKnowledgeDB

def load_config():
    """加载配置"""
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def test_smart_search():
    """测试智能搜索功能"""
    
    print("🧠 RAG智能搜索功能测试")
    print("=" * 50)
    
    # 加载配置
    config = load_config()
    
    # 初始化NotionKnowledgeDB
    knowledge_db = NotionKnowledgeDB(config)
    
    # 测试查询
    test_queries = [
        "AI效率中心是什么",
        "如何培养AI人才",
        "组织架构设计",
        "业务增长策略",
        "AIBP团队",
        "智能化转型",
        "人才培养方案",
        "转介绍机制"
    ]
    
    print(f"📊 开始测试 {len(test_queries)} 个查询...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"🔍 查询 {i}: '{query}'")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            # 测试新的智能搜索接口
            if hasattr(knowledge_db, 'smart_search_knowledge'):
                results = knowledge_db.smart_search_knowledge(query, max_results=3)
                search_type = "智能搜索"
            else:
                # 回退到关键词搜索
                results = knowledge_db.search_knowledge_by_keywords([query])
                search_type = "关键词搜索"
            
            search_time = time.time() - start_time
            
            print(f"⚡ 搜索方式: {search_type}")
            print(f"⏱️ 搜索时间: {search_time:.3f}秒")
            print(f"📋 结果数量: {len(results)}")
            
            if results:
                for j, result in enumerate(results[:2], 1):  # 只显示前2个结果
                    if isinstance(result, dict):
                        title = result.get('title', 'N/A')
                        # 尝试获取片段或内容
                        snippet = result.get('snippet', result.get('content', ''))[:150]
                        similarity = result.get('similarity_score', 'N/A')
                        
                        print(f"  📌 结果{j}: {title}")
                        if similarity != 'N/A':
                            print(f"    📊 相似度: {similarity:.3f}")
                        print(f"    📝 片段: {snippet}...")
                    else:
                        print(f"  📌 结果{j}: {str(result)[:100]}...")
            else:
                print("  ❌ 未找到相关结果")
                
        except Exception as e:
            print(f"  ❌ 搜索出错: {e}")
        
        print()
    
    print("🎉 测试完成！")

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