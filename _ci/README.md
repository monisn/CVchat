# CVchat AWS Serverless Deployment

This directory contains Terraform configuration to deploy the CVchat application as a serverless application on AWS.

## Architecture

The deployment uses the following AWS services:

- **AWS Lambda**: Runs the FastAPI application in a container
- **Amazon ECR**: Stores the Docker container image
- **AWS Secrets Manager**: Securely stores API keys and sensitive configuration
- **Lambda Function URL**: Provides HTTP endpoint with CORS support
- **CloudWatch Logs**: Stores application logs

## Prerequisites

1. **AWS CLI** configured with appropriate credentials
2. **Terraform** >= 1.0
3. **Docker** for building container images
4. **Groq API Key** for LLM access

## Deployment Steps

### 1. Configure Variables

Copy the example variables file and customize it:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and set your values:
- `groq_api_key`: Your Groq API key
- `content_origin`: Your website URL (e.g., https://msensat.dev)
- `aws_region`: AWS region for deployment
- Other optional configurations

### 2. Initialize Terraform

```bash
cd _ci
terraform init
```

### 3. Review the Plan

```bash
terraform plan
```

### 4. Apply Infrastructure

```bash
terraform apply
```

This will create:
- ECR repository
- Lambda function
- IAM roles and policies
- Secrets Manager secret
- CloudWatch log group
- Lambda Function URL

### 5. Build and Push Docker Image

After Terraform creates the infrastructure, build and push your Docker image:

```bash
# Get ECR login credentials
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build the Docker image
cd ..
docker build -t cvchat-prod .

# Tag the image
docker tag cvchat-prod:latest <ecr-repository-url>:latest

# Push to ECR
docker push <ecr-repository-url>:latest
```

Replace `<account-id>` and `<ecr-repository-url>` with values from Terraform outputs.

### 6. Update Lambda Function

After pushing the image, update the Lambda function:

```bash
aws lambda update-function-code \
  --function-name cvchat-prod \
  --image-uri <ecr-repository-url>:latest
```

### 7. Test the Deployment

Get your Lambda Function URL from Terraform outputs and test:

```bash
curl -X POST https://your-function-url.lambda-url.us-east-1.on.aws/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What experience does Mònica have in Python?",
    "history": []
  }'
```

## Important Notes

### Lambda Limitations

1. **Cold Starts**: First invocation may take 30-60 seconds due to model loading
2. **Timeout**: Maximum 15 minutes (configured to 5 minutes by default)
3. **Memory**: Configured to 3008 MB (maximum) for better performance
4. **Ephemeral Storage**: 2GB for model files and temporary data

### Cost Optimization

- Lambda is billed per request and compute time
- ECR storage is billed per GB-month
- Consider using Lambda provisioned concurrency for production to reduce cold starts
- CloudWatch logs retention is set to 14 days to reduce costs

### Streaming Responses

Lambda Function URLs support response streaming, which is used by the FastAPI StreamingResponse. This allows the chatbot to stream tokens as they're generated.

## Updating the Application

To deploy updates:

1. Make code changes
2. Build new Docker image
3. Push to ECR with a new tag or `:latest`
4. Update Lambda function code:
   ```bash
   aws lambda update-function-code \
     --function-name cvchat-prod \
     --image-uri <ecr-repository-url>:latest
   ```

## Monitoring

View logs in CloudWatch:

```bash
aws logs tail /aws/lambda/cvchat-prod --follow
```

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Note**: This will delete all resources including the ECR repository and stored images.

## Security Considerations

1. **API Keys**: Stored in AWS Secrets Manager, never in code
2. **CORS**: Configured to allow only specified origins
3. **IAM**: Lambda has minimal required permissions
4. **Encryption**: ECR images encrypted at rest with AES256
5. **Secrets Recovery**: 7-day recovery window for deleted secrets

## Troubleshooting

### Lambda Function Not Working

1. Check CloudWatch logs for errors
2. Verify environment variables are set correctly
3. Ensure Docker image was pushed successfully
4. Check Lambda timeout and memory settings

### CORS Errors

1. Verify `content_origin` in terraform.tfvars matches your website
2. Check `allowed_origins` includes all necessary domains
3. Ensure Lambda Function URL CORS configuration is correct

### Cold Start Issues

Consider using Lambda provisioned concurrency:

```hcl
resource "aws_lambda_provisioned_concurrency_config" "app" {
  function_name                     = aws_lambda_function.app.function_name
  provisioned_concurrent_executions = 1
  qualifier                         = aws_lambda_function.app.version
}
```

## Alternative: API Gateway

If you need more control over the API, you can add API Gateway:

1. Create `api_gateway.tf`
2. Configure REST API or HTTP API
3. Add custom domain, throttling, and API keys
4. Update CORS configuration

## Support

For issues or questions, contact monica@msensat.dev
