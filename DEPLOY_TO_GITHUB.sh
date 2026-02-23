#!/bin/bash
# Deploy to GitHub Script

echo "🚀 Polymarket Dashboard - GitHub Deployment"
echo "============================================"
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d ".git" ]; then
    echo "❌ Error: Please run this script from the polymarket-dashboard directory"
    exit 1
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git branch -M main
fi

# Get GitHub repository URL
echo "📝 Enter your GitHub repository URL"
echo "   Example: https://github.com/username/polymarket-dashboard.git"
echo "   Or: git@github.com:username/polymarket-dashboard.git"
echo ""
read -p "Repository URL: " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ Error: Repository URL is required"
    exit 1
fi

# Check if remote already exists
if git remote | grep -q "origin"; then
    echo "🔄 Updating remote origin..."
    git remote set-url origin "$REPO_URL"
else
    echo "➕ Adding remote origin..."
    git remote add origin "$REPO_URL"
fi

# Show current status
echo ""
echo "📊 Current git status:"
git status --short

# Ask for confirmation
echo ""
read -p "🤔 Ready to push to GitHub? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "❌ Deployment cancelled"
    exit 0
fi

# Create .env files if they don't exist
echo ""
echo "📝 Setting up environment files..."
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env (please update with your values)"
fi
if [ ! -f "frontend/.env" ]; then
    cp frontend/.env.example frontend/.env
    echo "✅ Created frontend/.env (please update with your values)"
fi

# Ensure files are staged
echo ""
echo "📦 Staging all files..."
git add .

# Check if there are changes to commit
if git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "✅ No new changes to commit"
else
    echo "💾 Committing changes..."
    git commit -m "Update: Prepare for GitHub deployment"
fi

# Push to GitHub
echo ""
echo "🚀 Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully deployed to GitHub!"
    echo ""
    echo "🎉 Next steps:"
    echo "   1. Visit your repository: ${REPO_URL%.git}"
    echo "   2. Update the README with your repository URL"
    echo "   3. Add repository secrets for CI/CD (see GITHUB_DEPLOYMENT.md)"
    echo "   4. Enable GitHub Actions in repository settings"
    echo "   5. Star the repository ⭐"
    echo ""
    echo "📖 For deployment instructions, see GITHUB_DEPLOYMENT.md"
else
    echo ""
    echo "❌ Push failed. Common issues:"
    echo "   - Repository doesn't exist on GitHub (create it first)"
    echo "   - Authentication required (set up SSH keys or personal access token)"
    echo "   - No write access to repository"
    echo ""
    echo "💡 To create a new repository:"
    echo "   1. Go to https://github.com/new"
    echo "   2. Name it 'polymarket-dashboard'"
    echo "   3. Don't initialize with README (we already have one)"
    echo "   4. Run this script again"
fi
