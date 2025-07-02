#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云端部署修复验证脚本
用于验证修复后的代码是否能正常运行
"""

import os
import sys
import json
import traceback
from datetime import datetime

def verify_environment_variables():
    """验证环境变量"""
    print("🔍 验证环境变量...")
    
    required_vars = [
        "NOTION_API_KEY",
        "NOTION_DATABASE_ID", 
        "OPENROUTER_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ 环境变量验证通过")
        return True

def verify_imports():
    """验证模块导入"""
    print("🔍 验证模块导入...")
    
    try:
        from notion_handler import NotionHandler
        from llm_handler import LLMHandler
        from template_manager import TemplateManager
        print("✅ 核心模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def verify_llm_handler():
    """验证LLM处理器"""
    print("🔍 验证LLM处理器...")
    
    try:
        from llm_handler import LLMHandler
        
        # 检查方法是否存在
        if not hasattr(LLMHandler, 'send_message'):
            print("❌ LLMHandler缺少send_message方法")
            return False
            
        if not hasattr(LLMHandler, 'generate_title'):
            print("❌ LLMHandler缺少generate_title方法")
            return False
            
        print("✅ LLMHandler方法验证通过")
        return True
        
    except Exception as e:
        print(f"❌ LLM处理器验证失败: {e}")
        return False

def verify_notion_handler():
    """验证Notion处理器"""
    print("🔍 验证Notion处理器...")
    
    try:
        from notion_handler import NotionHandler
        
        # 创建配置
        config = {
            "notion": {
                "api_key": os.getenv("NOTION_API_KEY", "test_key"),
                "database_id": os.getenv("NOTION_DATABASE_ID", "test_id"),
                "input_property_name": "输入",
                "output_property_name": "回复",
                "template_property_name": "模板选择",
                "knowledge_base_property_name": "背景",
                "model_property_name": "模型",
                "title_property_name": "标题"
            }
        }
        
        # 尝试初始化
        handler = NotionHandler(config)
        
        print("✅ NotionHandler初始化成功")
        return True
        
    except Exception as e:
        print(f"❌ Notion处理器验证失败: {e}")
        return False

def verify_cloud_main():
    """验证云端主程序"""
    print("🔍 验证云端主程序...")
    
    try:
        # 设置临时环境变量（如果未设置）
        if not os.getenv("NOTION_API_KEY"):
            os.environ["NOTION_API_KEY"] = "test_key"
        if not os.getenv("NOTION_DATABASE_ID"):
            os.environ["NOTION_DATABASE_ID"] = "test_id"
        if not os.getenv("OPENROUTER_API_KEY"):
            os.environ["OPENROUTER_API_KEY"] = "test_key"
            
        from cloud_hybrid_main import HybridCloudScheduler
        
        # 尝试初始化调度器
        scheduler = HybridCloudScheduler()
        
        print("✅ 云端主程序初始化成功")
        return True
        
    except Exception as e:
        print(f"❌ 云端主程序验证失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主验证函数"""
    print("🚀 开始部署修复验证...\n")
    
    tests = [
        ("环境变量", verify_environment_variables),
        ("模块导入", verify_imports), 
        ("LLM处理器", verify_llm_handler),
        ("Notion处理器", verify_notion_handler),
        ("云端主程序", verify_cloud_main)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}验证异常: {e}")
            results.append((test_name, False))
        print()
    
    # 汇总结果
    print("📊 验证结果汇总:")
    print("-" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print("-" * 50)
    print(f"总结: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n🎉 所有验证通过！云端部署修复成功！")
        print("\n📝 建议:")
        print("1. 确保在Zeabur中正确配置了所有环境变量")
        print("2. 重新部署应用")
        print("3. 检查部署日志确认没有错误")
        return True
    else:
        print(f"\n⚠️  有 {total - passed} 项验证失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 