#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的端到端测试 - 模拟真实的消息处理流程
"""

import os
import sys
from notion_handler import NotionHandler
from llm_handler import LLMHandler
from template_manager import TemplateManager

def test_full_message_processing():
    """测试完整的消息处理流程"""
    print("=" * 80)
    print("🧪 完整的端到端测试 - 模拟真实消息处理")
    print("=" * 80)
    
    # 加载配置
    try:
        import json
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✅ 配置加载成功")
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return
    
    # 初始化组件
    try:
        notion_handler = NotionHandler(config)
        llm_handler = LLMHandler(
            config["openrouter"]["api_key"],
            config["openrouter"]["model"]
        )
        template_manager = TemplateManager()
        print("✅ 所有组件初始化成功")
    except Exception as e:
        print(f"❌ 组件初始化失败: {e}")
        return
    
    # 模拟消息数据
    test_message = {
        "page_id": "test_page_id",
        "content": "我们部门对各个部门的 Ai 支持赋能中，应该在有限资源下，有限选择杠杆部门，如何评估和选择？",
        "template_choice": "组织智能化",
        "tags": ["AI效率中心"],  # 这是关键！确保标签正确
        "model_choice": ""
    }
    
    print(f"\n📋 测试消息:")
    print(f"   内容: {test_message['content']}")
    print(f"   模板: {test_message['template_choice']}")
    print(f"   标签: {test_message['tags']}")
    
    # 步骤1: 测试背景文件加载
    print(f"\n🔍 步骤1: 测试背景文件加载")
    knowledge_context = notion_handler.get_context_from_knowledge_base(test_message['tags'])
    print(f"   背景文件长度: {len(knowledge_context)} 字符")
    
    if knowledge_context:
        print(f"   背景文件预览: {knowledge_context[:200]}...")
    
    # 步骤2: 测试模板获取
    print(f"\n🔍 步骤2: 测试模板获取")
    try:
        template_data = template_manager.get_template(test_message['template_choice'])
        if template_data:
            base_system_prompt = template_data['prompt']
            print(f"   系统提示词长度: {len(base_system_prompt)} 字符")
            print(f"   系统提示词预览: {base_system_prompt[:200]}...")
        else:
            print(f"   ❌ 未找到模板: {test_message['template_choice']}")
            return
    except Exception as e:
        print(f"   ❌ 获取模板失败: {e}")
        return
    
    # 步骤3: 测试提示词组合
    print(f"\n🔍 步骤3: 测试提示词组合")
    if knowledge_context:
        system_prompt = f"""{base_system_prompt}

---

## 补充背景知识
{knowledge_context}

---

## 执行指令
请在严格遵循上述角色设定和输出格式的前提下，充分利用补充背景知识来增强回答质量。执行优先级：
1. 首要：保持角色设定的风格、格式和字数要求
2. 重要：当背景知识与用户问题相关时，深度融合背景信息
3. 补充：如背景知识不足或不相关，请明确说明并基于角色专业知识回答
4. 冲突处理：如背景信息与角色设定冲突，优先遵循角色设定"""
    else:
        system_prompt = base_system_prompt
    
    print(f"   最终系统提示词长度: {len(system_prompt)} 字符")
    
    # 步骤4: 构建最终输入
    print(f"\n🔍 步骤4: 构建最终LLM输入")
    final_input = f"{system_prompt}\n\n用户问题: {test_message['content']}"
    print(f"   最终输入长度: {len(final_input)} 字符")
    
    # 显示调试信息（模拟实际运行时的日志）
    print(f"\n" + "="*50)
    print("=== 调试信息（模拟实际运行日志） ===")
    print("="*50)
    print(f"System Prompt Length: {len(system_prompt)} characters")
    print(f"Final Content Sent to LLM: {final_input[:100]}...")
    print(f"Background file content length: {len(knowledge_context)} characters")
    print("="*50)
    
    # 步骤5: 测试LLM调用（可选）
    print(f"\n🔍 步骤5: 测试LLM调用")
    user_choice = input("是否要测试真实的LLM调用？(y/n): ").strip().lower()
    
    if user_choice == 'y':
        try:
            print("📤 发送请求到LLM...")
            response = llm_handler.get_response(system_prompt, test_message['content'])
            print(f"✅ LLM回复成功")
            print(f"   回复长度: {len(response)} 字符")
            print(f"   回复预览: {response[:300]}...")
            
            # 检查回复是否包含背景知识的关键词
            keywords = ["AI经理", "效率中心", "智能化转型", "赋能", "杠杆"]
            found_keywords = [kw for kw in keywords if kw in response]
            if found_keywords:
                print(f"✅ 回复包含背景知识关键词: {found_keywords}")
            else:
                print("⚠️  回复中未发现明显的背景知识关键词")
                
        except Exception as e:
            print(f"❌ LLM调用失败: {e}")
    else:
        print("⏭️  跳过LLM调用测试")
    
    print(f"\n" + "=" * 80)
    print("🏁 完整测试完成")
    print("=" * 80)
    
    # 给出诊断建议
    print(f"\n💡 诊断建议:")
    if len(knowledge_context) > 0:
        print("✅ 背景文件加载正常")
        print("🔧 如果实际运行时仍显示0字符，请检查:")
        print("   1. Notion中的'背景'标签是否正确设置为'AI效率中心'")
        print("   2. 是否运行的是正确的版本（本地/云端）")
        print("   3. 检查实际运行的代码是否是最新版本")
    else:
        print("❌ 背景文件加载失败")
        print("🔧 请检查knowledge_base目录和文件是否存在")

if __name__ == "__main__":
    test_full_message_processing() 