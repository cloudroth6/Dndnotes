# D&D Note-Taking Tool - Docker Setup Guide

This guide will help you set up the D&D Note-Taking application locally using Docker Compose.

## 🚀 Quick Start

### Prerequisites
- Docker (20.10+)
- Docker Compose (2.0+) or Docker with Compose plugin
- Git

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd Dndnotes-1
cp .env.example .env
```

### 2. One-Command Start
```bash
# Using make (recommended)
make setup

# Or manually
docker-compose up -d
# OR (for newer Docker versions)
docker compose up -d
```

### 3. Access the Application
- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8001/docs
- **MongoDB**: localhost:27017

### 4. Default Login
- **Username**: admin
- **Password**: admin

## 📋 Configuration Options

All configuration is done through the `.env` file. Copy `.env.example` to `.env` and modify as needed.

### Port Configuration
```env
FRONTEND_PORT=3000      # React web interface
BACKEND_PORT=8001       # FastAPI server
MONGO_PORT=27017        # MongoDB database
NGINX_PORT=80           # Reverse proxy (optional)
```

### Database Configuration
```env
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=password123
DB_NAME=dnd_notes
```

### Application Settings
```env
ADMIN_USERNAME=admin    # Default admin username
ADMIN_PASSWORD=admin    # Default admin password
NODE_ENV=development    # development or production
```

### Backend URL
```env
# For local development (default)
REACT_APP_BACKEND_URL=http://localhost:8001

# For production with domain
REACT_APP_BACKEND_URL=https://yourdomain.com
```

## 🔧 Setup Options

### Option 1: Basic Setup (Recommended)
```bash
# Copy environment file
cp .env.example .env

# Start all services
make start
# OR
docker-compose up -d
```
**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- MongoDB: localhost:27017

### Option 2: With Nginx Reverse Proxy
```bash
# Start with nginx
docker-compose --profile nginx up -d
```
**Access:**
- Application: http://localhost (port 80)
- All traffic routed through Nginx

### Option 3: Custom Ports
Edit `.env` file:
```env
FRONTEND_PORT=8080
BACKEND_PORT=8081
MONGO_PORT=27018
```
Then start:
```bash
docker-compose up -d
```

## 🛠️ Available Commands

### Using Make (Recommended)
```bash
make help               # Show all commands
make setup              # Initial setup and start
make start              # Start all services
make stop               # Stop all services
make restart            # Restart all services
make logs               # View all logs
make build              # Rebuild images
make health             # Check service health
make clean              # Clean up containers/volumes
```

### Direct Docker Compose
```bash
# View logs
docker-compose logs -f                # All services
docker-compose logs -f backend        # Backend only
docker-compose logs -f frontend       # Frontend only
docker-compose logs -f mongodb        # Database only

# Restart services
docker-compose restart                # All services
docker-compose restart backend        # Specific service

# Update and rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Database shell access
docker-compose exec mongodb mongosh -u admin -p password123
```

## ✅ Verification Steps

### 1. Check Service Status
```bash
make health
# OR
docker-compose ps
```

### 2. Test Application Access
1. **Frontend**: http://localhost:3000 ✅
2. **Backend API**: http://localhost:8001/docs ✅
3. **Login**: admin / admin ✅

### 3. Expected Results
- All services show "Up" and "healthy" status
- Frontend loads without errors
- Backend API documentation accessible
- Login works with default credentials
- Can create and manage D&D sessions

## 🐛 Troubleshooting

### Service Health Check
```bash
# Quick health check
make health

# Detailed service status
docker-compose ps

# View specific service logs
make logs-backend
make logs-frontend
make logs-mongodb
```

### Common Issues

#### Port Conflicts
```bash
# Check what's using a port
lsof -i :3000

# Change port in .env file
FRONTEND_PORT=3001
```

#### Services Not Starting
```bash
# Check logs for errors
docker-compose logs [service-name]

# Rebuild if needed
make build-no-cache
```

#### Database Connection Issues
```bash
# Reset database
make stop
make clean
make start

# Check MongoDB specifically
docker-compose logs mongodb
```

#### Permission Issues (Linux)
```bash
# Fix Docker permissions
sudo usermod -aG docker $USER
# Log out and back in

# Make scripts executable
chmod +x scripts/*.sh
```

### Fresh Start
```bash
# Complete reset
make clean-all
cp .env.example .env
make setup
```

## 🔒 Production Configuration

### 1. Security Settings
```env
# Change default passwords
MONGO_ROOT_PASSWORD=your-secure-password
ADMIN_PASSWORD=your-admin-password

# Production environment
NODE_ENV=production
ENVIRONMENT=production
```

### 2. Domain Configuration
```env
REACT_APP_BACKEND_URL=https://yourdomain.com
```

### 3. SSL/HTTPS with Nginx
1. Obtain SSL certificates
2. Place in `./nginx/ssl/`
3. Update nginx configuration
4. Start with nginx profile

## 📁 Project Structure
```
Dndnotes-1/
├── docker-compose.yml          # Main Docker configuration
├── .env.example               # Environment template
├── .env                       # Your configuration
├── Makefile                   # Convenient commands
├── backend/                   # Python FastAPI backend
│   ├── Dockerfile
│   ├── server.py
│   └── requirements.txt
├── frontend/                  # React frontend
│   ├── Dockerfile
│   ├── package.json
│   └── src/
├── nginx/                     # Reverse proxy config
│   └── nginx.conf
├── mongo-init/                # Database initialization
│   └── init.js
└── scripts/                   # Setup and utility scripts
    ├── setup.sh
    └── ...
```

## 🚀 Deployment

### Local Development
```bash
make setup
```

### Production Deployment
```bash
# With nginx reverse proxy
docker-compose --profile nginx up -d

# Or with production env file
docker-compose --env-file .env.production up -d
```

### Cloud Platforms
This setup works on:
- AWS EC2
- Google Cloud Compute Engine
- DigitalOcean Droplets
- Azure Virtual Machines
- Any Docker-compatible VPS

## 📞 Need Help?

1. **Check logs**: `make logs`
2. **Verify health**: `make health`
3. **Review this guide**
4. **Ensure Docker/Docker Compose is properly installed**
5. **Verify ports are available**

**Happy adventuring!** 🎲⚔️🧙‍♂️
