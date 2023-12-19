# 使用官方 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录为 /app
WORKDIR /app

# 将当前目录内容复制到容器的 /app 目录
COPY . /app

# 安装 requirements.txt 中的依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置 Flask 应用变量
ENV FLASK_APP flask_gen_voice.py
ENV FLASK_RUN_HOST 0.0.0.0

# 暴露端口 20000
EXPOSE 20000

# 设置 flask 的环境为开发模式
ENV FLASK_ENV development

# 使用 flask run 命令来启动应用
CMD ["flask", "run", "--port=20000"]
