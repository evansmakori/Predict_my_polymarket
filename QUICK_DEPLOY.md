# 🚀 Quick Deployment to DigitalOcean

## Option 1: One-Click Deploy (Easiest)

### Step 1: Click Deploy Button
[![Deploy to DO](https://www.deploytodo.com/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/evansmakori/Predict_my_polymarket/tree/main)

### Step 2: Configure (if prompted)
- **Name**: polymarket-ai-predictor
- **Region**: Choose nearest region
- **Plan**: Professional XS for backend ($12/mo), Basic for frontend ($5/mo)

### Step 3: Done!
Your app will be live in ~5-10 minutes at:
- `https://polymarket-ai-predictor-xxxxx.ondigitalocean.app`

---

## Option 2: Using doctl CLI

```bash
# 1. Install doctl
brew install doctl  # macOS
# or download from https://github.com/digitalocean/doctl/releases

# 2. Authenticate
doctl auth init
# Enter your DigitalOcean API token

# 3. Deploy
doctl apps create --spec .do/app.yaml

# 4. Check status
doctl apps list

# 5. View logs
doctl apps logs <app-id> --follow
```

---

## Option 3: DigitalOcean Web Console

### Step 1: Go to App Platform
Visit: https://cloud.digitalocean.com/apps

### Step 2: Create App
1. Click **"Create App"**
2. Choose **"GitHub"** as source
3. Select repository: `evansmakori/Predict_my_polymarket`
4. Branch: `main`
5. Click **"Next"**

### Step 3: Configure Services

**Backend Service:**
- Source Directory: `/backend`
- Build Command: `pip install -r requirements.txt`
- Run Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- HTTP Port: `8000`
- Instance Size: **Professional XS** ($12/month)

**Frontend Service:**
- Source Directory: `/frontend`
- Build Command: `npm ci && npm run build`
- Output Directory: `dist`
- Instance Size: **Basic XXS** ($5/month)

### Step 4: Environment Variables

**Backend:**
```
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=${APP_URL}
DATABASE_URL=sqlite:///./polymarket.db
TORCH_DEVICE=cpu
```

**Frontend:**
```
VITE_API_BASE_URL=${backend-api.PUBLIC_URL}
VITE_WS_BASE_URL=${backend-api.PUBLIC_URL}
```

### Step 5: Deploy
Click **"Create Resources"** and wait 5-10 minutes.

---

## 🎮 Train Models on GPU (Optional)

For better AI performance, train models on GPU:

### Step 1: Create GPU Droplet
1. Go to https://cloud.digitalocean.com/droplets
2. Click **"Create Droplet"**
3. Choose **"GPU Basic"** ($0.90/hour)
4. Select **"Ubuntu 22.04 with CUDA"**
5. Choose nearest region

### Step 2: Train Models
```bash
# SSH into droplet
ssh root@your_droplet_ip

# Clone repo
git clone https://github.com/evansmakori/Predict_my_polymarket.git
cd Predict_my_polymarket/backend

# Install dependencies
pip3 install -r requirements.txt

# Train models (takes ~5-10 minutes on GPU)
python3 train_on_digitalocean_gpu.py --model all --epochs 100

# Verify GPU usage
nvidia-smi
```

### Step 3: Download Models
```bash
# From local machine
scp -r root@your_droplet_ip:/root/Predict_my_polymarket/backend/models ./
```

### Step 4: Destroy Droplet (Important!)
```bash
# GPU droplets are expensive - destroy when done
doctl compute droplet delete <droplet-id>
```

---

## ✅ Verify Deployment

Once deployed, test these endpoints:

```bash
# Set your backend URL
export BACKEND_URL="https://backend-api-xxxxx.ondigitalocean.app"

# Test health
curl $BACKEND_URL/health

# Test AI status
curl $BACKEND_URL/api/ai/status

# Test API docs
open $BACKEND_URL/docs

# Test frontend
open https://polymarket-ai-predictor-xxxxx.ondigitalocean.app
```

---

## 💰 Cost Breakdown

### Minimum (No GPU Training)
- Backend: $12/month (Professional XS)
- Frontend: $5/month (Basic XXS)
- **Total: $17/month**

### With GPU Training (One-time)
- GPU Droplet: $0.90/hour × 1-2 hours = ~$2
- **Total First Month: $19**

### Production with Database
- Add PostgreSQL: +$15/month
- **Total: $32/month**

---

## 🐛 Troubleshooting

### Build Failed?
```bash
# Check logs
doctl apps logs <app-id> --type=build

# Common fix: clear cache
# Go to App Settings → Components → Backend → Edit → Clear Build Cache
```

### App Won't Start?
```bash
# Check runtime logs
doctl apps logs <app-id> --type=run --follow

# Verify environment variables
doctl apps spec get <app-id>
```

### CORS Errors?
Update `CORS_ORIGINS` environment variable:
```
CORS_ORIGINS=https://your-frontend-url.ondigitalocean.app
```

---

## 📚 Full Documentation

For detailed instructions, see:
- **DEPLOYMENT_GUIDE.md** - Complete deployment guide
- **DIGITALOCEAN_GPU_SETUP.md** - GPU training guide
- **HACKATHON_SUBMISSION.md** - Project description
- **README.md** - Project overview

---

## 🆘 Need Help?

- Documentation: See files above
- GitHub Issues: https://github.com/evansmakori/Predict_my_polymarket/issues
- DigitalOcean Docs: https://docs.digitalocean.com/products/app-platform/

---

**That's it! Your AI-powered prediction market analyzer is live! 🎉**
