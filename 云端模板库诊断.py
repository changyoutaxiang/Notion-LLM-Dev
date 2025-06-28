#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云端模板库诊断工具 v2.2
快速检查和修复云端部署的模板库问题
"""

import requests
import json
import sys
from datetime import datetime

class CloudTemplateDiagnostic:
    """云端模板库诊断工具"""
    
    def __init__(self, domain_url):
        """
        初始化诊断工具
        
        Args:
            domain_url: 云端部署的域名，如 https://your-app.zeabur.app
        """
        self.domain_url = domain_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 10
        
    def print_header(self, title):
        """打印标题"""
        print(f"\n{'='*50}")
        print(f"🔍 {title}")
        print(f"{'='*50}")
    
    def print_result(self, success, message):
        """打印结果"""
        icon = "✅" if success else "❌"
        print(f"{icon} {message}")
    
    def test_health_check(self):
        """测试健康检查"""
        self.print_header("健康检查")
        
        try:
            response = self.session.get(f"{self.domain_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.print_result(True, f"服务正常运行 - {data.get('status', 'unknown')}")
                
                # 检查调度器状态
                scheduler_status = data.get('scheduler_status')
                if scheduler_status:
                    self.print_result(True, f"调度器运行中: {scheduler_status.get('is_running', False)}")
                    if scheduler_status.get('template_database_configured'):
                        self.print_result(True, "模板库数据库已配置")
                    else:
                        self.print_result(False, "模板库数据库未配置 - 这就是问题所在！")
                else:
                    self.print_result(False, "调度器状态未知")
                
                return True, data
            else:
                self.print_result(False, f"健康检查失败 - HTTP {response.status_code}")
                return False, None
                
        except Exception as e:
            self.print_result(False, f"连接失败: {e}")
            return False, None
    
    def test_detailed_status(self):
        """测试详细状态"""
        self.print_header("详细状态检查")
        
        try:
            response = self.session.get(f"{self.domain_url}/status")
            if response.status_code == 200:
                data = response.json()
                
                # 检查关键状态
                self.print_result(True, f"调度器运行: {data.get('is_running', False)}")
                self.print_result(True, f"配置已加载: {data.get('config_loaded', False)}")
                
                # 🔥 关键检查：模板库配置
                template_db_configured = data.get('template_database_configured', False)
                if template_db_configured:
                    self.print_result(True, "模板库数据库已配置")
                else:
                    self.print_result(False, "❗ 模板库数据库未配置 - 需要添加 NOTION_TEMPLATE_DATABASE_ID 环境变量")
                
                # 检查自动同步
                auto_sync = data.get('auto_sync_enabled', False)
                self.print_result(auto_sync, f"自动同步: {'启用' if auto_sync else '禁用'}")
                
                # 检查模板数量
                template_count = data.get('template_count', 0)
                self.print_result(template_count > 0, f"本地模板数量: {template_count}")
                
                # 检查最后同步时间
                last_sync = data.get('last_template_sync')
                if last_sync:
                    self.print_result(True, f"最后同步时间: {last_sync}")
                else:
                    self.print_result(False, "尚未进行过模板库同步")
                
                return True, data
            else:
                self.print_result(False, f"状态检查失败 - HTTP {response.status_code}")
                return False, None
                
        except Exception as e:
            self.print_result(False, f"状态检查失败: {e}")
            return False, None
    
    def test_template_sync(self):
        """测试模板库同步"""
        self.print_header("模板库同步测试")
        
        try:
            # 尝试从Notion同步
            self.print_result(True, "尝试从Notion同步模板库...")
            response = self.session.post(f"{self.domain_url}/templates/sync-from-notion")
            
            if response.status_code == 200:
                data = response.json()
                self.print_result(True, f"同步成功: {data.get('message', '未知')}")
                return True, data
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', f'HTTP {response.status_code}')
                except:
                    error_msg = f'HTTP {response.status_code}'
                
                self.print_result(False, f"同步失败: {error_msg}")
                
                # 常见错误分析
                if "未配置" in error_msg:
                    print("\n💡 解决方案:")
                    print("   1. 在Zeabur控制台添加环境变量:")
                    print("      NOTION_TEMPLATE_DATABASE_ID=your_template_database_id")
                    print("   2. 重新部署应用")
                elif "权限" in error_msg or "Unauthorized" in error_msg:
                    print("\n💡 解决方案:")
                    print("   1. 检查Notion API密钥是否正确")
                    print("   2. 确保API集成已添加到模板库数据库")
                
                return False, error_msg
                
        except Exception as e:
            self.print_result(False, f"同步测试失败: {e}")
            return False, str(e)
    
    def test_template_list(self):
        """测试模板列表"""
        self.print_header("模板列表检查")
        
        try:
            response = self.session.get(f"{self.domain_url}/templates")
            if response.status_code == 200:
                data = response.json()
                templates = data.get('templates', [])
                
                if templates:
                    self.print_result(True, f"找到 {len(templates)} 个模板:")
                    for template in templates[:5]:  # 只显示前5个
                        name = template.get('name', '未知')
                        category = template.get('category', '未分类')
                        status = template.get('status', '未知')
                        print(f"   📋 {name} [{category}] - {status}")
                    
                    if len(templates) > 5:
                        print(f"   ... 还有 {len(templates) - 5} 个模板")
                else:
                    self.print_result(False, "没有找到任何模板")
                
                return True, templates
            else:
                self.print_result(False, f"获取模板列表失败 - HTTP {response.status_code}")
                return False, None
                
        except Exception as e:
            self.print_result(False, f"模板列表检查失败: {e}")
            return False, None
    
    def run_full_diagnostic(self):
        """运行完整诊断"""
        print(f"🚀 开始云端模板库诊断")
        print(f"🌐 目标域名: {self.domain_url}")
        print(f"⏰ 诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. 健康检查
        health_ok, health_data = self.test_health_check()
        
        # 2. 详细状态
        status_ok, status_data = self.test_detailed_status()
        
        # 3. 模板同步测试
        sync_ok, sync_data = self.test_template_sync()
        
        # 4. 模板列表
        templates_ok, templates_data = self.test_template_list()
        
        # 生成诊断报告
        self.print_header("诊断总结")
        
        total_tests = 4
        passed_tests = sum([health_ok, status_ok, sync_ok, templates_ok])
        
        if passed_tests == total_tests:
            print("🎉 所有测试通过！云端模板库功能正常")
        else:
            print(f"⚠️  通过 {passed_tests}/{total_tests} 项测试")
            
            if not health_ok:
                print("\n❗ 问题1: 服务连接失败")
                print("   💡 解决方案: 检查域名是否正确，服务是否正常启动")
            
            if not status_ok:
                print("\n❗ 问题2: 状态检查失败")
                print("   💡 解决方案: 检查应用是否正常部署")
            
            if not sync_ok:
                print("\n❗ 问题3: 模板库同步失败")
                print("   💡 这通常是主要问题，检查以下配置:")
                print("   - NOTION_TEMPLATE_DATABASE_ID 环境变量")
                print("   - Notion API密钥权限")
                print("   - 模板库数据库结构")
            
            if not templates_ok:
                print("\n❗ 问题4: 无法获取模板列表")
                print("   💡 解决方案: 先解决同步问题")

def main():
    """主函数"""
    print("🔧 Notion-LLM 云端模板库诊断工具 v2.2")
    
    if len(sys.argv) != 2:
        print("\n使用方法:")
        print("  python 云端模板库诊断.py https://your-app.zeabur.app")
        print("\n示例:")
        print("  python 云端模板库诊断.py https://my-notion-llm.zeabur.app")
        sys.exit(1)
    
    domain_url = sys.argv[1]
    diagnostic = CloudTemplateDiagnostic(domain_url)
    diagnostic.run_full_diagnostic()

if __name__ == "__main__":
    main() 