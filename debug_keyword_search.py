#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试关键词搜索功能
专门测试 search_knowledge_by_keywords 方法
"""

import json
from notion_knowledge_db import NotionKnowledgeDB
import jieba

def test_keyword_extraction():
    """测试关键词提取"""
    print("🔍 测试关键词提取")
    print("=" * 30)
    
    test_queries = [
        "AI效率中心",
        "部门职能", 
        "团队建设",
        "用户转化"
    ]
    
    for query in test_queries:
        # 使用jieba分词
        words = list(jieba.cut(query))
        
        # 过滤停用词
        stop_words = {'的', '是', '在', '有', '和', '与', '及', '或', '也', '了', '就', '都', '要', '能', '会'}
        keywords = [word.strip() for word in words 
                   if len(word.strip()) > 1 and word.strip() not in stop_words]
        
        print(f"查询: '{query}' → 关键词: {keywords}")

def test_keyword_search():
    """测试关键词搜索"""
    print("\n🔍 测试关键词搜索")
    print("=" * 30)
    
    # 加载配置
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    knowledge_db = NotionKnowledgeDB(config)
    
    # 测试不同的关键词组合
    test_cases = [
        ["AI效率中心"],
        ["AI", "效率"],
        ["部门"],
        ["团队"],
        ["用户"],
        ["转化"],
        ["建设"],
        ["职能"],
        ["在线教育"],
        ["业务"]
    ]
    
    for keywords in test_cases:
        print(f"\n🔍 搜索关键词: {keywords}")
        
        try:
            results = knowledge_db.search_knowledge_by_keywords(keywords)
            print(f"   结果数量: {len(results)}")
            
            if results:
                for i, result in enumerate(results[:2], 1):  # 只显示前2个
                    title = result.get('title', '无标题')
                    content_preview = result.get('content', '')[:100] + '...' if result.get('content') else '无内容'
                    print(f"   {i}. {title}")
                    print(f"      {content_preview}")
            else:
                print("   ❌ 无结果")
                
        except Exception as e:
            print(f"   ❌ 搜索失败: {e}")

def test_get_all_knowledge():
    """测试获取所有知识条目"""
    print("\n📚 测试获取所有知识条目")
    print("=" * 30)
    
    # 加载配置
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    knowledge_db = NotionKnowledgeDB(config)
    
    try:
        all_items = knowledge_db.get_all_knowledge_items()
        print(f"📊 总知识条目数: {len(all_items)}")
        
        for i, item in enumerate(all_items, 1):
            title = item.get('title', '无标题')
            keywords = item.get('keywords', [])
            print(f"  {i}. {title}")
            print(f"     关键词: {keywords}")
            print(f"     ID: {item.get('id', 'N/A')}")
            
    except Exception as e:
        print(f"❌ 获取失败: {e}")

if __name__ == "__main__":
    print("🔧 关键词搜索调试工具")
    print("=" * 50)
    
    test_keyword_extraction()
    test_get_all_knowledge()
    test_keyword_search() 