# D&D Note-Taking Tool - Docker Setup Guide

This guide will help you set up the D&D Note-Taking application locally using Docker Compose.

## 🚀 Quick Start

### Prerequisites
- Docker (20.10+)
- Docker Compose (2.0+)
- Git

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd dnd-notes-app
cp .env.example .env
```

### 2. Customize Configuration (Optional)
Edit the `.env` file to change ports, database settings, etc:
```bash
nano .env
```

### 3. Start the Application
```bash
# Start all services
docker-compose up -d

# Or start with logs visible
docker-compose up
```

### 4. Access the Application
- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8001/docs
- **MongoDB**: localhost:27017

### 5. Default Login
- **Username**: admin
- **Password**: admin

## 📋 Configuration Options

### Port Configuration
Change these in your `.env` file:
```env
FRONTEND_PORT=3000      # Web interface
BACKEND_PORT=8001       # API server
MONGO_PORT=27017        # Database
NGINX_PORT=80           # Reverse proxy (optional)
```

### Database Configuration
```env
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=password123
DB_NAME=dnd_notes
```

### Backend URL
```env
# For local development
REACT_APP_BACKEND_URL=http://localhost:8001

# For production with domain
REACT_APP_BACKEND_URL=https://yourdomain.com
```

## 🔧 Advanced Setup Options

### Option 1: Basic Setup (Default)
```bash
docker-compose up -d
```
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- MongoDB: localhost:27017

### Option 2: With Nginx Reverse Proxy
```bash
docker-compose --profile nginx up -d
```
- Application: http://localhost
- All traffic routed through Nginx

### Option 3: Custom Ports
Edit `.env` file:
```env
FRONTEND_PORT=8080
BACKEND_PORT=8081
MONGO_PORT=27018
```
Then:
```bash
docker-compose up -d
```

## 🛠️ Development Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart backend
```

### Update and Rebuild
```bash
# Pull latest changes and rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Management
```bash
# Access MongoDB shell
docker-compose exec mongodb mongosh -u admin -p password123

# Backup database
docker-compose exec mongodb mongodump --username admin --password password123 --authenticationDatabase admin --db dnd_notes --out /backup

# Restore database
docker-compose exec mongodb mongorestore --username admin --password password123 --authenticationDatabase admin --db dnd_notes /backup/dnd_notes
```

## 🐛 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the port
lsof -i :3000

# Change port in .env file
FRONTEND_PORT=3001
```

#### Services Not Starting
```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs backend

# Restart specific service
docker-compose restart backend
```

#### Database Connection Issues
```bash
# Check MongoDB logs
docker-compose logs mongodb

# Reset database
docker-compose down -v
docker-compose up -d
```

#### Frontend Not Loading
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend --no-cache
docker-compose up -d frontend
```

### Health Checks
```bash
# Check if all services are healthy
docker-compose ps

# Test API endpoint
curl http://localhost:8001/api/

# Test frontend
curl http://localhost:3000
```

## 🔒 Security for Production

### 1. Change Default Passwords
```env
MONGO_ROOT_PASSWORD=your-secure-password
ADMIN_PASSWORD=your-admin-password
```

### 2. Enable HTTPS with Nginx
1. Get SSL certificates
2. Place them in `./nginx/ssl/`
3. Uncomment SSL configuration in `nginx.conf`
4. Start with nginx profile

### 3. Use Environment-Specific Settings
```env
NODE_ENV=production
ENVIRONMENT=production
```

## 📂 Project Structure
```
dnd-notes-app/
├── docker-compose.yml          # Main Docker Compose configuration
├── .env.example               # Template environment variables
├── .env                       # Your local configuration
├── backend/
│   ├── Dockerfile            # Backend container setup
│   ├── server.py             # FastAPI application
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── Dockerfile            # Frontend container setup
│   ├── package.json          # Node.js dependencies
│   └── src/                  # React source code
└── nginx/
    └── nginx.conf            # Reverse proxy configuration
```

## 🚀 Deployment Options

### Local Development
```bash
docker-compose up -d
```

### Production Deployment
```bash
# With nginx reverse proxy
docker-compose --profile nginx up -d

# Or with custom configuration
cp .env.example .env.production
# Edit .env.production for production settings
docker-compose --env-file .env.production up -d
```

### Cloud Deployment
The Docker Compose setup works on:
- AWS EC2 with Docker
- Google Cloud Compute Engine
- DigitalOcean Droplets
- Azure Virtual Machines
- Any VPS with Docker support

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Docker and Docker Compose logs
3. Ensure all prerequisites are installed
4. Verify port availability
5. Check firewall settings

For additional help, please check the application logs and Docker Compose documentation.
