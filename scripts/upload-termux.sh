#!/bin/sh
current_branch=$(git branch --show-current)
restore_head() {
  git checkout --detach &&
  git reset $current_branch &&
  git checkout $current_branch
}
trap restore_head EXIT

set -e
git checkout --detach
git reset termux-upload
git checkout termux-upload
set +e

git add -A && git commit -m'upload commit'
git push termux termux-upload
