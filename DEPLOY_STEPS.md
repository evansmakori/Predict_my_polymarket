# 🚀 Deploy to DigitalOcean - Step by Step

Follow these steps to deploy your app right now!

---

## Quick Option: Run Automated Script

```bash
./DEPLOY_NOW.sh
```

This script will:
1. Install doctl (if needed)
2. Authenticate with DigitalOcean
3. Deploy your app
4. Show you the live URLs

---

## Manual Option: Step-by-Step Commands

### Step 1: Install doctl CLI

```bash
# Download doctl
cd ~
wget https://github.com/digitalocean/doctl/releases/download/v1.98.1/doctl-1.98.1-linux-amd64.tar.gz

# Extract
tar xf doctl-1.98.1-linux-amd64.tar.gz

# Install
sudo mv doctl /usr/local/bin

# Verify
doctl version
```

### Step 2: Get DigitalOcean API Token

1. **Go to**: https://cloud.digitalocean.com/account/api/tokens
2. **Click**: "Generate New Token"
3. **Name**: "Hackathon Deploy"
4. **Scopes**: Read + Write (both checkboxes)
5. **Click**: "Generate Token"
6. **Copy** the token (you won't see it again!)

### Step 3: Authenticate doctl

```bash
doctl auth init
```

When prompted, paste your API token.

### Step 4: Deploy the App

```bash
# Navigate to your project
cd ~/Desktop/Prediction_Markt_Dashboard/polymarket-dashboard

# Create the app on DigitalOcean
doctl apps create --spec .do/app.yaml
```

This will output something like:
```
ID                                  Name                     Default Ingress                           Active Deployment ID
abc123-xyz-789                      polymarket-ai-predictor  https://polymarket-ai-predictor-xxx.on... def456-uvw-123
```

### Step 5: Monitor Deployment

```bash
# Get app ID (from output above)
APP_ID="your-app-id-here"

# Watch logs
doctl apps logs $APP_ID --follow

# Check status
doctl apps get $APP_ID
```

### Step 6: Get Your Live URLs

After 5-10 minutes, run:

```bash
doctl apps get $APP_ID --format DefaultIngress
```

This will show your live URL like:
```
https://polymarket-ai-predictor-xxxxx.ondigitalocean.app
```

---

## Expected Deployment Timeline

| Time | Status |
|------|--------|
| 0 min | App created |
| 1 min | Building backend |
| 2-3 min | Building frontend |
| 4-5 min | Deploying containers |
| 5-10 min | ✅ Live and running! |

---

## Testing Your Deployed App

Once deployed, test these endpoints:

```bash
# Set your backend URL
export BACKEND_URL="https://backend-api-xxxxx.ondigitalocean.app"

# Test health
curl $BACKEND_URL/health

# Test AI status
curl $BACKEND_URL/api/ai/status

# View API docs
open $BACKEND_URL/docs

# View frontend
open https://polymarket-ai-predictor-xxxxx.ondigitalocean.app
```

---

## Cost

**Estimated Monthly Cost**: $17/month
- Backend (Professional XS): $12/month
- Frontend (Basic XXS): $5/month

**First month FREE**: DigitalOcean often provides $200 credit for new accounts

---

## Troubleshooting

### Error: "doctl: command not found"
```bash
# Make sure doctl is in PATH
export PATH=$PATH:/usr/local/bin
# Or reinstall following Step 1
```

### Error: "Unable to authenticate"
- Make sure you copied the full API token
- Token must have Read + Write access
- Try: `doctl auth init` again

### Build Failed
```bash
# Check logs
doctl apps logs $APP_ID --type=build

# Common fix: retry deployment
doctl apps create-deployment $APP_ID
```

### App Won't Start
```bash
# Check runtime logs
doctl apps logs $APP_ID --type=run --follow

# Check app status
doctl apps get $APP_ID
```

---

## Useful Commands

```bash
# List all apps
doctl apps list

# Get app details
doctl apps get $APP_ID

# View logs
doctl apps logs $APP_ID --follow

# View build logs
doctl apps logs $APP_ID --type=build

# Delete app (if needed)
doctl apps delete $APP_ID

# Update app (after code changes)
git push origin main  # Auto-deploys if configured
```

---

## After Deployment

### 1. Save Your URLs

Once deployed, save these URLs:

```bash
# Frontend URL
FRONTEND_URL="https://polymarket-ai-predictor-xxxxx.ondigitalocean.app"

# Backend URL
BACKEND_URL="https://backend-api-xxxxx.ondigitalocean.app"
```

### 2. Update Repository

Add your live URLs to:
- `README.md`
- `HACKATHON_SUBMISSION.md`
- `FINAL_SUMMARY.md`

### 3. Test All Features

- [ ] Homepage loads
- [ ] Can view markets
- [ ] AI predictions work
- [ ] Sentiment analysis works
- [ ] Trading signals work
- [ ] WebSocket updates work

### 4. Take Screenshots

For your demo video and submission:
- Homepage
- AI features in action
- Trading signals
- API docs page

---

## Next: Create Demo Video

With your app deployed, you can now:
1. Record demo video showing live app
2. Include live URLs in video
3. Submit to hackathon!

See `HACKATHON_CHECKLIST.md` for video script.

---

## Need Help?

- **DigitalOcean Docs**: https://docs.digitalocean.com/products/app-platform/
- **doctl Reference**: https://docs.digitalocean.com/reference/doctl/
- **Community**: https://www.digitalocean.com/community

---

**Ready to deploy? Run `./DEPLOY_NOW.sh` or follow the manual steps above!** 🚀
