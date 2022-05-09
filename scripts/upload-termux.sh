#!/bin/sh
set -e

current_branch=$(git branch --show-current)
restore_head() {
  git checkout --detach
  git reset $current_branch
  git checkout $current_branch
}
trap restore_head EXIT

git checkout --detach
git reset termux-upload
git checkout termux-upload

git add -A
git commit -m'upload commit'
git push termux termux-upload
