#!/bin/bash
# REA 环境变量封装：供所有 rea 命令使用
export PATH="/opt/fnm/node-versions/v24.22.1/installation/bin:$PATH"
export JAVA_HOME="$HOME/.local/share/jdk/jdk-21"
export REA_JADX_MCP_JAR="$HOME/.local/share/rea/android/jadx-headless-mcp-0.7.1-all.jar"
export REA_JADX_HEAP_MIB=8192
export REA_JADX_OPERATION_TIMEOUT_MS=600000
export REA_DIR="/home/user/Doubao/chats/38450562512781314/repos/rea"
rea() { node "$REA_DIR/scripts/rea.mjs" "$@"; }
