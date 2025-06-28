#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 RAG智能检索交互式测试界面
直接体验智能搜索功能，无需通过Notion界面
"""

import json
import time
import sys
from notion_knowledge_db import NotionKnowledgeDB

class InteractiveRAGTester:
    def __init__(self):
        self.knowledge_db = None
        self.load_system()
    
    def load_system(self):
        """加载RAG系统"""
        print("🚀 正在启动RAG智能检索系统...")
        print("=" * 50)
        
        try:
            # 加载配置
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 初始化知识库
            self.knowledge_db = NotionKnowledgeDB(config)
            
            print("✅ RAG系统启动成功！")
            print(f"📊 系统配置:")
            print(f"   - 嵌入模型: {config['knowledge_search']['rag_system']['embedding']['model_name']}")
            print(f"   - 搜索模式: {config['knowledge_search']['rag_system']['mode']}")
            print(f"   - 缓存启用: {config['knowledge_search']['rag_system']['search']['enable_caching']}")
            
        except Exception as e:
            print(f"❌ 系统启动失败: {e}")
            sys.exit(1)
    
    def search_knowledge(self, query):
        """执行智能搜索"""
        print(f"🔍 正在搜索: '{query}'")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            # 使用智能搜索
            if hasattr(self.knowledge_db, 'smart_search_knowledge'):
                results = self.knowledge_db.smart_search_knowledge(query, max_results=5)
                search_type = "🧠 智能搜索 (RAG)"
            else:
                # 回退到关键词搜索
                keywords = [query]
                results = self.knowledge_db.search_knowledge_by_keywords(keywords)
                search_type = "🔑 关键词搜索"
            
            search_time = time.time() - start_time
            
            print(f"⚡ 搜索方式: {search_type}")
            print(f"⏱️ 搜索耗时: {search_time:.3f}秒")
            print(f"📋 结果数量: {len(results) if results else 0}")
            print()
            
            if results:
                print("📚 搜索结果:")
                print("=" * 40)
                
                for i, result in enumerate(results, 1):
                    if isinstance(result, dict):
                        title = result.get('title', 'N/A')
                        category = result.get('category', 'N/A')
                        similarity = result.get('similarity_score', 'N/A')
                        
                        print(f"📌 结果 {i}: {title}")
                        print(f"   📁 分类: {category}")
                        if similarity != 'N/A':
                            print(f"   📊 相似度: {similarity:.3f}")
                        
                        # 显示内容片段
                        content = result.get('content', result.get('snippet', ''))
                        if content:
                            lines = content.split('\\n')
                            snippet = ' '.join(lines[:3])[:300]
                            print(f"   📝 内容: {snippet}...")
                        
                        keywords = result.get('keywords', [])
                        if keywords:
                            print(f"   🏷️ 关键词: {', '.join(keywords[:5])}")
                        
                        print()
                    else:
                        print(f"📌 结果 {i}: {str(result)[:200]}...")
                        print()
            else:
                print("❌ 未找到相关结果")
                print("💡 建议:")
                print("   - 尝试使用不同的关键词")
                print("   - 使用更通用的描述")
                print("   - 检查拼写是否正确")
            
        except Exception as e:
            print(f"❌ 搜索出错: {e}")
    
    def show_help(self):
        """显示帮助信息"""
        print("🆘 使用说明:")
        print("=" * 30)
        print("💬 直接输入查询内容，按回车搜索")
        print("📝 查询示例:")
        print("   - AI效率中心的职能是什么")
        print("   - 如何培养AI人才")
        print("   - 在线教育业务模式")
        print("   - 用户转化策略")
        print("   - AIBP团队建设")
        print()
        print("🎯 特殊命令:")
        print("   help  - 显示此帮助")
        print("   quit  - 退出程序")
        print("   exit  - 退出程序")
        print()
    
    def run(self):
        """运行交互式测试"""
        print()
        print("🎉 RAG智能检索系统已就绪！")
        print("💡 输入 'help' 查看使用说明，输入 'quit' 退出")
        print()
        
        while True:
            try:
                query = input("🤔 请输入您的问题: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 感谢使用RAG智能检索系统！")
                    break
                
                if query.lower() in ['help', '帮助', 'h']:
                    self.show_help()
                    continue
                
                print()
                self.search_knowledge(query)
                print()
                
            except KeyboardInterrupt:
                print("\\n\\n👋 用户中断，退出程序")
                break
            except Exception as e:
                print(f"❌ 出现错误: {e}")

def main():
    """主函数"""
    print()
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║              🧠 RAG智能检索系统 - 交互式测试              ║")
    print("║                     Phase 1 演示版本                        ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    
    tester = InteractiveRAGTester()
    tester.run()

if __name__ == "__main__":
    main() 