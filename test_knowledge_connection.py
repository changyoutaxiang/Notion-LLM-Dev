#!/usr/bin/env python3
"""
知识库连接测试脚本
用于验证Notion知识库配置是否正确
"""

import json
import sys
from notion_knowledge_db import NotionKnowledgeDB

def test_knowledge_database():
    """测试知识库数据库连接"""
    print("🧪 Notion知识库连接测试")
    print("=" * 40)
    
    # 加载配置
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ 配置文件 config.json 不存在")
        print("💡 请先复制 config.example.json 为 config.json 并填入正确的API密钥")
        return False
    except json.JSONDecodeError:
        print("❌ 配置文件格式错误")
        return False
    
    # 创建知识库实例
    try:
        kb = NotionKnowledgeDB(config)
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False
    
    # 测试基础连接
    print("🔍 测试基础Notion连接...")
    success, msg = kb.test_connection()
    if not success:
        print(f"❌ {msg}")
        return False
    print(f"✅ {msg}")
    
    # 测试知识库连接
    print("\n🔍 测试知识库数据库连接...")
    success, msg = kb.test_knowledge_database_connection()
    if not success:
        print(f"❌ {msg}")
        print("\n💡 解决建议：")
        print("   1. 检查知识库数据库ID是否正确")
        print("   2. 确认数据库已创建并且有正确的权限")
        print("   3. 验证数据库字段名称配置")
        return False
    print(f"✅ {msg}")
    
    # 测试基础查询功能
    print("\n🔍 测试知识库查询功能...")
    try:
        # 尝试搜索一个不存在的关键词，看是否返回空结果
        results = kb.search_knowledge_by_keywords(["测试关键词"])
        print(f"✅ 查询功能正常，返回 {len(results)} 个结果")
    except Exception as e:
        print(f"❌ 查询功能测试失败: {e}")
        return False
    
    print("\n🎉 所有测试通过！知识库连接配置正确")
    return True

def show_config_info():
    """显示当前配置信息"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        notion_config = config.get('notion', {})
        print("\n📋 当前知识库配置：")
        print(f"   知识库数据库ID: {notion_config.get('knowledge_database_id', '未配置')}")
        print(f"   分类数据库ID: {notion_config.get('category_database_id', '未配置')}")
        print(f"   知识搜索启用: {config.get('knowledge_search', {}).get('enable_new_system', False)}")
        
    except Exception as e:
        print(f"❌ 读取配置失败: {e}")

if __name__ == "__main__":
    # 显示配置信息
    show_config_info()
    
    # 执行测试
    success = test_knowledge_database()
    
    if success:
        print("\n🚀 下一步操作建议：")
        print("   1. 运行 python migrate_knowledge_to_notion.py 开始迁移现有知识")
        print("   2. 在Notion中检查迁移的知识条目")
        print("   3. 完善知识条目的分类和关键词")
        print("   4. 测试智能检索功能")
    else:
        print("\n🔧 请修复配置问题后重新测试")
        sys.exit(1) 