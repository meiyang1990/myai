#!/bin/bash
# generate_code_comment 项目环境一键配置脚本
# 用法: cd generate_code_comment && bash setup.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== generate_code_comment 环境配置 ==="
echo ""

# 1. 检查虚拟环境
if [ -d "venv" ]; then
    echo "✓ 虚拟环境已存在"
else
    echo "→ 创建虚拟环境..."
    python3 -m venv venv
    echo "✓ 虚拟环境创建完成"
fi

# 2. 激活虚拟环境
echo "→ 激活虚拟环境..."
source venv/bin/activate
echo "✓ 已激活: $(which python3)"

# 3. 升级 pip
echo "→ 升级 pip..."
pip install --upgrade pip -q

# 4. 安装依赖
echo "→ 安装项目依赖..."
pip install -r requirements.txt
echo ""
echo "✓ 所有依赖安装完成！"

# 5. 检查环境变量配置
if [ -z "$VOLCENGINE_API_KEY" ] || [ -z "$VOLCENGINE_MODEL_ENDPOINT" ]; then
    echo ""
    echo "⚠ 未检测到大模型相关环境变量，请先设置："
    echo "  export VOLCENGINE_API_KEY=\"your-api-key\""
    echo "  export VOLCENGINE_API_BASE=\"https://ark.cn-beijing.volces.com/api/coding/v3\""
    echo "  export VOLCENGINE_MODEL_ENDPOINT=\"your-endpoint-id\""
    echo ""
    echo "  建议将以上内容添加到 ~/.bashrc 或 ~/.zshrc 中"
    echo "  详细说明请参考 .env.example 文件"
fi

echo ""
echo "=== 配置完成 ==="
echo "后续使用请先激活虚拟环境："
echo "  cd $SCRIPT_DIR && source venv/bin/activate"
echo ""
echo "运行示例："
echo "  python main.py /path/to/your/project --overwrite"
