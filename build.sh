#!/bin/bash

set -e  # Exit on error

THEME_DIR="themes/_menus_ttms"
THEME_REPO="https://github.com/anomrac21/_menus_ttms.git"
THEME_BRANCH="master"

# Check if the theme submodule is set up
if [ ! -d "$THEME_DIR" ]; then
  echo "🔧 Theme submodule not found. Adding it..."
  git submodule add -b "$THEME_BRANCH" "$THEME_REPO" "$THEME_DIR"
else
  echo "✅ Theme submodule already exists."
fi

# Initialize and update submodules
echo "📦 Initializing/updating submodules..."
git submodule update --init --recursive

# Pull latest changes from the theme's branch
echo "🔄 Pulling latest from theme repo..."
cd "$THEME_DIR"
git checkout "$THEME_BRANCH"
git pull origin "$THEME_BRANCH"
cd ../../

# Build the Hugo site
echo "🚀 Running Hugo build..."
hugo

