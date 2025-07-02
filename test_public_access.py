#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地RAG服务公网访问配置测试脚本
验证网络配置是否正确，指导下一步操作
"""

import requests
import socket
import subprocess
import time
import json
from datetime import datetime

class PublicAccessTester:
    """公网访问配置测试器"""
    
    def __init__(self):
        self.local_ip = "127.0.0.1"
        self.internal_ip = "172.16.228.45"  # 内网IP
        self.public_ip = "1.203.80.194"     # 公网IP  
        self.port = 8001
        self.timeout = 5
        
        self.test_results = []
        
    def log_result(self, test_name, success, message, suggestion=""):
        """记录测试结果"""
        status = "✅ 通过" if success else "❌ 失败"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "suggestion": suggestion,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        self.test_results.append(result)
        
        print(f"{status} {test_name}: {message}")
        if suggestion and not success:
            print(f"   💡 建议: {suggestion}")
        
    def test_local_access(self):
        """测试1: 本地访问"""
        print("\n🔍 测试1: 本地服务访问")
        
        try:
            response = requests.get(f"http://{self.local_ip}:{self.port}/health", 
                                  timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "本地访问测试",
                    True,
                    f"服务正常运行，版本: {data.get('version', 'unknown')}"
                )
                return True
            else:
                self.log_result(
                    "本地访问测试",
                    False,
                    f"服务返回错误状态码: {response.status_code}",
                    "检查RAG服务是否正常启动"
                )
                return False
        except Exception as e:
            self.log_result(
                "本地访问测试",
                False,
                f"连接失败: {e}",
                "运行 python3 start_local_rag_service.py start"
            )
            return False
    
    def test_internal_access(self):
        """测试2: 内网访问"""
        print("\n🌐 测试2: 内网IP访问")
        
        try:
            response = requests.get(f"http://{self.internal_ip}:{self.port}/health", 
                                  timeout=self.timeout)
            if response.status_code == 200:
                self.log_result(
                    "内网访问测试",
                    True,
                    f"内网访问正常 ({self.internal_ip}:{self.port})"
                )
                return True
            else:
                self.log_result(
                    "内网访问测试",
                    False,
                    f"内网访问失败，状态码: {response.status_code}",
                    "检查服务是否绑定到0.0.0.0"
                )
                return False
        except Exception as e:
            self.log_result(
                "内网访问测试",
                False,
                f"内网连接失败: {e}",
                "确认服务监听在0.0.0.0:8001而非127.0.0.1:8001"
            )
            return False
    
    def test_port_listening(self):
        """测试3: 端口监听状态"""
        print("\n🔌 测试3: 端口监听状态")
        
        try:
            # 检查端口监听状态
            result = subprocess.run(['netstat', '-an'], 
                                  capture_output=True, text=True)
            
            if f"*.{self.port}" in result.stdout:
                self.log_result(
                    "端口监听检查",
                    True,
                    f"端口{self.port}正确监听所有接口 (*)"
                )
                return True
            elif f"127.0.0.1.{self.port}" in result.stdout:
                self.log_result(
                    "端口监听检查",
                    False,
                    f"端口{self.port}只监听本地接口",
                    "修改服务配置为host='0.0.0.0'"
                )
                return False
            else:
                self.log_result(
                    "端口监听检查",
                    False,
                    f"端口{self.port}未找到监听",
                    "启动RAG服务"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "端口监听检查",
                False,
                f"检查失败: {e}",
                "手动运行: netstat -an | grep 8001"
            )
            return False
    
    def test_firewall_status(self):
        """测试4: 防火墙状态"""
        print("\n🛡️ 测试4: 防火墙状态检查")
        
        try:
            # 检查macOS防火墙状态
            result = subprocess.run([
                'sudo', '/usr/libexec/ApplicationFirewall/socketfilterfw', 
                '--getglobalstate'
            ], capture_output=True, text=True)
            
            if "enabled" in result.stdout.lower():
                self.log_result(
                    "防火墙状态检查",
                    False,
                    "防火墙已启用，可能阻止外部访问",
                    "运行防火墙配置命令或关闭防火墙"
                )
                return False
            else:
                self.log_result(
                    "防火墙状态检查",
                    True,
                    "防火墙已关闭或允许访问"
                )
                return True
                
        except Exception as e:
            self.log_result(
                "防火墙状态检查",
                False,
                f"检查失败: {e}",
                "手动检查系统偏好设置 → 安全性与隐私 → 防火墙"
            )
            return False
    
    def test_router_connectivity(self):
        """测试5: 路由器连通性"""
        print("\n🌐 测试5: 路由器连通性")
        
        # 常见路由器地址
        router_ips = ["192.168.1.1", "192.168.0.1", "10.0.0.1"]
        
        for router_ip in router_ips:
            try:
                # 尝试ping路由器
                result = subprocess.run(['ping', '-c', '1', router_ip], 
                                      capture_output=True, text=True, timeout=3)
                
                if result.returncode == 0:
                    self.log_result(
                        "路由器连通性检查",
                        True,
                        f"路由器可访问: {router_ip}"
                    )
                    print(f"   📋 请访问 http://{router_ip} 配置端口转发")
                    return True
                    
            except Exception:
                continue
        
        self.log_result(
            "路由器连通性检查",
            False,
            "无法连接到路由器",
            "检查网络连接或路由器地址"
        )
        return False
    
    def test_public_ip_reachability(self):
        """测试6: 公网IP可达性"""
        print("\n🌍 测试6: 公网IP可达性")
        
        try:
            # 测试公网IP是否可ping通
            result = subprocess.run(['ping', '-c', '3', self.public_ip], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.log_result(
                    "公网IP可达性",
                    True,
                    f"公网IP {self.public_ip} 可以ping通"
                )
                return True
            else:
                self.log_result(
                    "公网IP可达性",
                    False,
                    f"公网IP {self.public_ip} 无法ping通",
                    "检查网络连接或IP地址是否正确"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "公网IP可达性",
                False,
                f"测试失败: {e}",
                "检查网络连接"
            )
            return False
    
    def provide_configuration_guide(self):
        """提供配置指导"""
        print("\n" + "="*60)
        print("📋 配置指导建议")
        print("="*60)
        
        # 分析测试结果
        local_ok = any(r['test'] == "本地访问测试" and r['success'] for r in self.test_results)
        internal_ok = any(r['test'] == "内网访问测试" and r['success'] for r in self.test_results)
        port_ok = any(r['test'] == "端口监听检查" and r['success'] for r in self.test_results)
        firewall_ok = any(r['test'] == "防火墙状态检查" and r['success'] for r in self.test_results)
        router_ok = any(r['test'] == "路由器连通性检查" and r['success'] for r in self.test_results)
        
        print(f"\n🎯 当前配置状态:")
        print(f"   本地服务: {'✅' if local_ok else '❌'}")
        print(f"   内网访问: {'✅' if internal_ok else '❌'}")
        print(f"   端口监听: {'✅' if port_ok else '❌'}")
        print(f"   防火墙: {'✅' if firewall_ok else '❌'}")
        print(f"   路由器: {'✅' if router_ok else '❌'}")
        
        print(f"\n📝 下一步操作:")
        
        if not local_ok:
            print("   1. 启动RAG服务: python3 start_local_rag_service.py start")
        elif not internal_ok or not port_ok:
            print("   1. 服务配置已修正，应该可以内网访问")
        else:
            print("   1. ✅ 本地配置已完成")
            
        if not firewall_ok:
            print("   2. 配置防火墙:")
            print("      sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3")
            print("      sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/bin/python3")
        else:
            print("   2. ✅ 防火墙配置正常")
            
        if router_ok:
            print("   3. 配置路由器端口转发:")
            print(f"      外部端口: {self.port}")
            print(f"      内部IP: {self.internal_ip}")
            print(f"      内部端口: {self.port}")
            print("      协议: TCP")
        else:
            print("   3. ❌ 检查路由器连接")
            
        print("   4. 测试外网访问:")
        print("      使用手机热点测试")
        print(f"      curl http://{self.public_ip}:{self.port}/health")
        
        print("\n🔗 推荐配置方案:")
        if local_ok and internal_ok:
            print("   ⭐ 方案一: 固定公网IP + 端口转发 (推荐)")
            print("   ⭐ 方案二: DDNS动态域名")
            print("   ⭐ 方案三: ngrok内网穿透 (测试)")
        else:
            print("   ❌ 请先解决本地服务问题")
    
    def generate_config_template(self):
        """生成配置模板"""
        print("\n" + "="*60)
        print("📄 云端服务配置模板")
        print("="*60)
        
        print("\n# Zeabur环境变量配置:")
        print("NOTION_API_KEY=your_notion_api_key")
        print("NOTION_DATABASE_ID=your_database_id")
        print("OPENROUTER_API_KEY=your_openrouter_key")
        print(f"LOCAL_RAG_SERVICE_URL=http://{self.public_ip}:{self.port}")
        print("ENABLE_RAG_FALLBACK=true")
        print("RAG_REQUEST_TIMEOUT=10")
        print("RAG_MAX_RETRIES=2")
        print("AUTO_START=true")
        print("CHECK_INTERVAL=120")
        
        print(f"\n# 测试命令:")
        print(f"curl http://{self.internal_ip}:{self.port}/health  # 内网测试")
        print(f"curl http://{self.public_ip}:{self.port}/health   # 公网测试")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 本地RAG服务公网访问配置测试")
        print("="*60)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试目标: {self.internal_ip}:{self.port} → {self.public_ip}:{self.port}")
        
        # 执行测试
        tests = [
            self.test_local_access,
            self.test_internal_access,
            self.test_port_listening,
            self.test_firewall_status,
            self.test_router_connectivity,
            self.test_public_ip_reachability
        ]
        
        for test in tests:
            try:
                test()
                time.sleep(1)  # 测试间隔
            except Exception as e:
                print(f"测试异常: {e}")
        
        # 总结结果
        success_count = sum(1 for r in self.test_results if r['success'])
        total_count = len(self.test_results)
        
        print(f"\n" + "="*60)
        print(f"📊 测试结果总览: {success_count}/{total_count} 项通过")
        print("="*60)
        
        # 显示详细结果
        for result in self.test_results:
            print(f"{result['status']} {result['test']}")
            if not result['success'] and result['suggestion']:
                print(f"   💡 {result['suggestion']}")
        
        # 提供指导
        self.provide_configuration_guide()
        self.generate_config_template()
        
        return success_count >= 3  # 至少3项测试通过才算基本可用

def main():
    """主函数"""
    tester = PublicAccessTester()
    
    print("📋 开始公网访问配置测试...")
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 基础配置已完成！现在可以配置路由器端口转发")
        print(f"📖 详细配置请参考: 本地RAG公网访问配置指南.md")
    else:
        print(f"\n⚠️ 配置尚未完成，请根据上述建议进行配置")
    
    print(f"\n💡 获取帮助:")
    print("   - 查看详细指南: 本地RAG公网访问配置指南.md")
    print("   - 重新运行测试: python3 test_public_access.py")

if __name__ == "__main__":
    main() 