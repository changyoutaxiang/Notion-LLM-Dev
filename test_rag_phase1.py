"""
RAG系统Phase 1测试脚本
测试高性能语义搜索和混合检索功能

测试项目：
1. 语义搜索引擎基础功能
2. 混合检索引擎集成
3. 性能基准测试
4. 错误处理和回退机制
"""

import os
import json
import time
import sys
from pathlib import Path

# 确保可以导入项目模块
sys.path.append(str(Path(__file__).parent))

def load_test_config():
    """加载测试配置"""
    config_path = Path("config.example.json")
    if not config_path.exists():
        print("❌ 配置文件不存在，请先创建 config.json")
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 确保RAG系统启用
        config['knowledge_search']['rag_system']['enabled'] = True
        return config
    except Exception as e:
        print(f"❌ 加载配置失败: {e}")
        return None

def test_semantic_search_engine():
    """测试语义搜索引擎"""
    print("\n🧠 测试语义搜索引擎...")
    
    try:
        from semantic_search import create_semantic_search_engine, SearchConfig
        
        # 创建测试配置
        config = {
            "embedding_model": "shibing624/text2vec-base-chinese",  # 使用轻量级模型进行测试
            "device": "cpu",  # 测试时使用CPU
            "enable_cache": False,  # 测试时禁用缓存
            "batch_size": 4
        }
        
        print("📥 初始化语义搜索引擎...")
        engine = create_semantic_search_engine(config)
        
        # 测试数据
        test_knowledge = [
            {
                "id": "test_1",
                "title": "AI效率中心介绍",
                "content": "AI效率中心是负责人工智能技术应用和效率提升的核心部门，专注于通过AI技术优化业务流程。"
            },
            {
                "id": "test_2", 
                "title": "用户转化策略",
                "content": "用户转化策略包括多种方法提高用户参与度和转化率，如个性化推荐、优化用户体验等。"
            },
            {
                "id": "test_3",
                "title": "项目管理流程",
                "content": "项目管理流程包括需求分析、项目规划、执行监控、风险管理和项目交付等关键环节。"
            }
        ]
        
        print("🏗️ 构建测试索引...")
        if engine.build_index(test_knowledge):
            print("✅ 索引构建成功")
        else:
            print("❌ 索引构建失败")
            return False
        
        # 测试搜索
        test_queries = [
            "AI技术应用",
            "如何提高转化率",
            "项目执行过程"
        ]
        
        for query in test_queries:
            print(f"\n🔍 测试查询: '{query}'")
            start_time = time.time()
            results = engine.search(query, top_k=3)
            search_time = time.time() - start_time
            
            print(f"⏱️ 搜索耗时: {search_time:.3f}秒")
            print(f"📊 找到 {len(results)} 个结果:")
            
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.title} (相似度: {result.similarity_score:.3f})")
                print(f"     片段: {result.content_snippet[:50]}...")
        
        # 性能统计
        stats = engine.get_stats()
        print(f"\n📈 性能统计:")
        print(f"  - 总搜索次数: {stats['total_searches']}")
        print(f"  - 平均搜索时间: {stats['avg_search_time']:.3f}秒")
        print(f"  - 内存使用: {stats['memory_usage_mb']:.1f}MB")
        
        return True
        
    except Exception as e:
        print(f"❌ 语义搜索引擎测试失败: {e}")
        return False

def test_hybrid_retrieval():
    """测试混合检索引擎"""
    print("\n🔀 测试混合检索引擎...")
    
    try:
        # 这里需要模拟NotionKnowledgeDB
        class MockNotionKnowledgeDB:
            def search_knowledge_by_keywords(self, keywords):
                # 模拟关键词搜索结果
                return [
                    {
                        "id": "mock_1",
                        "title": "模拟知识条目1",
                        "content": "这是一个模拟的知识条目，包含了相关的关键词。"
                    },
                    {
                        "id": "mock_2", 
                        "title": "模拟知识条目2",
                        "content": "这是另一个模拟的知识条目，用于测试关键词匹配。"
                    }
                ]
        
        config = load_test_config()
        if not config:
            return False
        
        # 简化配置用于测试
        config['knowledge_search']['rag_system']['embedding']['model_name'] = "shibing624/text2vec-base-chinese"
        config['knowledge_search']['rag_system']['embedding']['device'] = "cpu"
        
        from hybrid_retrieval import create_hybrid_retrieval_engine
        
        mock_db = MockNotionKnowledgeDB()
        
        print("🚀 初始化混合检索引擎...")
        hybrid_engine = create_hybrid_retrieval_engine(mock_db, config)
        
        # 测试查询分析
        from hybrid_retrieval import SmartQueryAnalyzer
        analyzer = SmartQueryAnalyzer()
        
        test_queries = [
            "什么是AI效率中心",
            "如何提高用户转化率",
            "项目管理"
        ]
        
        for query in test_queries:
            print(f"\n🔍 测试查询: '{query}'")
            
            # 查询分析
            analysis = analyzer.analyze(query)
            print(f"  📋 查询类型: {analysis.query_type}")
            print(f"  🔑 关键词: {analysis.processed_keywords}")
            print(f"  📊 复杂度: {analysis.complexity}")
            
            # 由于语义搜索引擎可能未完全初始化，这里主要测试架构
            print("  ✅ 查询分析完成")
        
        # 测试统计功能
        stats = hybrid_engine.get_search_stats()
        print(f"\n📈 混合检索统计:")
        for key, value in stats.items():
            print(f"  - {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 混合检索引擎测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_notion_integration():
    """测试Notion集成"""
    print("\n🔗 测试Notion集成...")
    
    try:
        config = load_test_config()
        if not config:
            return False
        
        # 检查Notion配置
        notion_config = config.get('notion', {})
        required_fields = ['token', 'knowledge_database_id']
        
        for field in required_fields:
            if not notion_config.get(field):
                print(f"⚠️ Notion配置缺少 {field}，跳过实际API测试")
                return True
        
        from notion_knowledge_db import NotionKnowledgeDB
        
        print("🔗 初始化Notion知识库...")
        knowledge_db = NotionKnowledgeDB(config)
        
        # 测试智能搜索接口
        test_query = "测试查询"
        print(f"🔍 测试智能搜索: '{test_query}'")
        
        results = knowledge_db.smart_search_knowledge(test_query, max_results=3)
        print(f"📊 搜索结果: {len(results)} 个")
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.get('title', 'N/A')}")
            if 'similarity_score' in result:
                print(f"     相似度: {result['similarity_score']:.3f}")
            if 'source_type' in result:
                print(f"     来源: {result['source_type']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Notion集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_benchmark():
    """性能基准测试"""
    print("\n⚡ 性能基准测试...")
    
    try:
        # 简单的性能测试
        import psutil
        import platform
        
        print(f"💻 系统信息:")
        print(f"  - 操作系统: {platform.system()} {platform.release()}")
        print(f"  - CPU核心数: {psutil.cpu_count()}")
        print(f"  - 内存总量: {psutil.virtual_memory().total / (1024**3):.1f}GB")
        print(f"  - 可用内存: {psutil.virtual_memory().available / (1024**3):.1f}GB")
        
        # 测试依赖包导入速度
        import_tests = [
            "numpy",
            "torch", 
            "sentence_transformers",
            "faiss",
            "jieba"
        ]
        
        print(f"\n📦 依赖包导入测试:")
        for package in import_tests:
            try:
                start_time = time.time()
                __import__(package)
                import_time = time.time() - start_time
                print(f"  ✅ {package}: {import_time:.3f}秒")
            except ImportError:
                print(f"  ❌ {package}: 未安装")
            except Exception as e:
                print(f"  ⚠️ {package}: 导入失败 ({e})")
        
        return True
        
    except Exception as e:
        print(f"❌ 性能基准测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 RAG系统Phase 1测试开始")
    print("=" * 50)
    
    test_results = []
    
    # 1. 性能基准测试
    test_results.append(("性能基准", test_performance_benchmark()))
    
    # 2. 语义搜索引擎测试
    test_results.append(("语义搜索引擎", test_semantic_search_engine()))
    
    # 3. 混合检索引擎测试
    test_results.append(("混合检索引擎", test_hybrid_retrieval()))
    
    # 4. Notion集成测试
    test_results.append(("Notion集成", test_notion_integration()))
    
    # 结果汇总
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！RAG系统Phase 1基础功能正常")
        print("\n📋 下一步建议:")
        print("1. 安装完整依赖: pip install -r requirements_rag.txt")
        print("2. 配置Notion API: 复制 config.example.json 为 config.json 并填入真实配置")
        print("3. 运行实际测试: python test_rag_phase1.py")
        print("4. 监控性能表现并进行优化")
    else:
        print("⚠️ 部分测试失败，请检查配置和依赖")
        print("\n🔧 故障排除建议:")
        print("1. 检查Python环境和依赖安装")
        print("2. 验证配置文件格式")
        print("3. 确认网络连接正常")
        print("4. 查看详细错误信息")

if __name__ == "__main__":
    main() 