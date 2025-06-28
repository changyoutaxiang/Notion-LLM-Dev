"""
RAG系统安装脚本
自动化环境配置、依赖安装和初始化设置

功能：
1. 检查系统环境
2. 安装Python依赖
3. 下载和缓存模型
4. 创建必要目录
5. 配置验证
"""

import os
import sys
import json
import subprocess
import platform
import shutil
from pathlib import Path
import urllib.request

def print_banner():
    """打印安装横幅"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                    🚀 RAG智能检索系统安装器                    ║
║                        高性能 Phase 1                        ║
╚═══════════════════════════════════════════════════════════════╝
    """)

def check_system_requirements():
    """检查系统要求"""
    print("🔍 检查系统环境...")
    
    # Python版本检查
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python版本过低: {python_version.major}.{python_version.minor}")
        print("   要求: Python 3.8+")
        return False
    
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 操作系统检查
    os_name = platform.system()
    print(f"💻 操作系统: {os_name} {platform.release()}")
    
    # 内存检查
    try:
        import psutil
        memory_gb = psutil.virtual_memory().total / (1024**3)
        print(f"💾 系统内存: {memory_gb:.1f}GB")
        
        if memory_gb < 4:
            print("⚠️ 内存较少，建议至少4GB用于最佳性能")
        
    except ImportError:
        print("⚠️ 无法检查内存信息 (psutil未安装)")
    
    # GPU检查
    gpu_available = False
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name()
            print(f"🎮 GPU设备: {gpu_name}")
            gpu_available = True
        else:
            print("💻 GPU未检测到，将使用CPU")
    except ImportError:
        print("📦 PyTorch未安装，稍后将安装")
    
    return True

def install_dependencies():
    """安装Python依赖"""
    print("\n📦 安装Python依赖包...")
    
    # 检查requirements_rag.txt是否存在
    req_file = Path("requirements_rag.txt")
    if not req_file.exists():
        print("❌ requirements_rag.txt 文件不存在")
        return False
    
    try:
        # 升级pip
        print("🔄 升级pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # 安装基础科学计算包
        print("🔢 安装基础科学计算包...")
        basic_packages = ["numpy", "scipy", "scikit-learn"]
        subprocess.run([sys.executable, "-m", "pip", "install"] + basic_packages,
                      check=True)
        
        # 安装PyTorch (CPU版本，兼容性更好)
        print("🔥 安装PyTorch...")
        subprocess.run([sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cpu"],
                      check=True)
        
        # 安装其他依赖
        print("📋 安装RAG系统依赖...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_rag.txt"],
                      check=True)
        
        print("✅ 依赖安装完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        print("🔧 故障排除建议:")
        print("1. 检查网络连接")
        print("2. 尝试使用国内镜像: pip install -i https://pypi.tuna.tsinghua.edu.cn/simple")
        print("3. 手动安装: pip install -r requirements_rag.txt")
        return False

def create_directories():
    """创建必要目录"""
    print("\n📁 创建项目目录...")
    
    directories = [
        "model_cache",
        "vector_cache", 
        "cache/embeddings",
        "cache/results",
        "logs",
        "temp"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {dir_path}")
    
    return True

def download_models():
    """下载和缓存模型"""
    print("\n🤖 下载嵌入模型...")
    
    try:
        # 下载中文分词模型
        print("📝 初始化中文分词...")
        import jieba
        # jieba会自动下载词典，这里触发一次
        list(jieba.cut("测试"))
        print("  ✅ jieba中文分词就绪")
        
        # 下载sentence-transformers模型
        print("🧠 下载嵌入模型...")
        from sentence_transformers import SentenceTransformer
        
        # 使用轻量级模型进行测试
        model_name = "shibing624/text2vec-base-chinese"
        print(f"  📥 下载模型: {model_name}")
        
        model = SentenceTransformer(model_name, cache_folder="./model_cache")
        
        # 测试模型
        test_embedding = model.encode(["测试文本"])
        print(f"  ✅ 模型测试成功，向量维度: {test_embedding.shape[1]}")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型下载失败: {e}")
        print("🔧 故障排除建议:")
        print("1. 检查网络连接")
        print("2. 尝试设置HuggingFace镜像")
        print("3. 手动下载模型文件")
        return False

def setup_configuration():
    """设置配置文件"""
    print("\n⚙️ 配置RAG系统...")
    
    config_example = Path("config.example.json")
    config_file = Path("config.json")
    
    if not config_example.exists():
        print("❌ config.example.json 不存在")
        return False
    
    if not config_file.exists():
        print("📝 创建配置文件...")
        shutil.copy(config_example, config_file)
        print("  ✅ 已复制 config.example.json -> config.json")
        print("  ⚠️ 请编辑 config.json 填入真实的Notion配置")
    else:
        print("  ✅ config.json 已存在")
    
    # 验证配置格式
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查RAG配置
        rag_config = config.get('knowledge_search', {}).get('rag_system', {})
        if rag_config.get('enabled', False):
            print("  ✅ RAG系统已启用")
        else:
            print("  ⚠️ RAG系统未启用，请检查配置")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置文件格式错误: {e}")
        return False

def run_tests():
    """运行基础测试"""
    print("\n🧪 运行基础功能测试...")
    
    try:
        # 导入测试
        import numpy as np
        import torch
        import sentence_transformers
        import jieba
        print("  ✅ 核心依赖导入成功")
        
        # 语义搜索基础测试
        from semantic_search import SearchConfig
        config = SearchConfig(
            embedding_model="shibing624/text2vec-base-chinese",
            device="cpu",
            enable_cache=False
        )
        print("  ✅ 语义搜索配置正常")
        
        # 混合检索基础测试
        from hybrid_retrieval import SmartQueryAnalyzer
        analyzer = SmartQueryAnalyzer()
        analysis = analyzer.analyze("测试查询")
        print(f"  ✅ 查询分析正常: {analysis.query_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ 基础测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_next_steps():
    """打印后续步骤"""
    print("\n" + "="*60)
    print("🎉 RAG系统安装完成！")
    print("\n📋 后续步骤:")
    
    print("\n1️⃣ 配置Notion API:")
    print("   - 编辑 config.json")
    print("   - 填入Notion Token和数据库ID")
    print("   - 确认数据库字段配置")
    
    print("\n2️⃣ 运行完整测试:")
    print("   python test_rag_phase1.py")
    
    print("\n3️⃣ 启动系统:")
    print("   python main.py")
    
    print("\n4️⃣ 监控性能:")
    print("   - 查看logs目录下的日志文件")
    print("   - 使用性能监控工具")
    
    print("\n🔧 故障排除:")
    print("   - 查看安装日志")
    print("   - 检查依赖版本兼容性")
    print("   - 参考项目README文档")
    
    print("\n🚀 享受智能检索体验！")

def main():
    """主安装函数"""
    print_banner()
    
    install_steps = [
        ("系统环境检查", check_system_requirements),
        ("安装Python依赖", install_dependencies),
        ("创建项目目录", create_directories),
        ("下载AI模型", download_models),
        ("配置系统设置", setup_configuration),
        ("运行基础测试", run_tests)
    ]
    
    success_count = 0
    total_steps = len(install_steps)
    
    for i, (step_name, step_func) in enumerate(install_steps, 1):
        print(f"\n[{i}/{total_steps}] {step_name}")
        print("-" * 40)
        
        try:
            if step_func():
                success_count += 1
                print(f"✅ {step_name} 完成")
            else:
                print(f"❌ {step_name} 失败")
                break
        except KeyboardInterrupt:
            print(f"\n⚠️ 用户中断安装")
            sys.exit(1)
        except Exception as e:
            print(f"❌ {step_name} 异常: {e}")
            break
    
    if success_count == total_steps:
        print_next_steps()
        return True
    else:
        print(f"\n❌ 安装未完成 ({success_count}/{total_steps} 步骤成功)")
        print("\n🔧 请检查错误信息，解决问题后重新运行安装脚本")
        return False

if __name__ == "__main__":
    main() 