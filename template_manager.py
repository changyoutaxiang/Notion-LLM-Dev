import json
import os
from datetime import datetime

class TemplateManager:
    """提示词模板管理器"""
    
    def __init__(self, template_file="templates.json"):
        self.template_file = template_file
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
    
    def export_templates(self, filename):
        """导出模板到文件"""
        try:
            data = {
                "templates": self.templates,
                "categories": self.categories,
                "exported": datetime.now().isoformat()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True, f"模板已导出到 {filename}"
        except Exception as e:
            return False, f"导出失败: {e}"
    
    def import_templates(self, filename, merge=True):
        """从文件导入模板"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_templates = data.get("templates", {})
            imported_categories = data.get("categories", [])
            
            if not merge:
                # 不合并，直接替换
                self.templates = imported_templates
                self.categories = imported_categories
            else:
                # 合并模式
                conflict_count = 0
                for name, template in imported_templates.items():
                    if name in self.templates:
                        conflict_count += 1
                        # 添加后缀避免冲突
                        new_name = f"{name}_导入"
                        self.templates[new_name] = template
                    else:
                        self.templates[name] = template
                
                # 合并分类
                for category in imported_categories:
                    if category not in self.categories:
                        self.categories.append(category)
            
            success = self.save_templates()
            message = f"导入成功！导入了 {len(imported_templates)} 个模板"
            if merge and conflict_count > 0:
                message += f"，{conflict_count} 个重名模板已添加后缀"
            
            return success, message if success else "保存失败"
            
        except Exception as e:
            return False, f"导入失败: {e}" 