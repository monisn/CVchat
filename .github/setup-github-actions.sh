#!/bin/bash
# GitHub Actions Setup Script for CVchat AWS Deployment

set -e

echo "🚀 CVchat GitHub Actions Setup"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}⚠️  GitHub CLI (gh) is not installed${NC}"
    echo "Install it from: https://cli.github.com/"
    echo "Or continue manually by adding secrets through GitHub web interface"
    echo ""
fi

echo "This script will help you set up GitHub Actions for automatic deployment."
echo ""

# Get repository info
REPO_OWNER=$(git config --get remote.origin.url | sed -n 's#.*/\([^/]*\)/\([^/]*\)\.git#\1#p')
REPO_NAME=$(git config --get remote.origin.url | sed -n 's#.*/\([^/]*\)/\([^/]*\)\.git#\2#p')

if [ -z "$REPO_OWNER" ] || [ -z "$REPO_NAME" ]; then
    echo "Could not detect repository. Make sure you're in a git repository with a remote."
    exit 1
fi

echo "Repository: $REPO_OWNER/$REPO_NAME"
echo ""

# Function to set secret
set_secret() {
    local secret_name=$1
    local secret_description=$2
    local is_sensitive=${3:-true}
    
    echo -e "${YELLOW}Setting: $secret_name${NC}"
    echo "Description: $secret_description"
    
    if [ "$is_sensitive" = true ]; then
        read -sp "Enter value (hidden): " secret_value
        echo ""
    else
        read -p "Enter value: " secret_value
    fi
    
    if command -v gh &> /dev/null; then
        echo "$secret_value" | gh secret set "$secret_name" -R "$REPO_OWNER/$REPO_NAME"
        echo -e "${GREEN}✓ Secret set successfully${NC}"
    else
        echo "Please add this secret manually in GitHub:"
        echo "Go to: https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions"
        echo "Secret name: $secret_name"
        echo ""
    fi
    echo ""
}

echo "📝 Required GitHub Secrets"
echo "=========================="
echo ""

# AWS Authentication
echo "Choose AWS authentication method:"
echo "1) OIDC (Recommended - No long-term credentials)"
echo "2) Access Keys (Simpler but less secure)"
read -p "Enter choice (1 or 2): " auth_choice

if [ "$auth_choice" = "1" ]; then
    echo ""
    echo "Setting up OIDC authentication..."
    echo ""
    echo "First, create an OIDC provider and IAM role in AWS:"
    echo ""
    echo "1. Create OIDC provider:"
    echo "   aws iam create-open-id-connect-provider \\"
    echo "     --url https://token.actions.githubusercontent.com \\"
    echo "     --client-id-list sts.amazonaws.com \\"
    echo "     --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1"
    echo ""
    echo "2. Create IAM role with trust policy (see .github/workflows/README.md)"
    echo ""
    echo "3. Attach these policies to the role:"
    echo "   - AmazonEC2ContainerRegistryPowerUser"
    echo "   - AWSLambda_FullAccess (or custom minimal policy)"
    echo ""
    read -p "Press Enter when you've created the IAM role..."
    echo ""
    
    set_secret "AWS_ROLE_ARN" "ARN of the IAM role for OIDC (e.g., arn:aws:iam::123456789012:role/GitHubActionsRole)" false
else
    echo ""
    echo "Setting up Access Key authentication..."
    echo ""
    set_secret "AWS_ACCESS_KEY_ID" "AWS Access Key ID" true
    set_secret "AWS_SECRET_ACCESS_KEY" "AWS Secret Access Key" true
fi

# Application secrets
set_secret "GROQ_API_KEY" "Groq API key for LLM access" true
set_secret "CONTENT_ORIGIN" "Your website URL (e.g., https://msensat.dev)" false

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Review the workflows in .github/workflows/"
echo "2. Update environment variables in the workflow files if needed"
echo "3. Push to main branch to trigger automatic deployment"
echo ""
echo "To manually trigger a deployment:"
echo "  gh workflow run manual-deploy.yml"
echo ""
echo "Or go to: https://github.com/$REPO_OWNER/$REPO_NAME/actions"
echo ""
