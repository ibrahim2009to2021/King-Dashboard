# DigitalOcean Deployment Guide

## Option 1: App Platform (Recommended - Easiest)

1. Go to https://cloud.digitalocean.com/apps
2. Click **Create App**
3. Select **GitHub** and connect your repository
4. Configure:
   - **Branch**: main
   - **Source Directory**: /
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add environment variables in App Settings
6. Click **Deploy**

Cost: ~$5/month (Basic)

## Option 2: Droplet with Docker (More Control)

### Create Droplet

1. Go to https://cloud.digitalocean.com/droplets
2. Create Droplet:
   - **Image**: Docker on Ubuntu 22.04
   - **Plan**: Basic $6/month (1GB RAM)
   - **Region**: Choose closest to your users
   - **Authentication**: SSH Key (recommended)

### Deploy via SSH

```bash
# SSH into your droplet
ssh root@YOUR_DROPLET_IP

# Clone your repo
git clone https://github.com/YOUR_USERNAME/ai-marketing-engine.git
cd ai-marketing-engine

# Create .env file
cp .env.example .env
nano .env  # Add your values

# Build and run
docker-compose up -d web-app

# Check status
docker-compose ps
docker-compose logs -f web-app
```

### Setup Domain & SSL

```bash
# Install certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate
certbot --nginx -d yourdomain.com

# Auto-renew
certbot renew --dry-run
```

### Nginx Config (if not using Docker nginx)

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## GitHub Actions Auto-Deploy

Add this to `.github/workflows/ci-cd.yml` deploy-production job:

```yaml
- name: Deploy to DigitalOcean
  uses: appleboy/ssh-action@master
  with:
    host: ${{ secrets.DROPLET_IP }}
    username: root
    key: ${{ secrets.SSH_PRIVATE_KEY }}
    script: |
      cd /root/ai-marketing-engine
      git pull origin main
      docker-compose down
      docker-compose up -d --build web-app
```

Add these GitHub secrets:
- `DROPLET_IP` - Your droplet's IP address
- `SSH_PRIVATE_KEY` - Your SSH private key

## Monitoring

1. **DigitalOcean Monitoring**: Enable in Droplet settings
2. **Uptime Checks**: Create in DO Control Panel → Monitoring

## Useful Commands

```bash
# View logs
docker-compose logs -f web-app

# Restart app
docker-compose restart web-app

# Update app
git pull && docker-compose up -d --build web-app

# Check disk space
df -h

# Check memory
free -m
```

## Estimated Costs

- **App Platform Basic**: $5/month
- **Droplet (1GB)**: $6/month
- **Managed Database** (optional): $15/month
- **Domain**: ~$12/year

Total: $5-21/month depending on setup
