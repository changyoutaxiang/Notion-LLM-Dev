# macOS手动安装ngrok指南

## 🚨 当前问题
macOS安全机制阻止运行下载的ngrok文件

## 🔧 解决步骤

### 方法1: 通过系统偏好设置允许
1. 🍎 点击苹果菜单 → 系统偏好设置 → 安全性与隐私
2. 🔒 点击"通用"标签页
3. 🔍 查找"已阻止使用ngrok"的提示
4. ✅ 点击"仍要打开"按钮
5. 🔄 重新运行: ./ngrok version

### 方法2: 使用官方安装包 (最简单)
1. 🌐 访问: https://ngrok.com/download
2. 📱 注册免费账户
3. 💾 下载"macOS"版本
4. 📦 双击.pkg文件安装
5. ✅ 安装完成后可以直接使用

### 方法3: 终端强制允许
```bash
sudo spctl --master-disable  # 临时禁用Gatekeeper
./ngrok version               # 测试运行
sudo spctl --master-enable   # 重新启用安全保护
```

## 🎯 推荐方案
建议使用方法2 (官方安装包)，最安全且简单
