#!/usr/bin/env python3
"""
详细的调试脚本：分析创建知识条目时的具体错误
"""

import json
import requests
from notion_knowledge_db import NotionKnowledgeDB

def debug_create_request():
    """调试创建知识条目的请求"""
    print("🐛 调试知识条目创建请求")
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
    
    # 测试简单的创建请求
    test_data = {
        "parent": {"database_id": kb.knowledge_db_id},
        "properties": {
            "知识标题": {
                "title": [
                    {
                        "text": {
                            "content": "测试知识条目"
                        }
                    }
                ]
            },
            "知识分类": {
                "select": {
                    "name": "AI效率中心"
                }
            },
            "状态": {
                "select": {
                    "name": "启用"
                }
            },
            "优先级": {
                "select": {
                    "name": "高"
                }
            }
        }
    }
    
    print(f"📝 测试数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    # 发送请求
    try:
        url = "https://api.notion.com/v1/pages"
        response = requests.post(url, headers=kb.headers, json=test_data, timeout=30)
        
        print(f"📡 请求URL: {url}")
        print(f"📊 响应状态: {response.status_code}")
        
        if response.status_code == 400:
            error_data = response.json()
            print(f"❌ 错误详情:")
            print(f"   代码: {error_data.get('code', 'N/A')}")
            print(f"   消息: {error_data.get('message', 'N/A')}")
            
            # 检查具体的验证错误
            if 'validation_errors' in error_data:
                print("🔍 验证错误详情:")
                for error in error_data['validation_errors']:
                    print(f"   - {error}")
        elif response.status_code == 200:
            print("✅ 创建成功！")
        else:
            print(f"⚠️  其他错误: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def check_required_fields():
    """检查必需字段配置"""
    print("\n🔍 检查必需字段配置")
    print("=" * 30)
    
    # 加载配置
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return
    
    kb = NotionKnowledgeDB(config)
    
    # 获取数据库schema
    try:
        url = f"https://api.notion.com/v1/databases/{kb.knowledge_db_id}"
        response = requests.get(url, headers=kb.headers, timeout=30)
        response.raise_for_status()
        
        database_info = response.json()
        properties = database_info.get("properties", {})
        
        # 检查必需字段
        required_fields = ["知识标题", "知识分类", "状态", "优先级"]
        missing_fields = []
        
        for field in required_fields:
            if field not in properties:
                missing_fields.append(field)
            else:
                field_info = properties[field]
                print(f"✅ {field}: {field_info['type']}")
                
                # 检查Select字段的选项
                if field_info['type'] in ['select', 'multi_select']:
                    options = field_info[field_info['type']].get('options', [])
                    if options:
                        option_names = [opt['name'] for opt in options]
                        print(f"   选项: {option_names}")
                    else:
                        print(f"   ⚠️  无选项配置")
        
        if missing_fields:
            print(f"\n❌ 缺少必需字段: {missing_fields}")
        else:
            print(f"\n✅ 所有必需字段都存在")
            
    except Exception as e:
        print(f"❌ 获取数据库schema失败: {e}")

if __name__ == "__main__":
    debug_create_request()
    check_required_fields() 