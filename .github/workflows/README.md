# GitHub Actions Workflows

This directory contains CI/CD workflows for automatic deployment to AWS Lambda.

## Workflows

### 1. `deploy.yml` - Automatic Deployment
**Trigger**: Push to `main` or `master` branch

Automatically:
- Builds Docker image
- Pushes to Amazon ECR
- Updates Lambda function
- Verifies deployment

### 2. `terraform.yml` - Infrastructure Management
**Trigger**: Changes to `_ci/` directory

Automatically:
- Validates Terraform code
- Plans infrastructure changes
- Applies changes on merge to main
- Comments plan on pull requests

### 3. `test.yml` - Testing
**Trigger**: Every push and pull request

Automatically:
- Runs Python tests
- Validates Docker build
- Lints code (optional)

### 4. `manual-deploy.yml` - Manual Deployment
**Trigger**: Manual workflow dispatch

Allows:
- Deploy to specific environment (prod/staging/dev)
- Choose specific image tag
- Test deployment after update

## Setup Instructions

### 1. Configure AWS Authentication

#### Option A: OIDC (Recommended - No long-term credentials)

1. Create an OIDC provider in AWS IAM:
   ```bash
   aws iam create-open-id-connect-provider \
     --url https://token.actions.githubusercontent.com \
     --client-id-list sts.amazonaws.com \
     --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
   ```

2. Create an IAM role with trust policy:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
         },
         "Action": "sts:AssumeRoleWithWebIdentity",
         "Condition": {
           "StringEquals": {
             "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
           },
           "StringLike": {
             "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_USERNAME/CVchat:*"
           }
         }
       }
     ]
   }
   ```

3. Attach policies to the role:
   - `AmazonEC2ContainerRegistryPowerUser`
   - `AWSLambda_FullAccess` (or custom policy with minimal permissions)

4. Add the role ARN to GitHub Secrets as `AWS_ROLE_ARN`

#### Option B: Access Keys (Simpler but less secure)

1. Create an IAM user with programmatic access
2. Attach necessary policies
3. Add to GitHub Secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

4. Update workflows to use access keys instead of OIDC

### 2. Configure GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions

Add the following secrets:

| Secret Name | Description | Required |
|------------|-------------|----------|
| `AWS_ROLE_ARN` | ARN of the IAM role for OIDC | Yes (Option A) |
| `AWS_ACCESS_KEY_ID` | AWS access key | Yes (Option B) |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Yes (Option B) |
| `GROQ_API_KEY` | Groq API key for LLM | Yes |
| `CONTENT_ORIGIN` | Your website URL (e.g., https://msensat.dev) | Yes |

### 3. Configure Repository Variables (Optional)

Go to Settings → Secrets and variables → Actions → Variables

| Variable Name | Description | Default |
|--------------|-------------|---------|
| `AWS_REGION` | AWS region | us-east-1 |
| `ECR_REPOSITORY` | ECR repository name | cvchat-prod |
| `LAMBDA_FUNCTION` | Lambda function name | cvchat-prod |

### 4. Enable GitHub Actions

1. Go to repository Settings → Actions → General
2. Under "Actions permissions", select "Allow all actions and reusable workflows"
3. Under "Workflow permissions", select "Read and write permissions"

## Usage

### Automatic Deployment

Simply push to the `main` branch:
```bash
git add .
git commit -m "Update application"
git push origin main
```

The `deploy.yml` workflow will automatically:
1. Build your Docker image
2. Push to ECR
3. Update Lambda function
4. Verify deployment

### Infrastructure Changes

Modify files in `_ci/` directory:
```bash
git add _ci/
git commit -m "Update infrastructure"
git push origin main
```

The `terraform.yml` workflow will:
1. Validate Terraform code
2. Show plan in PR comments (if PR)
3. Apply changes on merge to main

### Manual Deployment

1. Go to Actions tab in GitHub
2. Select "Manual Deploy" workflow
3. Click "Run workflow"
4. Choose environment and image tag
5. Click "Run workflow"

## Workflow Diagram

```
┌─────────────────┐
│  Push to main   │
└────────┬────────┘
         │
    ┌────▼────┐
    │  Test   │
    └────┬────┘
         │
    ┌────▼────────┐
    │   Build     │
    │   Docker    │
    └────┬────────┘
         │
    ┌────▼────────┐
    │  Push to    │
    │    ECR      │
    └────┬────────┘
         │
    ┌────▼────────┐
    │   Update    │
    │   Lambda    │
    └────┬────────┘
         │
    ┌────▼────────┐
    │   Verify    │
    └─────────────┘
```

## Monitoring Deployments

### View Workflow Runs
- Go to Actions tab in GitHub
- Click on a workflow run to see details
- View logs for each step

### Check Lambda Logs
```bash
aws logs tail /aws/lambda/cvchat-prod --follow
```

### Get Function URL
```bash
aws lambda get-function-url-config --function-name cvchat-prod
```

## Troubleshooting

### Deployment Fails

1. Check workflow logs in GitHub Actions
2. Verify AWS credentials are correct
3. Check Lambda function exists
4. Verify ECR repository exists

### Permission Errors

1. Verify IAM role/user has correct permissions
2. Check trust policy for OIDC
3. Ensure secrets are correctly set

### Docker Build Fails

1. Check Dockerfile syntax
2. Verify all dependencies in requirements.txt
3. Test build locally:
   ```bash
   docker build -t cvchat:test .
   ```

### Lambda Update Fails

1. Check image size (max 10GB)
2. Verify Lambda timeout settings
3. Check CloudWatch logs for errors

## Best Practices

1. **Use OIDC** instead of long-term access keys
2. **Test in staging** before deploying to production
3. **Use semantic versioning** for image tags
4. **Monitor CloudWatch** logs after deployment
5. **Set up alerts** for deployment failures
6. **Use environments** in GitHub for approval gates

## Advanced Configuration

### Multi-Environment Setup

Create separate environments in GitHub:
1. Settings → Environments
2. Add: `prod`, `staging`, `dev`
3. Configure protection rules
4. Add environment-specific secrets

### Rollback Strategy

To rollback to a previous version:
1. Go to Manual Deploy workflow
2. Enter the previous image tag (e.g., commit SHA)
3. Deploy to production

### Automated Testing

Add integration tests:
```yaml
- name: Integration test
  run: |
    curl -X POST "$FUNCTION_URL/chat" \
      -H "Content-Type: application/json" \
      -d '{"message": "test", "history": []}' \
      | grep -q "response"
```

## Support

For issues with workflows, check:
- GitHub Actions documentation
- AWS Lambda documentation
- Repository issues

Contact: monica@msensat.dev
