# 协作规范

## 核心原则

**本地工程文件夹与 GitHub 仓库始终保持一致**

## 工作流程

### 1. 修改流程（标准）

```
本地工程文件夹 (/home/ubuntu/projects/poju-game/)
    ↓
进行修改（代码、资源、文档）
    ↓
测试验证
    ↓
提交到 GitHub (git push / ./scripts/deploy.sh)
    ↓
确认线上生效
```

### 2. 禁止操作

- ❌ **禁止**直接在 GitHub 网页上修改文件
- ❌ **禁止**在本地其他地方修改后手动上传到 GitHub
- ❌ **禁止**修改后忘记同步到另一方

### 3. 正确操作

- ✅ **必须**在 `/home/ubuntu/projects/poju-game/` 下修改
- ✅ **必须**修改后执行 `./scripts/deploy.sh` 或 `git push`
- ✅ **必须**确认两边一致后才算完成

## 同步检查清单

每次修改后确认：

- [ ] 本地文件已更新
- [ ] GitHub 仓库已推送
- [ ] GitHub Pages 已生效（等待 1-2 分钟）
- [ ] 在线链接测试正常

## 版本管理

### 版本号规则
- `v1.0` - 初始版本
- `v1.1` - 小更新（视觉优化、bug修复）
- `v2.0` - 大更新（新功能、架构调整）

### 存档规范
每次发布新版本：
1. 复制当前 `src/index.html` 到 `versions/vX.X/index.html`
2. 更新 `docs/changelog.md`
3. 更新 `docs/roadmap.md`（标记已完成项）

## 部署命令

```bash
# 进入工程目录
cd /home/ubuntu/projects/poju-game/

# 方法1：使用部署脚本
./scripts/deploy.sh v1.2

# 方法2：手动 git 操作
git add .
git commit -m "描述修改内容"
git push origin main
```

## 紧急修复

如果发现线上有问题：
1. 立即在本地修复
2. 快速部署
3. 事后补全文档和测试

## 记录存档

此规范已记录到持久记忆中，每次处理「破局」游戏相关任务时会自动加载。
