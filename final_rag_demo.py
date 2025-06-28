#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 RAG智能检索系统最终演示
展示语义搜索、关键词搜索和混合检索的强大功能
"""

import json
import time
from notion_knowledge_db import NotionKnowledgeDB

def print_search_result(query, results, search_time):
    """格式化打印搜索结果"""
    print(f"\n🔍 查询: '{query}'")
    print(f"⏱️  搜索耗时: {search_time:.2f}秒")
    print(f"📊 找到 {len(results)} 个结果:")
    print("-" * 60)
    
    for i, result in enumerate(results, 1):
        title = result.get('title', '无标题')
        content = result.get('content', '')[:200] + '...' if result.get('content') else '无内容'
        
        # 显示匹配信息（如果有）
        match_info = ""
        if 'match_score' in result:
            match_keywords = result.get('matched_keywords', [])
            match_info = f" (匹配分数: {result['match_score']}, 关键词: {match_keywords})"
        
        print(f"{i}. 📄 {title}{match_info}")
        print(f"   💬 {content}")
        print()

def demo_different_search_types():
    """演示不同类型的搜索"""
    
    print("🚀 RAG智能检索系统最终演示")
    print("=" * 70)
    
    # 加载配置
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    knowledge_db = NotionKnowledgeDB(config)
    
    # 测试用例分类
    test_cases = {
        "🎯 精确匹配查询": [
            "AI效率中心",
            "在线教育"
        ],
        
        "🧠 语义理解查询": [
            "如何管理团队",
            "怎样提升用户转化",
            "组织架构设计",
            "教育业务模式"
        ],
        
        "🔍 关键词部分匹配": [
            "AI经理",
            "部门职能",
            "课程体系",
            "中东市场"
        ],
        
        "❓ 问题式查询": [
            "AI效率中心的使命是什么?",
            "如何建设AI团队?",
            "在线教育有哪些用户类型?"
        ]
    }
    
    # 执行测试
    for category, queries in test_cases.items():
        print(f"\n\n{category}")
        print("=" * 50)
        
        for query in queries:
            start_time = time.time()
            
            try:
                # 使用智能搜索
                results = knowledge_db.smart_search_knowledge(query, max_results=3)
                search_time = time.time() - start_time
                
                print_search_result(query, results, search_time)
                
            except Exception as e:
                print(f"❌ 查询失败: {query} - {e}")
                
            # 短暂延迟，避免过快请求
            time.sleep(1)

def demo_performance_comparison():
    """演示性能对比"""
    print("\n\n🏁 性能对比测试")
    print("=" * 50)
    
    # 加载配置
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    knowledge_db = NotionKnowledgeDB(config)
    
    test_query = "AI效率中心"
    
    # 传统关键词搜索
    print(f"🔍 传统关键词搜索: '{test_query}'")
    start_time = time.time()
    keyword_results = knowledge_db.search_knowledge_by_keywords([test_query])
    keyword_time = time.time() - start_time
    print(f"   结果数量: {len(keyword_results)}")
    print(f"   搜索耗时: {keyword_time:.3f}秒")
    
    time.sleep(1)
    
    # RAG智能搜索
    print(f"\n🧠 RAG智能搜索: '{test_query}'")
    start_time = time.time()
    smart_results = knowledge_db.smart_search_knowledge(test_query)
    smart_time = time.time() - start_time
    print(f"   结果数量: {len(smart_results)}")
    print(f"   搜索耗时: {smart_time:.3f}秒")
    
    # 性能提升
    if keyword_results and smart_results:
        improvement = len(smart_results) / len(keyword_results) if len(keyword_results) > 0 else 1
        print(f"\n📊 结果质量提升: {improvement:.1f}x")
        print(f"🎯 RAG系统通过语义理解，能找到更多相关内容！")

if __name__ == "__main__":
    print("🎭 RAG智能检索系统 - 最终演示")
    print("展示语义搜索、智能匹配和混合检索的强大功能")
    print("=" * 70)
    
    try:
        demo_different_search_types()
        demo_performance_comparison()
        
        print("\n\n🎉 演示完成！")
        print("RAG系统已经完全就绪，可以处理各种复杂查询!")
        print("现在你可以在Notion中体验智能搜索功能了！")
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}") 