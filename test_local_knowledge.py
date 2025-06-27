#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试本地版本的背景文件加载功能
"""

from notion_handler import NotionHandler

def test_local_knowledge_loading():
    """测试本地版本的背景文件加载"""
    print("=" * 60)
    print("🧪 测试本地版本背景文件加载功能")
    print("=" * 60)
    
    # 模拟配置（只需要基本的配置，不需要真实的API密钥）
    config = {
        "notion": {
            "api_key": "dummy_key",
            "database_id": "dummy_id",
            "input_property_name": "输入",
            "output_property_name": "回复",
            "template_property_name": "模板选择",
            "knowledge_base_property_name": "背景",
            "model_property_name": "模型",
            "title_property_name": "标题",
        }
    }
    
    # 创建NotionHandler实例
    try:
        handler = NotionHandler(config)
        print("✅ NotionHandler初始化成功")
    except Exception as e:
        print(f"❌ NotionHandler初始化失败: {e}")
        return
    
    # 测试不同的标签组合
    test_cases = [
        (["AI效率中心"], "单个标签: AI效率中心"),
        (["业务理解"], "单个标签: 业务理解"),
        (["AI效率中心", "业务理解"], "多个标签: AI效率中心 + 业务理解"),
        (["无"], "特殊标签: 无"),
        ([], "空标签列表"),
        (["不存在的标签"], "不存在的标签")
    ]
    
    for tags, description in test_cases:
        print(f"\n📋 测试用例: {description}")
        print(f"   标签: {tags}")
        
        try:
            context = handler.get_context_from_knowledge_base(tags)
            print(f"   结果: {len(context)} 字符")
            
            if context:
                # 显示前200个字符作为预览
                preview = context[:200].replace('\n', ' ')
                print(f"   预览: {preview}...")
            else:
                print("   结果: 空内容")
                
        except Exception as e:
            print(f"   ❌ 错误: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_local_knowledge_loading() 