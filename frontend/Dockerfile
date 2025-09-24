# 构建阶段
ARG NODE_VERSION=18.19.0-alpine
ARG NGINX_VERSION=alpine3.21

# 使用轻量级Node.js镜像构建（可通过ARG自定义）
FROM node:${NODE_VERSION} AS builder

# 设置工作目录
WORKDIR /app

# 复制package.json
COPY package.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 设置环境变量
ENV NODE_ENV=production

# 构建应用
RUN npm run build

# 生产阶段
FROM nginx:alpine AS runner

# 复制nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 复制构建产物到nginx目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 8080

# 添加健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# 启动nginx
ENTRYPOINT ["nginx", "-c", "/etc/nginx/nginx.conf"]
CMD ["-g", "daemon off;"]