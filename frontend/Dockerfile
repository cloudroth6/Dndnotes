# Use Node.js 20 Alpine image (required for react-router-dom@7.5.1)
FROM node:20-alpine

# Set environment variables
ENV NODE_ENV=development
ENV CHOKIDAR_USEPOLLING=true
ENV WATCHPACK_POLLING=true

# Install dependencies for better compatibility
RUN apk add --no-cache \
    curl \
    git

# Create non-root user first (before copying files)
RUN addgroup -g 1001 -S nodejs \
    && adduser -S nextjs -u 1001

# Set work directory and change ownership
WORKDIR /app
RUN chown nextjs:nodejs /app

# Switch to non-root user
USER nextjs

# Copy package files (as non-root user)
COPY --chown=nextjs:nodejs package*.json ./
COPY --chown=nextjs:nodejs yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source code (as non-root user)
COPY --chown=nextjs:nodejs . .

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Command to run the application
CMD ["yarn", "start"]
