#!/bin/bash

# 破局游戏部署脚本
# 用法: ./deploy.sh [版本号]

VERSION=${1:-"v1.1"}
REPO="hbl1104/poju-game"
BRANCH="main"

echo "🎮 开始部署 破局游戏 ${VERSION}..."

# 检查是否在项目根目录
if [ ! -f "src/index.html" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 复制当前版本到根目录
cp src/index.html index.html

# 提交到GitHub
git add index.html
git commit -m "Deploy ${VERSION}: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin ${BRANCH}

if [ $? -eq 0 ]; then
    echo "✅ 部署成功!"
    echo "🔗 访问: https://hbl1104.github.io/poju-game/"
else
    echo "❌ 部署失败"
    exit 1
fi
