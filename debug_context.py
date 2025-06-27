#!/usr/bin/env python3
"""
LLM上下文调试工具
用于查看发送给LLM的完整上下文内容，方便用户抽查背景文件是否正确加载
"""

import json
import os
from notion_handler import NotionHandler
from template_manager import TemplateManager

def load_config():
    """加载配置文件"""
    if os.path.exists("config.json"):
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        print("❌ 配置文件 config.json 未找到")
        return None

def debug_message_context():
    """调试消息上下文构建过程"""
    config = load_config()
    if not config:
        return
    
    # 初始化处理器
    notion_handler = NotionHandler(config)
    template_manager = TemplateManager()
    
    print("🔍 LLM上下文调试工具")
    print("=" * 50)
    
    try:
        # 获取最新的待处理消息
        pending_messages = notion_handler.get_pending_messages()
        
        if not pending_messages:
            print("📭 没有待处理的消息")
            return
        
        print(f"📝 找到 {len(pending_messages)} 条待处理消息")
        print()
        
        for i, message in enumerate(pending_messages, 1):
            print(f"🔹 消息 {i}/{len(pending_messages)}")
            print("-" * 30)
            
            # 提取消息信息
            content = message["content"]
            template_choice = message.get("template_choice", "")
            tags = message.get("tags", [])
            model_choice = message.get("model_choice", "")
            
            print(f"📋 用户输入: {content[:100]}...")
            print(f"🏷️  模板选择: {template_choice}")
            print(f"🔖 背景标签: {tags}")
            print(f"🤖 模型选择: {model_choice}")
            print()
            
            # 1. 获取知识库上下文
            print("📚 === 知识库上下文 ===")
            knowledge_context = notion_handler.get_context_from_knowledge_base(tags)
            
            if knowledge_context:
                print(f"✅ 成功加载背景文件，长度: {len(knowledge_context)} 字符")
                print("📄 背景文件内容预览 (前500字符):")
                print("-" * 40)
                print(knowledge_context[:500])
                if len(knowledge_context) > 500:
                    print("... (后续内容省略)")
                print("-" * 40)
            else:
                print("❌ 未加载到背景文件内容")
                if "无" in tags:
                    print("ℹ️  原因: 选择了'无'背景标签")
                else:
                    print(f"ℹ️  原因: 标签 {tags} 对应的文件不存在")
            print()
            
            # 2. 获取系统提示词
            print("🎯 === 系统提示词 ===")
            system_prompt = ""
            if template_choice:
                template = template_manager.get_template(template_choice)
                if template:
                    system_prompt = template["prompt"]
                    print(f"✅ 使用模板: {template_choice}")
                else:
                    print(f"❌ 模板未找到: {template_choice}")
            
            if not system_prompt:
                system_prompt = config.get("settings", {}).get("system_prompt", "你是一个智能助手，请认真回答用户的问题。请用中文回复。")
                print("✅ 使用默认系统提示词")
            
            print("📄 系统提示词内容:")
            print("-" * 40)
            print(system_prompt)
            print("-" * 40)
            print()
            
            # 3. 组合最终发送给LLM的内容
            print("🚀 === 最终发送给LLM的完整内容 ===")
            final_content = content
            if knowledge_context:
                final_content = f"""
{knowledge_context}

---

请严格根据以上知识库内容，直接回答用户的问题，不要输出任何额外的思考或推理过程。

用户问题如下:
{content}
"""
            
            print("📤 User Message Content:")
            print("=" * 60)
            print(final_content)
            print("=" * 60)
            print()
            
            # 统计信息
            print("📊 === 统计信息 ===")
            print(f"• 系统提示词长度: {len(system_prompt)} 字符")
            print(f"• 背景文件长度: {len(knowledge_context) if knowledge_context else 0} 字符") 
            print(f"• 用户问题长度: {len(content)} 字符")
            print(f"• 最终内容长度: {len(final_content)} 字符")
            print()
            
            # 询问是否继续查看下一条
            if i < len(pending_messages):
                user_input = input("❓ 按回车继续查看下一条，输入 'q' 退出: ")
                if user_input.lower() == 'q':
                    break
                print("\n" + "=" * 50 + "\n")
        
        print("✅ 调试完成")
        
    except Exception as e:
        print(f"❌ 调试过程中出错: {e}")

def debug_knowledge_base():
    """调试知识库文件"""
    print("📚 知识库文件调试")
    print("=" * 30)
    
    knowledge_dir = "knowledge_base"
    if not os.path.exists(knowledge_dir):
        print(f"❌ 知识库目录不存在: {knowledge_dir}")
        return
    
    # 列出所有知识库文件
    files = [f for f in os.listdir(knowledge_dir) if f.endswith('.md')]
    
    if not files:
        print("📭 知识库目录为空")
        return
    
    print(f"📂 找到 {len(files)} 个知识库文件:")
    for file in files:
        file_path = os.path.join(knowledge_dir, file)
        file_size = os.path.getsize(file_path)
        tag_name = file.replace('.md', '')
        print(f"  • {tag_name} ({file_size} 字节)")
    
    print()
    
    # 让用户选择查看文件内容
    while True:
        tag_input = input("🔍 输入标签名查看内容 (直接回车退出): ").strip()
        if not tag_input:
            break
        
        file_path = os.path.join(knowledge_dir, f"{tag_input}.md")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                print(f"\n📄 {tag_input} 的内容:")
                print("-" * 50)
                print(content)
                print("-" * 50)
                print(f"📊 总长度: {len(content)} 字符\n")
            except Exception as e:
                print(f"❌ 读取文件失败: {e}")
        else:
            print(f"❌ 文件未找到: {tag_input}.md")

def main():
    """主函数"""
    print("🛠️  LLM上下文调试工具")
    print("用于检查背景文件是否正确加载到LLM上下文中")
    print()
    
    while True:
        print("请选择调试模式:")
        print("1. 调试待处理消息的完整上下文")
        print("2. 查看知识库文件内容")
        print("3. 退出")
        
        choice = input("\n请输入选择 (1-3): ").strip()
        
        if choice == "1":
            print()
            debug_message_context()
        elif choice == "2":
            print()
            debug_knowledge_base()
        elif choice == "3":
            print("👋 再见!")
            break
        else:
            print("❌ 无效选择，请重新输入")
        
        print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    main() 