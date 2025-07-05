#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion-LLM 异步通信助手
作者: AI Assistant
版本: 1.0.0

这个程序帮助你实现Notion与LLM之间的异步通信：
1. 监听Notion数据库中的新消息
2. 自动发送给LLM处理
3. 将回复写回Notion数据库

使用前请确保：
1. 安装了必要的依赖包 (运行: pip install -r requirements.txt)
2. 在config.json中配置了正确的API密钥
3. Notion数据库有正确的字段结构
"""

import sys
import os
import json

# 检查是否为云端部署环境
if os.environ.get('CLOUD_DEPLOYMENT') == 'true' or os.environ.get('PORT'):
    # 云端环境，启动云端版本
    print("🌐 检测到云端部署环境，启动云端版本...")
    from cloud_main import app, CloudScheduler
    import threading
    
    def start_cloud_version():
        # 创建调度器实例
        scheduler = CloudScheduler()
        
        # 如果设置了自动启动，则启动调度器
        if os.environ.get("AUTO_START", "true").lower() == "true":
            threading.Thread(target=scheduler.start, daemon=True).start()
            print("✅ 自动启动调度器")
        
        # 启动Flask服务
        port = int(os.environ.get('PORT', 5000))
        app.run(host="0.0.0.0", port=port, debug=False)
    
    if __name__ == "__main__":
        start_cloud_version()
        sys.exit(0)
else:
    # 本地环境，导入GUI模块
    try:
        from gui import NotionLLMGUI
    except ImportError as e:
        print(f"❌ GUI模块导入失败: {e}")
        print("💡 如果您想在云端运行，请设置环境变量 CLOUD_DEPLOYMENT=true")
        sys.exit(1)

def check_dependencies():
    """检查依赖包是否已安装"""
    required_packages = ['requests', 'flask', 'dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少必要的依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def check_config_file():
    """检查配置文件是否存在"""
    if not os.path.exists("config.json"):
        print("❌ 配置文件 config.json 不存在")
        
        # 创建默认配置文件
        default_config = {
            "notion": {
                "api_key": "请填入你的Notion API密钥",
                "database_id": "请填入你的Notion数据库ID",
                "input_property_name": "输入",
                "output_property_name": "回复",
                "status_property_name": "状态",
                "status_in_progress": "In progress",
                "status_done": "Done",
                "template_property_name": "模板选择",
                "knowledge_base_property_name": "背景",
                "model_property_name": "模型",
                "title_property_name": "标题",
                "knowledge_base_path": "knowledge_base",
                "template_database_id": "请填入你的模板库数据库ID（可选）",
                "template_name_property": "模板名称",
                "template_category_property": "分类",
                "template_prompt_property": "提示词",
                "template_description_property": "描述",
                "template_status_property": "状态"
            },
            "openrouter": {
                "api_key": "请填入你的OpenRouter API密钥",
                "model": "anthropic/claude-3.5-sonnet"
            },
            "settings": {
                "check_interval": 120,
                "max_retries": 3,
                "request_timeout": 30,
                "system_prompt": "你是一个智能助手，请认真回答用户的问题。请用中文回复。",
                "require_template_selection": True,
                "auto_generate_title": True,
                "title_max_length": 20,
                "title_min_length": 10,
                "auto_sync_templates": True,
                "sync_on_startup": True,
                "sync_interval_hours": 24,
                "model_mapping": {
                    "Gemini 2.5 pro": "google/gemini-2.5-pro",
                    "Gemini 2.5 flash": "google/gemini-2.5-flash",
                    "Claude 4 sonnet": "anthropic/claude-sonnet-4",
                    "Chatgpt 4.1": "openai/gpt-4.1",
                    "Chatgpt O3": "openai/o3",
                    "Deepseek R1": "deepseek/deepseek-r1-0528",
                    "Deepseek V3": "deepseek/deepseek-chat-v3-0324"
                }
            },
            "knowledge_search": {
                "enable_smart_rag": False,
                "max_snippets": 5,
                "similarity_threshold": 0.3
            }
        }
        
        try:
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            print("✅ 已创建默认配置文件 config.json")
            print("⚠️  请在程序中配置你的API密钥和数据库ID")
            return True
        except Exception as e:
            print(f"❌ 创建配置文件失败: {e}")
            return False
    
    print("✅ 配置文件存在")
    return True

def print_welcome():
    """打印欢迎信息"""
    print("=" * 60)
    print("🤖 Notion-LLM 异步通信助手")
    print("=" * 60)
    print()
    print("功能特点:")
    print("• 📝 监听Notion数据库中的新消息")
    print("• 🧠 自动调用LLM (通过OpenRouter) 处理消息")
    print("• 🔄 将LLM回复自动写回Notion数据库")
    print("• 🖥️  简单易用的图形界面")
    print("• 📊 实时监控和日志记录")
    print("• 🗂️  模板库管理和同步")
    print("• 📚 支持知识库背景上下文")
    print("• ☁️  支持云端部署")
    print()
    print("Notion数据库需要的字段:")
    print("• 标题 (Title)")
    print("• 输入 (Rich Text)")  
    print("• 模板选择 (Select)")
    print("• 背景 (Multi-select)")
    print("• 模型 (Select)")
    print("• 回复 (Rich Text)")
    print("• 状态 (Select)")
    print()
    print("🆕 简化版特性:")
    print("• 🎯 本地GUI + 云端API双模式")
    print("• 🤖 AI自动生成标题")
    print("• 📋 完整的模板库管理")
    print("• 🔄 自动同步模板选项")
    print("• 📚 本地知识库RAG支持")
    print("• 📊 智能状态监控")
    print()

def main():
    """主函数"""
    # 检查是否为云端部署环境
    if os.environ.get('CLOUD_DEPLOYMENT') == 'true' or os.environ.get('PORT'):
        # 云端环境已经在文件开头处理了
        return
    
    print_welcome()
    
    # 检查运行环境
    print("🔍 检查运行环境...")
    
    if not check_dependencies():
        print("\n❌ 请先安装依赖包后再运行程序")
        input("按回车键退出...")
        return
    
    if not check_config_file():
        print("\n❌ 配置文件问题，程序无法启动")
        input("按回车键退出...")
        return
    
    print("\n🚀 启动图形界面...")
    
    try:
        # 启动GUI
        app = NotionLLMGUI()
        app.root.protocol("WM_DELETE_WINDOW", app.on_closing)  # 处理窗口关闭事件
        app.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main() 