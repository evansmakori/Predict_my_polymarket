# DigitalOcean Deployment Guide

Complete guide to deploying the Polymarket AI Predictor on DigitalOcean.

## 📋 Table of Contents
1. [DigitalOcean App Platform (Recommended)](#app-platform)
2. [GPU Droplet for ML Training](#gpu-droplet)
3. [Database Options](#database)
4. [Environment Variables](#environment-variables)
5. [Post-Deployment Steps](#post-deployment)

---

## 🚀 Method 1: DigitalOcean App Platform (Recommended)

App Platform is the easiest way to deploy both frontend and backend.

### Step 1: Prerequisites
- DigitalOcean account (sign up at https://cloud.digitalocean.com/)
- GitHub repository connected to DigitalOcean
- Repository: https://github.com/evansmakori/Predict_my_polymarket

### Step 2: Deploy via App Spec

#### Option A: Using Web Console

1. **Go to DigitalOcean App Platform**
   - Navigate to https://cloud.digitalocean.com/apps
   - Click "Create App"

2. **Connect GitHub Repository**
   - Select "GitHub" as source
   - Authorize DigitalOcean to access your repository
   - Select `evansmakori/Predict_my_polymarket`
   - Choose `main` branch

3. **Configure Services**
   
   **Backend Service:**
   - Name: `backend-api`
   - Source Directory: `/backend`
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - HTTP Port: `8000`
   - HTTP Routes: `/api`, `/docs`, `/ws`
   - Instance Size: Professional XS ($12/month)
   
   **Frontend Service:**
   - Name: `frontend`
   - Source Directory: `/frontend`
   - Build Command: `npm ci && npm run build`
   - Output Directory: `dist`
   - HTTP Routes: `/`
   - Instance Size: Basic XXS ($5/month)

4. **Set Environment Variables**
   
   For Backend:
   ```
   API_HOST=0.0.0.0
   API_PORT=8000
   CORS_ORIGINS=${APP_URL}
   DATABASE_URL=sqlite:///./polymarket.db
   TORCH_DEVICE=cpu
   LOG_LEVEL=INFO
   ```
   
   For Frontend:
   ```
   VITE_API_BASE_URL=${backend-api.PUBLIC_URL}
   VITE_WS_BASE_URL=${backend-api.PUBLIC_URL}
   ```

5. **Deploy**
   - Review configuration
   - Click "Create Resources"
   - Wait 5-10 minutes for deployment

#### Option B: Using doctl CLI

```bash
# Install doctl
# macOS
brew install doctl

# Linux
cd ~
wget https://github.com/digitalocean/doctl/releases/download/v1.98.1/doctl-1.98.1-linux-amd64.tar.gz
tar xf doctl-1.98.1-linux-amd64.tar.gz
sudo mv doctl /usr/local/bin

# Authenticate
doctl auth init

# Create app from spec
doctl apps create --spec .do/app.yaml

# Get app ID and monitor deployment
doctl apps list
doctl apps logs <app-id> --follow
```

### Step 3: Verify Deployment

Once deployed, you'll get URLs like:
- **Frontend**: `https://polymarket-ai-predictor-xxxxx.ondigitalocean.app`
- **Backend**: `https://backend-api-xxxxx.ondigitalocean.app`

Test the endpoints:
```bash
# Health check
curl https://backend-api-xxxxx.ondigitalocean.app/health

# API docs
open https://backend-api-xxxxx.ondigitalocean.app/docs

# AI status
curl https://backend-api-xxxxx.ondigitalocean.app/api/ai/status
```

---

## 🎮 Method 2: GPU Droplet for ML Training

For training ML models with GPU acceleration.

### Step 1: Create GPU Droplet

1. **Go to Droplets**
   - Navigate to https://cloud.digitalocean.com/droplets
   - Click "Create Droplet"

2. **Choose Image**
   - Select "Marketplace"
   - Search for "PyTorch GPU"
   - Or use "Ubuntu 22.04 LTS" and install CUDA manually

3. **Choose Plan**
   - Select "GPU Droplets"
   - Recommended: **GPU Basic** ($0.90/hour, ~$648/month)
   - For testing: Use regular droplet ($12/month) without GPU

4. **Choose Region**
   - Select nearest region with GPU availability
   - NYC3, SFO3, or TOR1 typically have GPUs

5. **Authentication**
   - Add your SSH key
   - Or use password authentication

6. **Create Droplet**
   - Hostname: `polymarket-gpu-trainer`
   - Click "Create Droplet"

### Step 2: Setup GPU Droplet

```bash
# SSH into droplet
ssh root@your_droplet_ip

# Update system
apt update && apt upgrade -y

# Install Python and dependencies
apt install -y python3-pip python3-venv git

# Verify NVIDIA GPU
nvidia-smi

# Clone repository
git clone https://github.com/evansmakori/Predict_my_polymarket.git
cd Predict_my_polymarket/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify PyTorch GPU
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Step 3: Train Models on GPU

```bash
# Train all models
python3 train_on_digitalocean_gpu.py --model all --epochs 100

# Or train individually
python3 train_on_digitalocean_gpu.py --model price_predictor --epochs 200
python3 train_on_digitalocean_gpu.py --model anomaly
python3 train_on_digitalocean_gpu.py --model sentiment

# Monitor GPU usage
watch -n 1 nvidia-smi
```

### Step 4: Download Trained Models

```bash
# From your local machine
scp -r root@your_droplet_ip:/root/Predict_my_polymarket/backend/models ./models

# Or use SFTP
sftp root@your_droplet_ip
cd /root/Predict_my_polymarket/backend
get -r models
```

### Step 5: Destroy GPU Droplet (Save Money!)

```bash
# Important: GPU droplets are expensive!
# Destroy after training to avoid charges

# From DigitalOcean web console or:
doctl compute droplet delete <droplet-id>
```

---

## 💾 Method 3: Database Options

### Option 1: SQLite (Default - Included)
- Included with app
- Good for testing
- Limited to single instance

### Option 2: DigitalOcean Managed PostgreSQL
1. **Create Database**
   - Go to https://cloud.digitalocean.com/databases
   - Click "Create Database"
   - Choose PostgreSQL
   - Select plan: Basic ($15/month)

2. **Update Environment Variables**
   ```
   DATABASE_URL=postgresql://user:password@host:25060/polymarket?sslmode=require
   ```

3. **Update Backend Code**
   - Modify `backend/app/core/database.py` to use PostgreSQL instead of DuckDB

---

## 🔧 Environment Variables Reference

### Backend Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_HOST` | API host address | `0.0.0.0` | Yes |
| `API_PORT` | API port | `8000` | Yes |
| `CORS_ORIGINS` | Allowed CORS origins | `*` | Yes |
| `DATABASE_URL` | Database connection string | `sqlite:///./polymarket.db` | Yes |
| `TORCH_DEVICE` | PyTorch device (cpu/cuda) | `cpu` | No |
| `ENABLE_GPU` | Enable GPU features | `false` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `POLYMARKET_API_KEY` | Polymarket API key | - | No |

### Frontend Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `VITE_API_BASE_URL` | Backend API URL | `https://backend-api-xxx.ondigitalocean.app` | Yes |
| `VITE_WS_BASE_URL` | WebSocket URL | `wss://backend-api-xxx.ondigitalocean.app` | Yes |

---

## ✅ Post-Deployment Steps

### 1. Test AI Endpoints

```bash
# Set your backend URL
BACKEND_URL="https://backend-api-xxxxx.ondigitalocean.app"

# Test AI status
curl "$BACKEND_URL/api/ai/status"

# Test health check
curl "$BACKEND_URL/health"

# Test price prediction (replace market_id)
curl "$BACKEND_URL/api/ai/predict/0x123456..."
```

### 2. Monitor Application

```bash
# View logs
doctl apps logs <app-id> --type=run --follow

# Check metrics
doctl apps tier instance-size list
```

### 3. Set Up Custom Domain (Optional)

1. Go to your app in DigitalOcean console
2. Click "Settings" → "Domains"
3. Add custom domain
4. Update DNS records with your domain provider

### 4. Enable HTTPS

- HTTPS is automatic with App Platform
- Free SSL certificates via Let's Encrypt
- Automatic renewal

---

## 💰 Cost Estimation

### App Platform Deployment
- **Backend** (Professional XS): $12/month
- **Frontend** (Basic XXS): $5/month
- **Total**: ~$17/month

### GPU Training (One-time)
- **GPU Droplet** (Basic GPU): $0.90/hour
- **Training Time**: ~1-2 hours
- **One-time Cost**: ~$2

### With Managed Database
- **PostgreSQL** (Basic): +$15/month
- **Total**: ~$32/month

---

## 🐛 Troubleshooting

### Build Failures

**Problem**: Backend build fails with dependency errors
```bash
# Solution: Lock dependency versions
pip freeze > requirements.txt
```

**Problem**: Frontend build fails
```bash
# Solution: Clear npm cache
npm ci --force
```

### Runtime Issues

**Problem**: Backend crashes on startup
```bash
# Check logs
doctl apps logs <app-id> --type=run --tail=100

# Common fixes:
# 1. Check environment variables
# 2. Verify database connectivity
# 3. Check for missing dependencies
```

**Problem**: CORS errors
```bash
# Solution: Update CORS_ORIGINS environment variable
CORS_ORIGINS=https://your-frontend-url.ondigitalocean.app
```

### GPU Issues

**Problem**: CUDA not available
```bash
# Verify GPU
nvidia-smi

# Reinstall PyTorch with CUDA
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

---

## 📚 Additional Resources

- [DigitalOcean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [DigitalOcean GPU Droplets](https://docs.digitalocean.com/products/droplets/gpu/)
- [DigitalOcean Gradient AI Platform](https://docs.digitalocean.com/products/gradient-ai-platform/)
- [doctl CLI Reference](https://docs.digitalocean.com/reference/doctl/)

---

## 🆘 Support

- DigitalOcean Community: https://www.digitalocean.com/community
- GitHub Issues: https://github.com/evansmakori/Predict_my_polymarket/issues
- Documentation: See README.md and DIGITALOCEAN_GPU_SETUP.md
