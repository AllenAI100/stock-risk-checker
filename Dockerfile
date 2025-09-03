# 使用 Python 3.11 官方 slim 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 升级 pip
RUN pip install --upgrade pip setuptools wheel

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目文件
COPY . .

# Streamlit 启动命令
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]

