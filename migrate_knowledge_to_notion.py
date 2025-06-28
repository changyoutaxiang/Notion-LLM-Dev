#!/usr/bin/env python3
"""
知识库迁移脚本：将现有knowledge_base文件夹中的.md文件迁移到Notion知识库
"""

import os
import json
from datetime import datetime
from notion_knowledge_db import NotionKnowledgeDB

class KnowledgeMigration:
    """知识库迁移器"""
    
    def __init__(self, config_file: str = "config.json"):
        """初始化迁移器"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"❌ 配置文件 {config_file} 不存在")
            exit(1)
        except json.JSONDecodeError:
            print(f"❌ 配置文件 {config_file} 格式错误")
            exit(1)
        
        self.notion_kb = NotionKnowledgeDB(self.config)
        self.knowledge_base_path = "knowledge_base"
        
        # 预定义的知识映射配置（适配现有分类体系）
        self.knowledge_mapping = {
            "AI效率中心.md": {
                "title": "AI效率中心部门介绍与AI经理团队建设",
                "category": "AI效率中心",
                "subcategory": "组织架构",
                "keywords": ["AI效率中心", "部门职能", "组织架构", "AI经理", "团队建设", "战略使命"],
                "scenarios": ["部门介绍", "职能咨询", "业务了解", "团队建设咨询"],
                "priority": "高",
                "summary": "AI效率中心的战略定位、核心使命、运作模式，以及AI经理/AIBP团队建设框架和人才培养路径。"
            },
            "业务理解.md": {
                "title": "在线教育业务理解文档",
                "category": "51Talk业务背景",
                "subcategory": "业务流程",
                "keywords": ["业务理解", "在线教育", "用户转化", "课程体系", "中东市场", "1对1外教"],
                "scenarios": ["业务了解", "用户咨询", "流程指导", "市场分析"],
                "priority": "高",
                "summary": "在线教育公司的完整业务模式，包括用户分类、获取渠道、转化漏斗、课程体系和服务机制。"
            }
        }
    
    def run_migration(self):
        """执行完整的迁移流程"""
        print("🚀 开始知识库迁移...")
        
        # 1. 测试连接
        if not self._test_connections():
            print("❌ 连接测试失败，停止迁移")
            return False
        
        # 2. 扫描知识文件
        knowledge_files = self._scan_knowledge_files()
        if not knowledge_files:
            print("❌ 未找到知识文件")
            return False
        
        print(f"📂 找到 {len(knowledge_files)} 个知识文件")
        
        # 3. 执行迁移
        success_count = 0
        for file_path in knowledge_files:
            if self._migrate_single_file(file_path):
                success_count += 1
        
        print(f"\n🎉 迁移完成！成功: {success_count}/{len(knowledge_files)}")
        return success_count == len(knowledge_files)
    
    def _test_connections(self):
        """测试Notion连接"""
        print("🔍 测试Notion连接...")
        
        # 测试基础连接
        success, msg = self.notion_kb.test_connection()
        if not success:
            print(f"❌ 基础连接失败: {msg}")
            return False
        print(f"✅ 基础连接: {msg}")
        
        # 测试知识库连接
        success, msg = self.notion_kb.test_knowledge_database_connection()
        if not success:
            print(f"❌ 知识库连接失败: {msg}")
            return False
        print(f"✅ 知识库连接: {msg}")
        
        return True
    
    def _scan_knowledge_files(self):
        """扫描知识库文件"""
        knowledge_files = []
        
        if not os.path.exists(self.knowledge_base_path):
            print(f"❌ 知识库目录不存在: {self.knowledge_base_path}")
            return knowledge_files
        
        for filename in os.listdir(self.knowledge_base_path):
            if filename.endswith('.md') and filename != '.DS_Store':
                file_path = os.path.join(self.knowledge_base_path, filename)
                if os.path.isfile(file_path):
                    knowledge_files.append(file_path)
        
        return knowledge_files
    
    def _migrate_single_file(self, file_path: str):
        """迁移单个知识文件"""
        filename = os.path.basename(file_path)
        print(f"\n📄 迁移文件: {filename}")
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                print(f"⚠️  文件内容为空，跳过: {filename}")
                return False
            
            # 获取知识映射配置
            config = self.knowledge_mapping.get(filename)
            if not config:
                print(f"⚠️  未找到文件配置，使用默认配置: {filename}")
                config = self._generate_default_config(filename, content)
            
            # 生成优化的内容
            optimized_content = self._optimize_content_for_notion(content, config['summary'])
            
            # 创建知识条目
            knowledge_id = self.notion_kb.create_knowledge_entry(
                title=config['title'],
                category=config['category'],
                keywords=config['keywords'],
                content=optimized_content,
                subcategory=config.get('subcategory'),
                scenarios=config.get('scenarios'),
                priority=config.get('priority', '中'),
                status='启用'
            )
            
            if knowledge_id:
                print(f"✅ 迁移成功: {config['title']}")
                print(f"   📍 知识ID: {knowledge_id[:8]}...")
                print(f"   🏷️  分类: {config['category']}")
                print(f"   🔑 关键词: {', '.join(config['keywords'][:3])}...")
                return True
            else:
                print(f"❌ 迁移失败: {filename}")
                return False
                
        except Exception as e:
            print(f"❌ 迁移文件时出错 {filename}: {e}")
            return False
    
    def _generate_default_config(self, filename: str, content: str):
        """为未配置的文件生成默认配置"""
        # 从文件名生成标题
        title = filename.replace('.md', '').replace('_', ' ').replace('-', ' ')
        
        # 简单的内容分析来确定分类（适配现有分类选项）
        content_lower = content.lower()
        if any(word in content_lower for word in ['AI效率中心', '效率中心', 'AI经理', 'AIBP']):
            category = "AI效率中心"
            subcategory = "组织架构"
        elif any(word in content_lower for word in ['51talk', '业务', '流程', '用户', '产品', '教育']):
            category = "51Talk业务背景"
            subcategory = "业务流程"
        elif any(word in content_lower for word in ['AI', '训练', '培训', '训战营']):
            category = "AI训战营"
            subcategory = "培训资料"
        else:
            category = "51Talk业务背景"  # 默认分类
            subcategory = "基础资料"
        
        # 提取关键词（简单实现）
        keywords = [title]
        if '效率' in content:
            keywords.append('效率')
        if 'AI' in content:
            keywords.append('AI')
        if '业务' in content:
            keywords.append('业务')
        
        return {
            "title": title,
            "category": category,
            "subcategory": subcategory,
            "keywords": keywords,
            "scenarios": ["一般查询", "基础信息"],
            "priority": "中",
            "summary": f"{title}的相关信息和说明。"
        }
    
    def _optimize_content_for_notion(self, content: str, summary: str):
        """优化内容格式以适配Notion"""
        # 构建结构化的知识条目内容
        optimized = f"""# 知识摘要
{summary}

## 详细内容
{content}

## 适用场景说明
此知识条目适用于以下场景：
- 📋 用户咨询相关问题时
- 🔍 需要了解详细信息时
- 💼 业务背景了解时

## 更新记录
- {datetime.now().strftime('%Y-%m-%d')}：从原始文件迁移创建
"""
        
        return optimized
    
    def create_backup(self):
        """创建原始文件备份"""
        print("💾 创建原始文件备份...")
        
        backup_dir = f"knowledge_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            import shutil
            if os.path.exists(self.knowledge_base_path):
                shutil.copytree(self.knowledge_base_path, backup_dir)
                print(f"✅ 备份创建成功: {backup_dir}")
                return backup_dir
            else:
                print("⚠️  知识库目录不存在，跳过备份")
                return None
        except Exception as e:
            print(f"❌ 备份创建失败: {e}")
            return None


def main():
    """主函数"""
    print("🎯 Notion知识库迁移工具")
    print("=" * 50)
    
    # 创建迁移器
    migrator = KnowledgeMigration()
    
    # 询问是否创建备份
    create_backup = input("是否创建原始文件备份？(y/n): ").lower().strip()
    if create_backup in ['y', 'yes', '是']:
        backup_dir = migrator.create_backup()
        if backup_dir:
            print(f"📁 备份位置: {backup_dir}")
    
    # 确认迁移
    confirm = input("\n确认开始迁移？这将在Notion中创建新的知识条目。(y/n): ").lower().strip()
    if confirm not in ['y', 'yes', '是']:
        print("❌ 迁移已取消")
        return
    
    # 执行迁移
    success = migrator.run_migration()
    
    if success:
        print("\n🎉 恭喜！知识库迁移已完成")
        print("📋 下一步建议：")
        print("   1. 检查Notion知识库中的条目")
        print("   2. 完善分类和关键词标签")
        print("   3. 测试知识检索功能")
        print("   4. 更新配置文件中的 enable_new_system 为 true")
    else:
        print("\n❌ 迁移过程中出现错误，请检查日志")


if __name__ == "__main__":
    main() 