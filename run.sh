#!/bin/bash

set -e  # 一旦出错就退出
set -u  # 变量未定义时退出

modules_dir="submodules"
updated_submodules=()

# 遍历每一个子模块目录
for sub_dir in "$modules_dir"/*/; do
  # 如果不是目录就跳过
  [ -d "$sub_dir" ] || continue

  sub_name=$(basename "$sub_dir")
  if [ ! -e "$sub_dir/.git" ]; then
    echo -e "\033[1;[33mWarning: '$sub_name' is not a git repository. Skipping.\033[0m"
    continue
  fi
  echo -e "\033[1;[36mChecking $sub_name...\033[0m"

  pushd "$sub_dir" > /dev/null

  git fetch origin
  local_commit=$(git rev-parse HEAD)  
  # 自动适配 main 或 master
  if git show-ref --verify --quiet refs/remotes/origin/main; then
    remote_branch="origin/main"
  else
    remote_branch="origin/master"
  fi
  remote_commit=$(git rev-parse "$remote_branch")

  if [ "$local_commit" != "$remote_commit" ]; then
    git reset --hard "$remote_branch"
    echo -e "\033[1;32m[Updated]\033[0m \033[32m$sub_name has updates.\033[0m"
    updated_submodules+=("$sub_name")
  else
    echo -e "\033[1;90m[Up-to-date]\033[0m \033[90m$sub_name is up to date.\033[0m"
  fi

  popd > /dev/null
done


# 检查是否有更新的子模块
if [ ${#updated_submodules[@]} -gt 0 ]; then
  for sub in "${updated_submodules[@]}"; do
    # 调用 Python 脚本处理子模块
    python3 main.py "$sub"
  done

  # 添加所有更改
  git add .

  # 设置时区并获取当前时间（设置为中国标准时间）
  currentDateTime=$(TZ="Asia/Shanghai" date +"%Y-%m-%d %H:%M:%S")

  # 提交更改
  git commit -m "update node from ${updated_submodules[*]} at $currentDateTime"
  
  currentBranch=$(git rev-parse --abbrev-ref HEAD)
  if [ "$currentBranch" == "main" ]; then
    git push --force
  else
    echo "Current branch is not 'main', skipping push."
  fi
fi
