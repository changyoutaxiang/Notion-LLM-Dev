import json
import os
from datetime import datetime

class TemplateManager:
    """提示词模板管理器"""
    
    def __init__(self, template_file="templates.json", notion_handler=None):
        self.template_file = template_file
        self.notion_handler = notion_handler
        self.templates = {}
        self.categories = []
        self.load_templates()
    
    def load_templates(self):
        """加载模板文件"""
        try:
            if os.path.exists(self.template_file):
                with open(self.template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.templates = data.get("templates", {})
                    self.categories = data.get("categories", ["基础", "商业", "技术", "创意", "教育", "生活"])
            else:
                # 如果文件不存在，创建默认模板
                self.create_default_templates()
        except Exception as e:
            print(f"加载模板文件失败: {e}")
            self.create_default_templates()
    
    def save_templates(self):
        """保存模板到文件"""
        try:
            data = {
                "templates": self.templates,
                "categories": self.categories,
                "metadata": {
                    "version": "1.0",
                    "last_updated": datetime.now().isoformat(),
                    "total_templates": len(self.templates)
                }
            }
            
            with open(self.template_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存模板文件失败: {e}")
            return False
    
    def create_default_templates(self):
        """创建默认模板"""
        self.templates = {
            "通用助手": {
                "category": "基础",
                "prompt": "你是一个智能助手，请认真回答用户的问题。请用中文回复。",
                "description": "通用的AI助手，适合日常问答"
            }
        }
        self.categories = ["基础", "商业", "技术", "创意", "教育", "生活"]
        self.save_templates()
    
    def get_all_templates(self):
        """获取所有模板"""
        return self.templates
    
    def get_templates_by_category(self, category):
        """根据分类获取模板"""
        return {name: template for name, template in self.templates.items() 
                if template.get("category") == category}
    
    def get_template(self, name):
        """获取指定模板"""
        return self.templates.get(name)
    
    def add_template(self, name, prompt, category="基础", description=""):
        """添加新模板"""
        if name in self.templates:
            return False, "模板名称已存在"
        
        self.templates[name] = {
            "category": category,
            "prompt": prompt,
            "description": description,
            "created": datetime.now().isoformat()
        }
        
        if category not in self.categories:
            self.categories.append(category)
        
        success = self.save_templates()
        return success, "模板添加成功" if success else "保存失败"
    
    def update_template(self, name, prompt=None, category=None, description=None):
        """更新模板"""
        if name not in self.templates:
            return False, "模板不存在"
        
        template = self.templates[name]
        if prompt is not None:
            template["prompt"] = prompt
        if category is not None:
            template["category"] = category
            if category not in self.categories:
                self.categories.append(category)
        if description is not None:
            template["description"] = description
        
        template["updated"] = datetime.now().isoformat()
        
        success = self.save_templates()
        return success, "模板更新成功" if success else "保存失败"
    
    def delete_template(self, name):
        """删除模板"""
        if name not in self.templates:
            return False, "模板不存在"
        
        del self.templates[name]
        success = self.save_templates()
        return success, "模板删除成功" if success else "保存失败"
    
    def get_categories(self):
        """获取所有分类"""
        return self.categories
    
    def add_category(self, category):
        """添加新分类"""
        if category not in self.categories:
            self.categories.append(category)
            return self.save_templates()
        return True
    
    def sync_from_notion(self):
        """从Notion同步模板到本地"""
        if not self.notion_handler:
            return False, "未配置Notion处理器"
        
        try:
            print("🔄 开始从Notion同步模板...")
            
            # 从Notion获取模板数据
            notion_data = self.notion_handler.get_templates_from_notion()
            
            if not notion_data:
                return False, "从Notion获取模板数据失败"
            
            # 更新本地模板数据
            self.templates = notion_data.get('templates', {})
            notion_categories = notion_data.get('categories', [])
            
            # 合并分类，保持现有分类并添加新的
            for category in notion_categories:
                if category not in self.categories:
                    self.categories.append(category)
            
            # 保存到本地文件
            success = self.save_templates()
            
            if success:
                print(f"✅ 成功同步 {len(self.templates)} 个模板")
                return True, f"同步成功！获取了 {len(self.templates)} 个模板"
            else:
                return False, "保存模板到本地文件失败"
                
        except Exception as e:
            print(f"❌ 同步模板失败: {e}")
            return False, f"同步失败: {e}"
    
    def sync_to_notion(self):
        """将本地模板同步到Notion"""
        if not self.notion_handler:
            return False, "未配置Notion处理器"
        
        try:
            print("🔄 开始向Notion同步模板...")
            
            success_count = 0
            failed_templates = []
            
            for name, template_data in self.templates.items():
                success = self.notion_handler.sync_template_to_notion(name, template_data)
                if success:
                    success_count += 1
                else:
                    failed_templates.append(name)
            
            if failed_templates:
                return False, f"同步完成：成功 {success_count} 个，失败 {len(failed_templates)} 个\n失败的模板：{', '.join(failed_templates)}"
            else:
                return True, f"同步成功！上传了 {success_count} 个模板到Notion"
                
        except Exception as e:
            print(f"❌ 同步模板到Notion失败: {e}")
            return False, f"同步失败: {e}"
    
    def auto_sync_from_notion_if_empty(self):
        """如果本地模板为空，自动从Notion同步"""
        if len(self.templates) == 0 and self.notion_handler:
            print("📥 检测到本地模板库为空，尝试从Notion自动同步...")
            success, message = self.sync_from_notion()
            if success:
                print(f"✅ 自动同步成功: {message}")
            else:
                print(f"❌ 自动同步失败: {message}")
            return success
        return True
 