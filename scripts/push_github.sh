#!/usr/bin/env bash
# 一键推送到 GitHub：若已安装 gh，可自动建仓并推送；否则根据传入的仓库 URL 添加 remote 并推送。
# 用法：
#   ./scripts/push_github.sh                    # 若已配置 origin，仅执行 git push
#   ./scripts/push_github.sh <仓库名>            # 需已安装 gh，创建公开仓库并推送
#   ./scripts/push_github.sh https://github.com/用户/仓库.git   # 添加 origin 并推送

set -e
cd "$(dirname "$0")/.."

if git remote get-url origin &>/dev/null; then
  echo "已存在 origin，执行推送..."
  git push -u origin main
  echo "推送完成。"
  exit 0
fi

if [ -n "$1" ]; then
  if command -v gh &>/dev/null && [[ ! "$1" =~ ^https?:// ]] && [[ ! "$1" =~ ^git@ ]]; then
    echo "使用 GitHub CLI 创建仓库并推送: $1"
    gh repo create "$1" --public --source=. --remote=origin --push
    echo "已创建并推送。"
    exit 0
  fi
  if [[ "$1" =~ ^https?:// ]] || [[ "$1" =~ ^git@ ]]; then
    echo "添加远程 origin 并推送..."
    git remote add origin "$1"
    git push -u origin main
    echo "推送完成。"
    exit 0
  fi
fi

echo "用法："
echo "  $0                     # 已有 origin 时直接推送"
echo "  $0 <仓库名>            # 需安装 gh，创建公开仓库并推送"
echo "  $0 <仓库完整 URL>       # 添加 origin 并推送"
exit 1
