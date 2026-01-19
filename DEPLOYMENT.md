# CVchat Deployment Checklist

Use this checklist to ensure a smooth deployment to AWS Lambda via GitHub Actions.

## Pre-Deployment Setup

### 1. AWS Infrastructure (One-time)

- [ ] AWS account created and configured
- [ ] AWS CLI installed and configured locally
- [ ] Terraform installed (>= 1.0)
- [ ] Navigate to `_ci/` directory
- [ ] Copy `terraform.tfvars.example` to `terraform.tfvars`
- [ ] Update `terraform.tfvars` with your values:
  - [ ] `groq_api_key`
  - [ ] `content_origin`
  - [ ] `aws_region`
  - [ ] `allowed_origins`
- [ ] Run `terraform init`
- [ ] Run `terraform plan` and review
- [ ] Run `terraform apply` to create infrastructure
- [ ] Note the outputs (ECR URL, Lambda Function URL, etc.)

### 2. GitHub Repository Setup

- [ ] Repository created on GitHub
- [ ] Code pushed to GitHub
- [ ] GitHub Actions enabled in repository settings

### 3. GitHub Secrets Configuration

Choose authentication method:

#### Option A: OIDC (Recommended)
- [ ] Create OIDC provider in AWS IAM
- [ ] Create IAM role with trust policy for GitHub
- [ ] Attach required policies to role:
  - [ ] `AmazonEC2ContainerRegistryPowerUser`
  - [ ] `AWSLambda_FullAccess` (or custom minimal policy)
- [ ] Add `AWS_ROLE_ARN` to GitHub Secrets

#### Option B: Access Keys
- [ ] Create IAM user with programmatic access
- [ ] Attach required policies
- [ ] Add `AWS_ACCESS_KEY_ID` to GitHub Secrets
- [ ] Add `AWS_SECRET_ACCESS_KEY` to GitHub Secrets

#### Application Secrets (Required for both)
- [ ] Add `GROQ_API_KEY` to GitHub Secrets
- [ ] Add `CONTENT_ORIGIN` to GitHub Secrets

### 4. Workflow Configuration

- [ ] Review `.github/workflows/deploy.yml`
- [ ] Update environment variables if needed:
  - [ ] `AWS_REGION`
  - [ ] `ECR_REPOSITORY`
  - [ ] `LAMBDA_FUNCTION`
- [ ] Review `.github/workflows/terraform.yml`
- [ ] Review `.github/workflows/test.yml`

## First Deployment

### Manual First Deploy (Recommended)

- [ ] Ensure all infrastructure is created via Terraform
- [ ] Build Docker image locally:
  ```bash
  docker build -t cvchat:test .
  ```
- [ ] Test Docker image locally:
  ```bash
  docker run -p 8000:8000 -e GROQ_API_KEY=xxx -e CONTENT_ORIGIN=xxx cvchat:test
  ```
- [ ] Login to ECR:
  ```bash
  aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
  ```
- [ ] Tag and push image:
  ```bash
  docker tag cvchat:test <ecr-url>:latest
  docker push <ecr-url>:latest
  ```
- [ ] Update Lambda function:
  ```bash
  aws lambda update-function-code --function-name cvchat-prod --image-uri <ecr-url>:latest
  ```
- [ ] Wait for update to complete:
  ```bash
  aws lambda wait function-updated --function-name cvchat-prod
  ```
- [ ] Get Lambda Function URL:
  ```bash
  aws lambda get-function-url-config --function-name cvchat-prod
  ```
- [ ] Test the endpoint:
  ```bash
  curl -X POST <function-url>/chat -H "Content-Type: application/json" -d '{"message":"test","history":[]}'
  ```

### Automatic Deploy via GitHub Actions

- [ ] Push code to `main` branch:
  ```bash
  git add .
  git commit -m "Initial deployment"
  git push origin main
  ```
- [ ] Go to GitHub Actions tab
- [ ] Watch the deployment workflow run
- [ ] Check for any errors in the logs
- [ ] Verify deployment completed successfully

## Post-Deployment Verification

- [ ] Check Lambda function status in AWS Console
- [ ] View CloudWatch logs:
  ```bash
  aws logs tail /aws/lambda/cvchat-prod --follow
  ```
- [ ] Test the API endpoint:
  ```bash
  curl -X POST <function-url>/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "What experience does Mònica have in Python?", "history": []}'
  ```
- [ ] Verify CORS headers are correct
- [ ] Test from your website (msensat.dev)
- [ ] Check response streaming works correctly
- [ ] Monitor Lambda metrics in CloudWatch:
  - [ ] Invocations
  - [ ] Duration
  - [ ] Errors
  - [ ] Throttles

## Ongoing Maintenance

### Regular Updates

- [ ] Make code changes
- [ ] Test locally
- [ ] Commit and push to `main`
- [ ] Monitor GitHub Actions workflow
- [ ] Verify deployment in AWS
- [ ] Test the updated endpoint

### Infrastructure Updates

- [ ] Modify Terraform files in `_ci/`
- [ ] Run `terraform plan` locally
- [ ] Review changes
- [ ] Commit and push
- [ ] Monitor Terraform workflow in GitHub Actions
- [ ] Verify infrastructure changes in AWS Console

### Monitoring

- [ ] Set up CloudWatch alarms for:
  - [ ] Lambda errors
  - [ ] Lambda duration (timeout warnings)
  - [ ] Lambda throttles
- [ ] Review CloudWatch logs regularly
- [ ] Monitor Lambda costs in AWS Cost Explorer
- [ ] Check ECR storage usage

### Security

- [ ] Rotate AWS credentials periodically
- [ ] Review IAM permissions regularly
- [ ] Update dependencies in `requirements.txt`
- [ ] Scan Docker images for vulnerabilities
- [ ] Review CloudWatch logs for suspicious activity

## Troubleshooting Checklist

### Deployment Fails

- [ ] Check GitHub Actions logs
- [ ] Verify AWS credentials are valid
- [ ] Check IAM permissions
- [ ] Verify Lambda function exists
- [ ] Check ECR repository exists
- [ ] Review CloudWatch logs

### Lambda Function Errors

- [ ] Check CloudWatch logs
- [ ] Verify environment variables
- [ ] Check Secrets Manager values
- [ ] Test Docker image locally
- [ ] Verify Lambda timeout settings
- [ ] Check Lambda memory settings

### API Not Responding

- [ ] Verify Lambda Function URL is correct
- [ ] Check CORS configuration
- [ ] Test with curl directly
- [ ] Check Lambda function status
- [ ] Review CloudWatch logs
- [ ] Verify network connectivity

## Rollback Procedure

If deployment fails:

1. [ ] Identify last working commit/image tag
2. [ ] Go to GitHub Actions → Manual Deploy workflow
3. [ ] Select environment: `prod`
4. [ ] Enter previous image tag (commit SHA)
5. [ ] Run workflow
6. [ ] Verify rollback successful
7. [ ] Investigate and fix the issue
8. [ ] Redeploy when ready

## Cost Monitoring

- [ ] Set up AWS Budget alerts
- [ ] Monitor Lambda invocations
- [ ] Check ECR storage costs
- [ ] Review CloudWatch Logs storage
- [ ] Optimize Lambda memory/timeout if needed

## Documentation

- [ ] Update README.md with deployment info
- [ ] Document any custom configurations
- [ ] Keep this checklist updated
- [ ] Document troubleshooting steps for common issues

---

**Last Updated**: 2026-01-21
**Maintained By**: monica@msensat.dev
