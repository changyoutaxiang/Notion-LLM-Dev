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
from gui import NotionLLMGUI

def check_dependencies():
    """检查依赖包是否已安装"""
    required_packages = ['requests']
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
                "database_id": "请填入你的Notion数据库ID"
            },
            "openrouter": {
                "api_key": "请填入你的OpenRouter API密钥",
                "model": "anthropic/claude-3.5-sonnet"
            },
            "settings": {
                "check_interval": 120,
                "max_retries": 3,
                "request_timeout": 30
            }
        }
        
        try:
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            print("✅ 已创建默认配置文件 config.json")
            print("⚠️  请在程序中配置你的API密钥")
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
    print()
    print("Notion数据库需要的字段:")
    print("• 标题 (Title)")
    print("• 输入内容 (Rich Text)")  
    print("• 模板选择 (Select)")
    print("• LLM 回复 (Rich Text)")
    print()
    print("🆕 最新功能:")
    print("• 🎯 双异步模式：需选择模板才执行处理")
    print("• 🤖 AI自动生成10-20字的自然标题")
    print("• 📋 完整的模板库管理系统")
    print("• 🔄 自动同步模板选项到Notion")
    print("• 📊 智能统计等待和处理状态")
    print()

def main():
    """主函数"""
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