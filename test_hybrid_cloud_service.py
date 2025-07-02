#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
混合架构云端服务测试脚本
验证Zeabur部署前的准备工作
"""

import os
import sys
import subprocess
import importlib.util
import requests
import json
import time
from datetime import datetime

class HybridCloudServiceTester:
    """混合架构云端服务测试器"""
    
    def __init__(self):
        self.test_results = []
        self.deploy_ready = True
        self.zeabur_deploy_path = "zeabur_hybrid_deploy"
        
    def log_result(self, test_name, success, message, suggestion=""):
        """记录测试结果"""
        status = "✅ 通过" if success else "❌ 失败"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "suggestion": suggestion
        })
        if not success:
            self.deploy_ready = False
        print(f"{status} {test_name}: {message}")
        if suggestion and not success:
            print(f"   💡 建议: {suggestion}")
    
    def test_deployment_files(self):
        """测试1: 检查部署文件完整性"""
        print("\n🔍 测试1: 检查部署文件完整性")
        
        required_files = [
            "app.py",
            "cloud_hybrid_main.py", 
            "notion_handler.py",
            "llm_handler.py",
            "template_manager.py",
            "requirements.txt",
            "README.md"
        ]
        
        missing_files = []
        for file in required_files:
            file_path = os.path.join(self.zeabur_deploy_path, file)
            if not os.path.exists(file_path):
                missing_files.append(file)
        
        if missing_files:
            self.log_result(
                "部署文件检查",
                False,
                f"缺少文件: {', '.join(missing_files)}",
                "请确保所有必需文件存在于zeabur_hybrid_deploy目录中"
            )
        else:
            self.log_result(
                "部署文件检查", 
                True,
                f"所有{len(required_files)}个必需文件都存在"
            )
    
    def test_dependencies(self):
        """测试2: 检查轻量化依赖包"""
        print("\n📦 测试2: 检查轻量化依赖包")
        
        try:
            # 读取requirements.txt
            req_file = os.path.join(self.zeabur_deploy_path, "requirements.txt")
            with open(req_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 只检查实际的依赖行（非注释、非空行）
            actual_deps = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    # 提取包名（去掉版本号）
                    pkg_name = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                    actual_deps.append(pkg_name)
            
            # 检查是否包含重型依赖（在实际依赖中）
            heavy_deps = ["torch", "faiss-cpu", "sentence-transformers", "transformers", "numpy"]
            found_heavy = []
            for dep in heavy_deps:
                if dep in actual_deps:
                    found_heavy.append(dep)
            
            # 检查是否包含轻量依赖
            light_deps = ["Flask", "requests", "python-dotenv"]
            missing_light = []
            for dep in light_deps:
                if dep not in actual_deps:
                    missing_light.append(dep)
            
            if found_heavy:
                self.log_result(
                    "依赖包轻量化",
                    False,
                    f"发现重型依赖: {', '.join(found_heavy)}",
                    "移除AI模型相关依赖包以减少云端资源消耗"
                )
            elif missing_light:
                self.log_result(
                    "依赖包轻量化",
                    False,
                    f"缺少必需依赖: {', '.join(missing_light)}",
                    "添加Web框架和HTTP客户端依赖"
                )
            else:
                self.log_result(
                    "依赖包轻量化",
                    True,
                    "依赖包配置正确，已移除重型AI依赖"
                )
                
        except Exception as e:
            self.log_result(
                "依赖包轻量化",
                False,
                f"读取requirements.txt失败: {e}",
                "检查requirements.txt文件是否存在和格式是否正确"
            )
    
    def test_module_imports(self):
        """测试3: 测试模块导入"""
        print("\n🔧 测试3: 测试模块导入")
        
        # 临时添加zeabur_deploy_path到Python路径
        sys.path.insert(0, self.zeabur_deploy_path)
        
        modules_to_test = [
            ("cloud_hybrid_main", "HybridCloudScheduler"),
            ("notion_handler", "NotionHandler"),
            ("llm_handler", "LLMHandler"),
            ("template_manager", "TemplateManager")
        ]
        
        all_imports_ok = True
        import_results = []
        
        for module_name, class_name in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, class_name):
                    import_results.append(f"✅ {module_name}.{class_name}")
                else:
                    import_results.append(f"❌ {module_name}.{class_name} (类不存在)")
                    all_imports_ok = False
            except ImportError as e:
                import_results.append(f"❌ {module_name} (导入失败: {e})")
                all_imports_ok = False
        
        # 移除临时路径
        sys.path.remove(self.zeabur_deploy_path)
        
        self.log_result(
            "模块导入测试",
            all_imports_ok,
            f"导入结果:\n   " + "\n   ".join(import_results),
            "修复导入错误或缺失的依赖包" if not all_imports_ok else ""
        )
    
    def test_scheduler_initialization(self):
        """测试4: 测试调度器初始化"""
        print("\n⚙️ 测试4: 测试调度器初始化")
        
        # 设置测试环境变量
        test_env = {
            "NOTION_API_KEY": "test_key",
            "NOTION_DATABASE_ID": "test_db_id",
            "OPENROUTER_API_KEY": "test_openrouter_key",
            "LOCAL_RAG_SERVICE_URL": "http://localhost:8001"
        }
        
        for key, value in test_env.items():
            os.environ[key] = value
        
        try:
            sys.path.insert(0, self.zeabur_deploy_path)
            from cloud_hybrid_main import HybridCloudScheduler
            
            # 尝试创建调度器实例
            scheduler = HybridCloudScheduler()
            
            # 检查关键属性
            required_attrs = ["config", "notion_handler", "llm_handler", "template_manager"]
            missing_attrs = []
            for attr in required_attrs:
                if not hasattr(scheduler, attr):
                    missing_attrs.append(attr)
            
            if missing_attrs:
                self.log_result(
                    "调度器初始化",
                    False,
                    f"调度器缺少属性: {', '.join(missing_attrs)}",
                    "检查HybridCloudScheduler类的__init__方法"
                )
            else:
                self.log_result(
                    "调度器初始化",
                    True,
                    "调度器初始化成功，所有组件就绪"
                )
                
        except Exception as e:
            self.log_result(
                "调度器初始化",
                False,
                f"初始化失败: {e}",
                "检查配置和依赖包是否正确"
            )
        finally:
            # 清理环境变量和路径
            for key in test_env.keys():
                os.environ.pop(key, None)
            if self.zeabur_deploy_path in sys.path:
                sys.path.remove(self.zeabur_deploy_path)
    
    def test_local_rag_connection(self):
        """测试5: 测试本地RAG连接"""
        print("\n🔗 测试5: 测试本地RAG连接")
        
        local_rag_url = "http://127.0.0.1:8001"
        
        try:
            # 检查本地RAG健康状态
            response = requests.get(f"{local_rag_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get("status") == "healthy":
                    self.log_result(
                        "本地RAG连接",
                        True,
                        f"本地RAG服务运行正常 (版本: {health_data.get('version', 'unknown')})"
                    )
                else:
                    self.log_result(
                        "本地RAG连接",
                        False,
                        "本地RAG服务响应异常",
                        "检查本地RAG服务状态"
                    )
            else:
                self.log_result(
                    "本地RAG连接",
                    False,
                    f"连接失败: HTTP {response.status_code}",
                    "确保本地RAG服务正在运行在端口8001"
                )
                
        except requests.exceptions.ConnectionError:
            self.log_result(
                "本地RAG连接",
                False,
                "无法连接到本地RAG服务",
                "启动本地RAG服务: bash 启动RAG后台服务.sh"
            )
        except Exception as e:
            self.log_result(
                "本地RAG连接",
                False,
                f"连接测试失败: {e}",
                "检查网络和服务状态"
            )
    
    def test_flask_app(self):
        """测试6: 测试Flask应用"""
        print("\n🌐 测试6: 测试Flask应用")
        
        try:
            sys.path.insert(0, self.zeabur_deploy_path)
            from cloud_hybrid_main import app
            
            # 检查Flask应用路由
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append(f"{rule.rule} ({', '.join(rule.methods)})")
            
            expected_routes = ["/health", "/start", "/stop", "/status"]
            missing_routes = []
            for route in expected_routes:
                found = any(route in r for r in routes)
                if not found:
                    missing_routes.append(route)
            
            if missing_routes:
                self.log_result(
                    "Flask应用测试",
                    False,
                    f"缺少路由: {', '.join(missing_routes)}",
                    "检查Flask路由定义"
                )
            else:
                self.log_result(
                    "Flask应用测试",
                    True,
                    f"Flask应用正常，包含{len(routes)}个路由"
                )
                
        except Exception as e:
            self.log_result(
                "Flask应用测试",
                False,
                f"Flask应用测试失败: {e}",
                "检查Flask应用定义和依赖"
            )
        finally:
            if self.zeabur_deploy_path in sys.path:
                sys.path.remove(self.zeabur_deploy_path)
    
    def generate_deployment_guide(self):
        """生成部署指南"""
        print("\n📋 生成部署指南")
        
        guide = f"""
# 🚀 Zeabur部署指南

## 📊 测试结果总览
测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
部署就绪: {"✅ 是" if self.deploy_ready else "❌ 否"}

"""
        
        for result in self.test_results:
            guide += f"- {result['status']} {result['test']}: {result['message']}\n"
        
        guide += f"""

## 🌐 Zeabur部署步骤

### 1. 准备代码仓库
```bash
# 进入部署目录
cd zeabur_hybrid_deploy

# 初始化Git仓库（如果需要）
git init
git add .
git commit -m "混合架构云端服务部署"

# 推送到GitHub/GitLab
git remote add origin YOUR_REPO_URL
git push -u origin main
```

### 2. 创建Zeabur项目
1. 访问 https://dash.zeabur.com
2. 点击 "New Project"
3. 选择 "Git Repository"
4. 连接你的代码仓库

### 3. 配置环境变量
在Zeabur项目设置中添加：

```env
# 必需配置
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_database_id
OPENROUTER_API_KEY=your_openrouter_key

# 混合架构配置
LOCAL_RAG_SERVICE_URL=http://YOUR_LOCAL_IP:8001
ENABLE_RAG_FALLBACK=true
RAG_FALLBACK_MESSAGE=本地知识库暂时不可用，已采用基础模式处理

# 可选配置
AUTO_START=true
CHECK_INTERVAL=120
```

### 4. 本地RAG服务配置
确保你的本地RAG服务：
- 正在运行在端口8001
- 可以从公网访问（使用固定IP或DDNS）
- 防火墙已开放8001端口

### 5. 部署和验证
1. Zeabur会自动检测app.py并开始部署
2. 部署完成后访问健康检查: https://your-app.zeabur.app/health
3. 检查系统状态: https://your-app.zeabur.app/status

## 🔧 故障排除

如果部署失败，检查：
1. 环境变量是否配置完整
2. 代码是否成功推送到仓库
3. requirements.txt格式是否正确
4. 本地RAG服务是否可从公网访问

## 📞 获得帮助

如有问题请检查：
- 部署日志
- 健康检查API响应
- 本地RAG服务状态
"""

        # 保存部署指南
        with open("zeabur_deployment_guide.md", "w", encoding="utf-8") as f:
            f.write(guide)
        
        print("✅ 部署指南已生成: zeabur_deployment_guide.md")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始混合架构云端服务测试")
        print("=" * 60)
        
        # 运行所有测试
        self.test_deployment_files()
        self.test_dependencies()
        self.test_module_imports()
        self.test_scheduler_initialization()
        self.test_local_rag_connection()
        self.test_flask_app()
        
        # 生成总结
        print("\n" + "=" * 60)
        print("📊 测试结果总结")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        
        print(f"通过测试: {passed}/{total}")
        print(f"部署就绪: {'✅ 是' if self.deploy_ready else '❌ 否'}")
        
        if not self.deploy_ready:
            print("\n❌ 发现问题，请解决后再进行部署:")
            for result in self.test_results:
                if not result['success'] and result['suggestion']:
                    print(f"- {result['test']}: {result['suggestion']}")
        else:
            print("\n🎉 所有测试通过！可以开始Zeabur部署")
        
        # 生成部署指南
        self.generate_deployment_guide()
        
        return self.deploy_ready


if __name__ == "__main__":
    tester = HybridCloudServiceTester()
    deploy_ready = tester.run_all_tests()
    
    if deploy_ready:
        print("\n🚀 下一步: 按照 zeabur_deployment_guide.md 进行云端部署")
    else:
        print("\n🔧 下一步: 解决上述问题后重新运行测试") 