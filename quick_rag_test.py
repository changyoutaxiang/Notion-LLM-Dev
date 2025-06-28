#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 快速RAG测试脚本
验证智能搜索功能是否正常工作
"""

import json
import time
from notion_knowledge_db import NotionKnowledgeDB

def main():
    print("🧠 快速RAG智能搜索测试")
    print("=" * 40)
    
    try:
        # 加载配置
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ 配置加载成功")
        
        # 初始化知识库
        print("🔗 连接知识库...")
        knowledge_db = NotionKnowledgeDB(config)
        print("✅ 知识库连接成功")
        
        # 测试查询列表
        test_queries = [
            "AI效率中心",
            "部门职能", 
            "团队建设",
            "用户转化"
        ]
        
        print(f"\n🔍 开始测试 {len(test_queries)} 个查询...\n")
        
        for i, query in enumerate(test_queries, 1):
            print(f"🔍 测试 {i}: '{query}'")
            
            start_time = time.time()
            
            # 测试传统关键词搜索
            try:
                keyword_results = knowledge_db.search_knowledge_by_keywords([query])
                keyword_count = len(keyword_results) if keyword_results else 0
            except Exception as e:
                keyword_count = 0
                print(f"  ⚠️ 关键词搜索出错: {e}")
            
            # 测试新的智能搜索
            try:
                smart_results = knowledge_db.smart_search_knowledge(query, max_results=3)
                smart_count = len(smart_results) if smart_results else 0
            except Exception as e:
                smart_count = 0
                print(f"  ⚠️ 智能搜索出错: {e}")
            
            search_time = (time.time() - start_time) * 1000
            
            print(f"  📊 关键词搜索: {keyword_count} 个结果")
            print(f"  🧠 智能搜索: {smart_count} 个结果")
            print(f"  ⏱️ 搜索耗时: {search_time:.1f}ms")
            
            # 显示智能搜索结果
            if smart_count > 0:
                print(f"  📝 智能搜索结果:")
                for j, result in enumerate(smart_results[:2], 1):
                    snippet = result.get('content_snippet', result.get('snippet', ''))[:100]
                    if snippet:
                        snippet = snippet.replace('\n', ' ')
                        print(f"    {j}. {snippet}...")
            
            print()
        
        print("🎉 RAG测试完成！")
        
        # 系统状态检查
        print("\n📊 系统状态:")
        rag_enabled = config.get('knowledge_search', {}).get('rag_system', {}).get('enabled', False)
        print(f"   RAG系统: {'✅ 启用' if rag_enabled else '❌ 未启用'}")
        
        embedding_model = config.get('knowledge_search', {}).get('rag_system', {}).get('embedding', {}).get('model_name', 'N/A')
        print(f"   嵌入模型: {embedding_model}")
        
        search_mode = config.get('knowledge_search', {}).get('rag_system', {}).get('mode', 'keyword')
        print(f"   搜索模式: {search_mode}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 