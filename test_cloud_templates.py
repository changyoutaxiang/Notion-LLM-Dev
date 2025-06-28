#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云端模板库功能测试脚本
用于验证云端部署版本的模板库同步功能是否正常工作
"""

import os
import json
import time
import requests
from datetime import datetime

class CloudTemplatesTester:
    """云端模板库功能测试器"""
    
    def __init__(self, base_url=None):
        # 从环境变量或参数获取云端URL
        self.base_url = base_url or os.getenv("CLOUD_URL", "http://localhost:5000")
        if self.base_url.endswith('/'):
            self.base_url = self.base_url[:-1]
        
        print(f"🌐 测试目标: {self.base_url}")
        print("=" * 50)
    
    def test_health(self):
        """测试健康检查"""
        print("1️⃣ 测试健康检查...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 健康检查通过")
                print(f"   📊 状态: {data.get('status')}")
                print(f"   🕐 时间: {data.get('timestamp')}")
                return True
            else:
                print(f"   ❌ 健康检查失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ 健康检查异常: {e}")
            return False
    
    def test_status(self):
        """测试状态查询"""
        print("\\n2️⃣ 测试状态查询...")
        try:
            response = requests.get(f"{self.base_url}/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 状态查询成功")
                print(f"   🔄 调度器运行: {data.get('is_running')}")
                print(f"   📝 处理消息数: {data.get('message_count')}")
                print(f"   📚 模板数量: {data.get('template_count')}")
                print(f"   🗄️ 模板库已配置: {data.get('template_database_configured')}")
                print(f"   🔄 自动同步启用: {data.get('auto_sync_enabled')}")
                print(f"   🕐 最后同步: {data.get('last_template_sync')}")
                return data
            else:
                print(f"   ❌ 状态查询失败: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"   ❌ 状态查询异常: {e}")
            return None
    
    def test_get_templates(self):
        """测试获取模板列表"""
        print("\\n3️⃣ 测试获取模板列表...")
        try:
            response = requests.get(f"{self.base_url}/templates", timeout=10)
            if response.status_code == 200:
                data = response.json()
                templates = data.get('templates', {})
                categories = data.get('categories', [])
                print(f"   ✅ 获取模板列表成功")
                print(f"   📚 模板总数: {data.get('count')}")
                print(f"   📂 分类数量: {len(categories)}")
                print(f"   🏷️ 分类列表: {', '.join(categories)}")
                print(f"   🕐 最后同步: {data.get('last_sync')}")
                
                if templates:
                    print("   📝 模板列表:")
                    for name, template in list(templates.items())[:5]:  # 只显示前5个
                        print(f"      • {name} ({template.get('category', '未知分类')})")
                    if len(templates) > 5:
                        print(f"      ... 还有 {len(templates) - 5} 个模板")
                else:
                    print("   ⚠️ 模板库为空")
                
                return data
            else:
                print(f"   ❌ 获取模板列表失败: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"   ❌ 获取模板列表异常: {e}")
            return None
    
    def test_sync_from_notion(self):
        """测试从Notion同步模板"""
        print("\\n4️⃣ 测试从Notion同步模板...")
        try:
            response = requests.post(f"{self.base_url}/templates/sync-from-notion", timeout=30)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 从Notion同步成功")
                print(f"   📄 同步结果: {data.get('message')}")
                return True
            else:
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = data.get('error', f'HTTP {response.status_code}')
                print(f"   ❌ 从Notion同步失败: {error_msg}")
                return False
        except Exception as e:
            print(f"   ❌ 从Notion同步异常: {e}")
            return False
    
    def test_sync_to_notion(self):
        """测试同步模板到Notion"""
        print("\\n5️⃣ 测试同步模板到Notion...")
        try:
            response = requests.post(f"{self.base_url}/templates/sync-to-notion", timeout=30)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 同步到Notion成功")
                print(f"   📄 同步结果: {data.get('message')}")
                return True
            else:
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = data.get('error', f'HTTP {response.status_code}')
                print(f"   ❌ 同步到Notion失败: {error_msg}")
                return False
        except Exception as e:
            print(f"   ❌ 同步到Notion异常: {e}")
            return False
    
    def test_specific_template(self, template_name):
        """测试获取特定模板"""
        print(f"\\n6️⃣ 测试获取特定模板: {template_name}")
        try:
            response = requests.get(f"{self.base_url}/templates/{template_name}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                template = data.get('template', {})
                print(f"   ✅ 获取模板成功")
                print(f"   📝 模板名称: {data.get('name')}")
                print(f"   🏷️ 分类: {template.get('category')}")
                print(f"   📄 描述: {template.get('description', '无描述')}")
                print(f"   📏 提示词长度: {len(template.get('prompt', ''))} 字符")
                return True
            elif response.status_code == 404:
                print(f"   ⚠️ 模板不存在: {template_name}")
                return False
            else:
                print(f"   ❌ 获取模板失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ 获取模板异常: {e}")
            return False
    
    def run_full_test(self):
        """运行完整测试"""
        print("🧪 开始云端模板库功能测试")
        print(f"🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        results = []
        
        # 1. 健康检查
        results.append(("健康检查", self.test_health()))
        
        # 2. 状态查询
        status_data = self.test_status()
        results.append(("状态查询", status_data is not None))
        
        # 3. 获取模板列表
        templates_data = self.test_get_templates()
        results.append(("获取模板列表", templates_data is not None))
        
        # 4. 检查是否配置了模板库
        if status_data and status_data.get('template_database_configured'):
            # 5. 从Notion同步测试
            results.append(("从Notion同步", self.test_sync_from_notion()))
            
            # 等待一下再获取更新后的模板
            time.sleep(2)
            updated_templates = self.test_get_templates()
            
            # 6. 测试获取特定模板（如果有模板的话）
            if updated_templates and updated_templates.get('templates'):
                first_template_name = list(updated_templates['templates'].keys())[0]
                results.append(("获取特定模板", self.test_specific_template(first_template_name)))
            
            # 7. 同步到Notion测试
            results.append(("同步到Notion", self.test_sync_to_notion()))
        else:
            print("\\n⚠️ 模板库数据库未配置，跳过同步测试")
            results.append(("模板库配置", False))
        
        # 测试结果总结
        print("\\n" + "=" * 50)
        print("📊 测试结果总结")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, passed_test in results:
            status = "✅ 通过" if passed_test else "❌ 失败"
            print(f"{test_name:<15} {status}")
            if passed_test:
                passed += 1
        
        print("-" * 50)
        print(f"总体结果: {passed}/{total} 项测试通过")
        
        if passed == total:
            print("🎉 所有测试通过！云端模板库功能正常工作")
        elif passed >= total * 0.7:
            print("⚠️ 大部分测试通过，可能存在一些配置问题")
        else:
            print("❌ 多项测试失败，请检查配置和网络连接")
        
        return passed, total

def main():
    """主函数"""
    import sys
    
    # 支持命令行参数指定URL
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("请输入云端URL (回车使用默认 http://localhost:5000): ").strip()
        if not url:
            url = "http://localhost:5000"
    
    tester = CloudTemplatesTester(url)
    tester.run_full_test()

if __name__ == "__main__":
    main() 