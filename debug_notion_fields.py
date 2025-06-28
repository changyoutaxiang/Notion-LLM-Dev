#!/usr/bin/env python3
"""
Notion数据库字段调试脚本
用于检查知识库数据库的字段配置是否正确
"""

import json
import requests
from notion_knowledge_db import NotionKnowledgeDB

def debug_database_schema():
    """调试数据库模式配置"""
    print("🔍 Notion数据库字段调试")
    print("=" * 50)
    
    # 加载配置
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return
    
    # 创建NotionKnowledgeDB实例
    kb = NotionKnowledgeDB(config)
    
    # 获取数据库schema
    try:
        url = f"https://api.notion.com/v1/databases/{kb.knowledge_db_id}"
        response = requests.get(url, headers=kb.headers, timeout=30)
        response.raise_for_status()
        
        database_info = response.json()
        properties = database_info.get("properties", {})
        
        print(f"📊 数据库标题: {database_info.get('title', [{}])[0].get('text', {}).get('content', '未知')}")
        print(f"📊 数据库ID: {kb.knowledge_db_id}")
        print(f"📊 总字段数: {len(properties)}")
        print()
        
        # 检查必需字段
        required_fields = {
            kb.knowledge_title_prop: "title",
            kb.knowledge_category_prop: "select", 
            kb.knowledge_keywords_prop: "multi_select",
            kb.knowledge_priority_prop: "select",
            kb.knowledge_status_prop: "select",
            kb.knowledge_usage_prop: "number"
        }
        
        print("🔍 检查必需字段...")
        all_fields_ok = True
        
        for field_name, expected_type in required_fields.items():
            if field_name in properties:
                actual_type = properties[field_name].get("type")
                if actual_type == expected_type:
                    print(f"✅ {field_name}: {actual_type}")
                    
                    # 检查Select字段的选项
                    if actual_type == "select":
                        options = properties[field_name].get("select", {}).get("options", [])
                        option_names = [opt.get("name") for opt in options]
                        print(f"   选项: {option_names}")
                        
                        # 检查必需的选项值
                        if field_name == kb.knowledge_priority_prop:
                            if "中" not in option_names:
                                print(f"   ⚠️  缺少选项: '中'")
                                all_fields_ok = False
                        elif field_name == kb.knowledge_status_prop:
                            if "启用" not in option_names:
                                print(f"   ⚠️  缺少选项: '启用'")
                                all_fields_ok = False
                        elif field_name == kb.knowledge_category_prop:
                            required_categories = ["业务知识", "技术文档", "流程规范", "部门介绍"]
                            missing_categories = [cat for cat in required_categories if cat not in option_names]
                            if missing_categories:
                                print(f"   ⚠️  缺少分类选项: {missing_categories}")
                                all_fields_ok = False
                                
                    elif actual_type == "multi_select":
                        options = properties[field_name].get("multi_select", {}).get("options", [])
                        option_names = [opt.get("name") for opt in options]
                        print(f"   选项: {option_names[:5]}{'...' if len(option_names) > 5 else ''}")
                        
                else:
                    print(f"❌ {field_name}: 期望{expected_type}，实际{actual_type}")
                    all_fields_ok = False
            else:
                print(f"❌ 缺少字段: {field_name}")
                all_fields_ok = False
        
        print()
        
        # 检查可选字段
        optional_fields = {
            kb.knowledge_subcategory_prop: "select",
            kb.knowledge_scenarios_prop: "multi_select"
        }
        
        print("🔍 检查可选字段...")
        for field_name, expected_type in optional_fields.items():
            if field_name in properties:
                actual_type = properties[field_name].get("type")
                if actual_type == expected_type:
                    print(f"✅ {field_name}: {actual_type}")
                else:
                    print(f"⚠️  {field_name}: 期望{expected_type}，实际{actual_type}")
            else:
                print(f"⚪ {field_name}: 未配置（可选）")
        
        print()
        
        if all_fields_ok:
            print("🎉 所有必需字段配置正确！")
            
            # 尝试创建一个测试条目
            print("\n🧪 测试创建知识条目...")
            test_entry_id = kb.create_knowledge_entry(
                title="测试知识条目",
                category="业务知识",
                keywords=["测试", "调试"],
                content="这是一个测试条目，用于验证配置是否正确。",
                priority="中",
                status="启用"
            )
            
            if test_entry_id:
                print(f"✅ 测试条目创建成功: {test_entry_id[:8]}...")
                
                # 清理测试条目
                print("🧹 清理测试条目...")
                try:
                    delete_url = f"https://api.notion.com/v1/pages/{test_entry_id}"
                    delete_payload = {"archived": True}
                    requests.patch(delete_url, headers=kb.headers, json=delete_payload, timeout=30)
                    print("✅ 测试条目已清理")
                except:
                    print("⚠️  测试条目清理失败（可手动删除）")
                    
            else:
                print("❌ 测试条目创建失败")
        else:
            print("❌ 数据库字段配置有问题，请修复后再试")
            
    except Exception as e:
        print(f"❌ 获取数据库信息失败: {e}")

if __name__ == "__main__":
    debug_database_schema() 