# Texture Deployment Guide

## Quick Start (Digital Ocean / Ubuntu)

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd texture
```

### 2. Run Installation Script
```bash
chmod +x install.sh
./install.sh
```

This will install:
- Node.js 20.x
- pnpm
- Python 3
- uv (Python package manager)
- Caddy web server
- All project dependencies

### 3. Reload Shell
```bash
source ~/.bashrc  # or ~/.zshrc
```

### 4. Start Production Server
```bash
make prod
```

The application will be available at:
- **Local**: http://localhost:8080
- **Server**: http://YOUR_SERVER_IP:8080

---

## Configuration

### Caddyfile

The default `Caddyfile` is configured to listen on `0.0.0.0:8080` (accessible from internet).

**For custom domain with automatic HTTPS:**
```caddy
yourdomain.com {
    root * Kolam/dist
    encode gzip

    handle /api/* {
        reverse_proxy localhost:8000
    }

    handle {
        try_files {path} /index.html
        file_server
    }
}
```

### Firewall Setup

If using UFW firewall:
```bash
sudo ufw allow 8080/tcp
sudo ufw allow 80/tcp   # For HTTP
sudo ufw allow 443/tcp  # For HTTPS (if using domain)
```

---

## Running as System Service (Optional)

### 1. Edit Service File
```bash
nano texture.service
```

Update:
- `User=YOUR_USERNAME` → Your actual username
- `WorkingDirectory=/path/to/texture` → Actual path

### 2. Install Service
```bash
sudo cp texture.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable texture
sudo systemctl start texture
```

### 3. Check Status
```bash
sudo systemctl status texture
```

### 4. View Logs
```bash
sudo journalctl -u texture -f
```

---

## Manual Commands

### Development Mode
```bash
make start       # Start both servers with hot reload
make stop        # Stop development servers
```

Servers:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

### Production Mode
```bash
make build       # Build frontend only
make prod        # Build + start production servers
make prod-stop   # Stop production servers
```

Application: http://localhost:8080 (or your server IP)

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8080
sudo lsof -i :8080
sudo kill -9 <PID>

# Or stop all
make prod-stop
```

### Caddy Not Starting
```bash
# Check Caddy logs
sudo journalctl -u caddy -f

# Validate Caddyfile
caddy validate --config Caddyfile

# Restart Caddy
caddy stop
caddy start --config Caddyfile
```

### Python Dependencies Issues
```bash
cd Weaver
rm -rf .venv
uv venv
uv sync
```

### Node.js Dependencies Issues
```bash
cd Kolam
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### Check Running Processes
```bash
# Check if backend is running
ps aux | grep uvicorn

# Check if Caddy is running
ps aux | grep caddy

# Check logs
tail -f weaver.log
tail -f caddy.log
```

---

## Environment Variables

### Development (`.env` or `.env.local`)
```bash
VITE_API_URL=http://localhost:8000/api/v1
```

### Production (`.env.production`)
```bash
VITE_API_URL=/api/v1
```

No manual copying needed - build tools handle this automatically.

---

## Security Considerations

### 1. Change Default Port
Update `Caddyfile` and firewall rules.

### 2. Use HTTPS with Domain
Configure Caddyfile with your domain - Caddy handles HTTPS automatically.

### 3. Restrict Backend Access
Backend should only be accessible from localhost (already configured).

### 4. Keep Dependencies Updated
```bash
cd Weaver && uv sync --upgrade
cd Kolam && pnpm update
```

---

## Monitoring

### Check Service Status
```bash
sudo systemctl status texture
```

### View Live Logs
```bash
# Application logs
tail -f weaver.log
tail -f caddy.log

# System logs
sudo journalctl -u texture -f
```

### Resource Usage
```bash
htop
# or
top
```

---

## Backup

Backup these directories:
- `Weaver/app/storage/uploads/` - Uploaded datasets
- `.env` and `.env.production` - Configuration

```bash
tar -czf texture-backup-$(date +%Y%m%d).tar.gz \
    Weaver/app/storage/uploads/ \
    Kolam/.env.production
```

---

## Updates

### Pull Latest Code
```bash
git pull origin main
```

### Rebuild and Restart
```bash
make prod-stop
./install.sh     # If dependencies changed
make prod
```

Or with systemd:
```bash
sudo systemctl restart texture
```
