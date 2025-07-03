#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置验证工具
用于验证config.json配置文件是否正确设置
"""

import json
import os
import sys
import re
import requests

def load_config():
    """加载配置文件"""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ 配置文件 config.json 不存在")
        print("请先运行 main.py 创建默认配置文件")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件格式错误: {e}")
        return None
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return None

def validate_notion_config(config):
    """验证Notion配置"""
    print("\n🔍 验证Notion配置...")
    
    notion_config = config.get("notion", {})
    issues = []
    
    # 检查必要字段
    required_fields = {
        "api_key": "Notion API密钥",
        "database_id": "Notion数据库ID"
    }
    
    for field, description in required_fields.items():
        value = notion_config.get(field, "")
        if not value or value.startswith("请填入"):
            issues.append(f"  - {description}未设置")
    
    # 检查属性名称
    property_fields = {
        "input_property_name": "输入",
        "output_property_name": "回复",
        "status_property_name": "状态",
        "template_property_name": "模板选择",
        "knowledge_base_property_name": "背景",
        "model_property_name": "模型",
        "title_property_name": "标题"
    }
    
    for field, expected in property_fields.items():
        value = notion_config.get(field, "")
        if not value:
            issues.append(f"  - {field}未设置")
    
    if issues:
        print("❌ Notion配置有问题:")
        for issue in issues:
            print(issue)
        return False
    else:
        print("✅ Notion配置字段填写正确，正在检测API连通性...")

    # ----------- 新增: Notion API连通性检测 -----------
    api_key = notion_config.get("api_key", "")
    database_id = notion_config.get("database_id", "")

    # 检查 database_id 格式（32位或带-的UUID）
    uuid_pattern = re.compile(r"^[0-9a-fA-F]{32}$|^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
    if not uuid_pattern.match(database_id):
        print(f"❌ 数据库ID格式可能有误: {database_id}")
        print("请确认数据库ID为32位字符串或带-的UUID，可在Notion数据库页面链接中获取。")
        return False

    # 请求Notion API
    url = f"https://api.notion.com/v1/databases/{database_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            print("✅ Notion API连通性检测通过，配置有效！")
        return True
        else:
            print(f"❌ Notion API请求失败，状态码: {resp.status_code}")
            try:
                err = resp.json()
                print(f"错误信息: {err.get('message', str(err))}")
            except Exception:
                print(f"响应内容: {resp.text}")
            if resp.status_code == 400:
                print("可能原因：数据库ID格式错误，或该ID不是数据库。")
            elif resp.status_code == 401:
                print("可能原因：API密钥无效或已过期。")
            elif resp.status_code == 403:
                print("可能原因：API密钥没有访问该数据库的权限，请在Notion中将集成添加为数据库成员。")
            elif resp.status_code == 404:
                print("可能原因：数据库ID不存在，或API密钥无权访问。")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求异常: {e}")
        print("请检查网络连接，或稍后重试。")
        return False

def validate_openrouter_config(config):
    """验证OpenRouter配置"""
    print("\n🔍 验证OpenRouter配置...")
    
    openrouter_config = config.get("openrouter", {})
    issues = []
    
    # 检查API密钥
    api_key = openrouter_config.get("api_key", "")
    if not api_key or api_key.startswith("请填入"):
        issues.append("  - OpenRouter API密钥未设置")
    
    # 检查模型
    model = openrouter_config.get("model", "")
    if not model:
        issues.append("  - 默认模型未设置")
    
    if issues:
        print("❌ OpenRouter配置有问题:")
        for issue in issues:
            print(issue)
        return False
    else:
        print("✅ OpenRouter配置正确")
        return True

def validate_settings_config(config):
    """验证设置配置"""
    print("\n🔍 验证设置配置...")
    
    settings_config = config.get("settings", {})
    issues = []
    
    # 检查数值型设置
    numeric_fields = {
        "check_interval": (30, 3600),  # 30秒到1小时
        "max_retries": (1, 10),
        "request_timeout": (10, 300),
        "title_max_length": (10, 100),
        "title_min_length": (5, 50),
        "sync_interval_hours": (1, 168)  # 1小时到7天
    }
    
    for field, (min_val, max_val) in numeric_fields.items():
        value = settings_config.get(field)
        if value is None:
            issues.append(f"  - {field}未设置")
        elif not isinstance(value, (int, float)) or value < min_val or value > max_val:
            issues.append(f"  - {field}值无效，应在{min_val}-{max_val}之间")
    
    # 检查模型映射
    model_mapping = settings_config.get("model_mapping", {})
    if not model_mapping:
        issues.append("  - 模型映射未设置")
    elif not isinstance(model_mapping, dict):
        issues.append("  - 模型映射格式错误")
    
    if issues:
        print("❌ 设置配置有问题:")
        for issue in issues:
            print(issue)
        return False
    else:
        print("✅ 设置配置正确")
        return True

def validate_knowledge_config(config):
    """验证知识库配置"""
    print("\n🔍 验证知识库配置...")
    
    knowledge_config = config.get("knowledge_search", {})
    issues = []
    
    # 检查基本设置
    enable_rag = knowledge_config.get("enable_smart_rag", False)
    if not isinstance(enable_rag, bool):
        issues.append("  - enable_smart_rag应为布尔值")
    
    max_snippets = knowledge_config.get("max_snippets", 5)
    if not isinstance(max_snippets, int) or max_snippets < 1 or max_snippets > 20:
        issues.append("  - max_snippets应为1-20之间的整数")
    
    similarity_threshold = knowledge_config.get("similarity_threshold", 0.3)
    if not isinstance(similarity_threshold, (int, float)) or similarity_threshold < 0 or similarity_threshold > 1:
        issues.append("  - similarity_threshold应为0-1之间的数值")
    
    if issues:
        print("❌ 知识库配置有问题:")
        for issue in issues:
            print(issue)
        return False
    else:
        print("✅ 知识库配置正确")
        return True

def check_file_structure():
    """检查文件结构"""
    print("\n🔍 检查文件结构...")
    
    required_files = [
        "main.py",
        "gui.py",
        "scheduler.py",
        "cloud_main.py",
        "notion_handler.py",
        "llm_handler.py",
        "template_manager.py",
        "templates.json",
        "requirements.txt"
    ]
    
    required_dirs = [
        "knowledge_base"
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    for dir in required_dirs:
        if not os.path.exists(dir):
            missing_dirs.append(dir)
    
    if missing_files or missing_dirs:
        print("❌ 缺少必要文件:")
        for file in missing_files:
            print(f"  - {file}")
        for dir in missing_dirs:
            print(f"  - {dir}/ (目录)")
        return False
    else:
        print("✅ 文件结构完整")
        return True

def main():
    """主函数"""
    print("🔧 Notion-LLM 配置验证工具")
    print("=" * 50)
    
    # 加载配置
    config = load_config()
    if config is None:
        sys.exit(1)
    
    # 验证各部分配置
    results = []
    results.append(validate_notion_config(config))
    results.append(validate_openrouter_config(config))
    results.append(validate_settings_config(config))
    results.append(validate_knowledge_config(config))
    results.append(check_file_structure())
    
    # 总结结果
    print("\n" + "=" * 50)
    if all(results):
        print("🎉 所有配置验证通过！")
        print("你现在可以正常使用Notion-LLM程序了。")
        print("\n使用方法:")
        print("1. 本地GUI模式: python main.py")
        print("2. 云端API模式: python cloud_main.py")
    else:
        print("❌ 配置验证失败")
        print("请按照上述提示修正配置后重新验证。")
        sys.exit(1)

if __name__ == "__main__":
    main() 