# Secrets Manager for storing sensitive configuration
resource "aws_secretsmanager_secret" "app_secrets" {
  name                    = "${var.project_name}-${var.environment}-secrets"
  description             = "Secrets for ${var.project_name} application"
  recovery_window_in_days = 7
  
  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-secrets"
      Environment = var.environment
    }
  )
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  
  secret_string = jsonencode({
    GROQ_API_KEY    = var.groq_api_key
    CONTENT_ORIGIN  = var.content_origin
  })
}

# IAM policy for Lambda to read secrets
resource "aws_iam_policy" "lambda_secrets" {
  name        = "${var.project_name}-${var.environment}-lambda-secrets"
  description = "Allow Lambda to read secrets from Secrets Manager"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = aws_secretsmanager_secret.app_secrets.arn
      }
    ]
  })
}
