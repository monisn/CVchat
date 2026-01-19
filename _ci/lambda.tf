# IAM role for Lambda function
resource "aws_iam_role" "lambda" {
  name = "${var.project_name}-${var.environment}-lambda-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  
  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-lambda-role"
      Environment = var.environment
    }
  )
}

# Attach basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Attach secrets policy
resource "aws_iam_role_policy_attachment" "lambda_secrets" {
  role       = aws_iam_role.lambda.name
  policy_arn = aws_iam_policy.lambda_secrets.arn
}

# Lambda function
resource "aws_lambda_function" "app" {
  function_name = "${var.project_name}-${var.environment}"
  role          = aws_iam_role.lambda.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.app.repository_url}:latest"
  
  memory_size = var.lambda_memory_size
  timeout     = var.lambda_timeout
  
  ephemeral_storage {
    size = var.lambda_ephemeral_storage
  }
  
  environment {
    variables = {
      SECRETS_ARN    = aws_secretsmanager_secret.app_secrets.arn
      CONTENT_ORIGIN = var.content_origin
      USER_AGENT     = "CVchat/1.0"
    }
  }
  
  # Note: This requires the image to be pushed to ECR first
  # Use lifecycle to prevent recreation on every apply
  lifecycle {
    ignore_changes = [image_uri]
  }
  
  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}"
      Environment = var.environment
    }
  )
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.app.function_name}"
  retention_in_days = 14
  
  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-logs"
      Environment = var.environment
    }
  )
}

# Lambda Function URL for direct invocation
resource "aws_lambda_function_url" "app" {
  function_name      = aws_lambda_function.app.function_name
  authorization_type = "NONE"
  
  cors {
    allow_credentials = false
    allow_origins     = concat([var.content_origin], var.allowed_origins)
    allow_methods     = ["POST", "GET", "OPTIONS"]
    allow_headers     = ["content-type", "x-amz-date", "authorization", "x-api-key", "x-amz-security-token"]
    expose_headers    = ["x-amz-request-id"]
    max_age           = 86400
  }
}

# Output Lambda Function URL
output "lambda_function_url" {
  description = "Lambda Function URL"
  value       = aws_lambda_function_url.app.function_url
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.app.function_name
}
