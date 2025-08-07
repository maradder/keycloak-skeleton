# Build stage
FROM node:22-alpine as builder

WORKDIR /app

# Copy package files
COPY app/package*.json ./
RUN npm ci --only=production

# Copy source code
COPY app/ .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]