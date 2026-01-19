output "deployment_info" {
  description = "Deployment information"
  value = {
    region               = var.aws_region
    environment          = var.environment
    lambda_function_url  = aws_lambda_function_url.app.function_url
    ecr_repository_url   = aws_ecr_repository.app.repository_url
    lambda_function_name = aws_lambda_function.app.function_name
    secrets_arn          = aws_secretsmanager_secret.app_secrets.arn
  }
}

output "next_steps" {
  description = "Next steps for deployment"
  value = <<-EOT
    
    Next steps to deploy your application:
    
    1. Build and push Docker image to ECR:
       aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com
       docker build -t ${var.project_name}-${var.environment} ..
       docker tag ${var.project_name}-${var.environment}:latest ${aws_ecr_repository.app.repository_url}:latest
       docker push ${aws_ecr_repository.app.repository_url}:latest
    
    2. Update Lambda function to use the new image:
       aws lambda update-function-code --function-name ${aws_lambda_function.app.function_name} --image-uri ${aws_ecr_repository.app.repository_url}:latest
    
    3. Your API endpoint will be available at:
       ${aws_lambda_function_url.app.function_url}
    
    4. Test the endpoint:
       curl -X POST ${aws_lambda_function_url.app.function_url}chat \
         -H "Content-Type: application/json" \
         -d '{"message": "What experience does Mònica have in Rust?", "history": []}'
  EOT
}
