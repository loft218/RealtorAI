#!/usr/bin/env bash
# =============================================================================
# update_realtorai.sh
# 自动从 GitHub 拉取 RealtorAI 最新代码，安装依赖，并重启 systemd 服务
# 用法：将此脚本放到服务器任意位置（推荐 /usr/local/bin），然后赋可执行权限
#       sudo chmod +x /usr/local/bin/update_realtorai.sh
#       执行：/usr/local/bin/update_realtorai.sh
# =============================================================================

set -euo pipefail

# ==== 配置区，请根据实际修改 ====
# 项目所在目录
PROJECT_DIR="/mnt/RealtorAI"
# Git 分支
GIT_BRANCH="main"
# systemd 服务名
SERVICE_NAME="realtorai"
# ================================

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting update of RealtorAI..."

# 切到项目目录
if [ ! -d "$PROJECT_DIR" ]; then
  echo "Error: project directory '$PROJECT_DIR' does not exist."
  exit 1
fi
cd "$PROJECT_DIR"

# 切换到目标分支并拉取最新
echo "Pulling latest code from GitHub (branch: $GIT_BRANCH)..."
git fetch origin "$GIT_BRANCH"
git reset --hard "origin/$GIT_BRANCH"

# 激活虚拟环境并安装依赖（如果 requirements.txt 有变动）
if [ -f "venv/bin/activate" ]; then
  echo "Activating virtual environment and installing dependencies..."
  # 注意：source 需要在脚本中用 bash 执行才生效
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
  deactivate
else
  echo "Warning: virtual environment not found at venv/, skipping pip install."
fi

# 重启 systemd 服务
echo "Restarting systemd service: $SERVICE_NAME"
sudo systemctl daemon-reload
sudo systemctl restart "$SERVICE_NAME"
sudo systemctl status "$SERVICE_NAME" --no-pager

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Update and restart complete."
