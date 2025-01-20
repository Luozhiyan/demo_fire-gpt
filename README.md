# 专家评分系统

这是一个基于 Vue 3 + Flask 的专家评分系统，支持文件上传、专家评分等功能。

## 系统要求

### 后端要求
- Python 3.8 或更高版本
- MySQL 数据库

### 前端要求
- Node.js 16.0 或更高版本
- npm 或 yarn 包管理器

## 项目结构
```
demo/
├── backend/           # 后端 Flask 应用
│   ├── database/     # 数据库相关文件
│   ├── routes/       # API 路由
│   ├── utils/        # 工具函数
│   ├── .env.example  # 环境变量模板
│   └── app.py        # 应用入口
├── frontend/         # 前端 Vue 应用
│   ├── src/         # 源代码
│   └── ...
├── case_show/       # 示例文件夹，包含测试用例
└── requirements.txt  # Python 依赖文件
```

## 安装步骤

### 1. 后端设置

1. 创建并激活 Python 虚拟环境（推荐）：
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. 安装 Python 依赖：
```bash
cd backend
pip install -r requirements.txt
```

3. 设置环境变量：
```bash
# 复制环境变量模板
cp .env.example .env
# 然后编辑 .env 文件，填入你的实际配置
```

环境变量说明：
- `DB_HOST`: 数据库主机地址（默认 localhost）
- `DB_PORT`: 数据库端口（默认 3306）
- `DB_USER`: 数据库用户名
- `DB_PASSWORD`: 数据库密码
- `DB_NAME`: 数据库名称
- `FLASK_ENV`: 运行环境（development/production）
- `FLASK_DEBUG`: 是否开启调试模式（1/0）
- `SECRET_KEY`: Flask 密钥，用于会话加密
- `UPLOAD_FOLDER`: 文件上传目录
- `MAX_CONTENT_LENGTH`: 最大上传文件大小（字节）
- `CORS_ORIGINS`: 允许的前端地址

4. 设置数据库：
- 确保 MySQL 服务已启动
- 创建新的数据库
- 使用 `backend/database/init.sql` 初始化数据库结构

### 2. 前端设置

1. 安装前端依赖：
```bash
cd frontend
npm install
```

2. 如果需要，修改前端配置：
- 编辑 `src/config.js` 文件，调整相关配置

## 运行项目

### 启动后端服务：
```bash
cd backend
python app.py
```
后端服务将在 http://localhost:5000 运行

### 启动前端服务：
```bash
cd frontend
npm run dev
```
前端服务将在 http://localhost:5173 运行

## 使用说明

1. 访问 http://localhost:5173 打开前端页面
2. 系统主要功能：
   - 文件上传
   - 专家评分
   - 评分结果查看
   - ...

## 示例文件

项目包含示例案例文件夹 `case_show`，其中包含：
- 宁夏地区案例
- 陕西地区案例

这些示例文件可以用于测试系统功能和熟悉系统操作。

## 常见问题

1. 如果遇到数据库连接问题，请检查：
   - MySQL 服务是否正常运行
   - 数据库连接配置是否正确
   - 数据库用户权限是否足够

2. 如果遇到前端依赖安装问题，可以尝试：
   ```bash
   npm clean-cache --force
   rm -rf node_modules
   npm install
   ```

## 注意事项

- 请确保所有文件的编码格式为 UTF-8
- 建议使用 Chrome 或 Firefox 最新版本浏览器
- 上传文件大小限制为 [您设置的限制大小]

## 开发注意事项

1. 不要提交敏感信息：
   - 确保 `.env` 文件不被提交到版本控制
   - 使用 `.env.example` 作为环境变量模板

2. 依赖管理：
   - 后端：使用 `pip freeze > requirements.txt` 更新依赖
   - 前端：使用 `package.json` 管理依赖

3. 文件上传：
   - 上传文件会保存在 backend/uploads 目录
   - 注意文件大小限制（默认 16MB）

## 技术栈

- 前端：Vue 3 + Element Plus + Vite
- 后端：Flask + MySQL
- 其他：Axios, Vue Router, Pinia
