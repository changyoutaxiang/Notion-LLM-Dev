# 🚨 云端部署问题 - 快速修复指南

## 问题描述
```
ImportError: libtk8.6.so: cannot open shared object file: No such file or directory
```

## ⚡ 立即修复方案

### 方案1：使用 startserver.py（推荐）

在 Zeabur 部署设置中，修改启动命令为：
```bash
python startserver.py
```

### 方案2：使用 run.sh 脚本

在 Zeabur 部署设置中，修改启动命令为：
```bash
./run.sh
```

### 方案3：使用 Procfile

确保项目根目录有 `Procfile` 文件（已创建），内容：
```
web: python startserver.py
```

### 方案4：使用环境变量（自动检测）

如果必须使用 `main.py`，请设置环境变量：
```bash
CLOUD_DEPLOYMENT=true
```

## 🔧 Zeabur 具体设置步骤

### 步骤1：选择启动方式
在 Zeabur 项目设置中，选择以下任一方式：

#### Docker 部署（推荐）
1. 选择 **Docker** 部署
2. 确保使用项目根目录的 `Dockerfile`

#### Python 部署
1. 选择 **Python** 部署
2. 启动命令设置为：`python startserver.py`

### 步骤2：设置环境变量
```bash
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_database_id
OPENROUTER_API_KEY=your_openrouter_api_key
```

### 步骤3：重新部署
点击 **重新部署** 按钮

## ✅ 验证部署成功

部署完成后，检查以下端点：

1. **健康检查**
   ```
   GET https://your-domain.zeabur.app/health
   ```
   
2. **启动调度器**
   ```
   POST https://your-domain.zeabur.app/start
   ```

3. **检查状态**
   ```
   GET https://your-domain.zeabur.app/status
   ```

## 🔄 故障排除

### 如果仍然有问题：

1. **检查日志**
   - 查看 Zeabur 部署日志
   - 确认是否使用了正确的启动文件

2. **检查文件**
   - 确保 `startserver.py` 文件存在
   - 确保 `Dockerfile` 文件存在

3. **重新推送代码**
   ```bash
   git add .
   git commit -m "fix: 修复云端部署问题"
   git push
   ```

## 📋 部署检查清单

- [ ] 环境变量已设置
- [ ] 启动命令正确
- [ ] 项目文件完整
- [ ] 使用正确的启动文件
- [ ] 健康检查通过

## 🆘 紧急解决方案

如果上述方案都不工作，请：

1. 删除当前部署
2. 重新创建部署
3. 使用以下设置：
   - 启动命令：`python startserver.py`
   - 环境变量：必需的 API 密钥
   - 部署方式：Python 或 Docker

---

💡 **提示**：推荐使用 `startserver.py` 启动，这是专门为云端部署设计的，不包含任何 GUI 相关代码。 