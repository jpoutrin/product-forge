---
name: AWS Cloud Services
description: AWS best practices for IAM, EC2, S3, RDS, Lambda, ECS/EKS, and other services
version: 1.0.0
triggers:
  - aws
  - amazon web services
  - ec2
  - s3
  - lambda
  - iam
  - rds
  - eks
  - ecs
  - cloudformation
  - dynamodb
  - sqs
  - sns
---

# AWS Cloud Services Skill

This skill automatically activates when working with AWS services to ensure security best practices, cost optimization, and proper architecture patterns.

## Core Principle

**SECURE, SCALABLE, COST-EFFECTIVE AWS**

```
❌ Overly permissive IAM, unencrypted data, single-AZ deployments
✅ Least privilege IAM, encryption everywhere, multi-AZ resilience
```

## IAM Best Practices

```
AWS IAM SECURITY
════════════════════════════════════════════════════════════

PRINCIPLE OF LEAST PRIVILEGE
├── Grant minimum permissions needed
├── Use conditions to restrict access
├── Prefer managed policies over inline
└── Regular access reviews

IDENTITY PATTERNS
├── Human users → IAM Identity Center (SSO)
├── Applications → IAM Roles (not access keys)
├── Cross-account → Assume Role
└── External → OIDC Federation
```

### IAM Policy Examples

```json
// ✅ CORRECT: Specific, conditional permissions
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3BucketAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/uploads/*",
      "Condition": {
        "StringEquals": {
          "aws:PrincipalTag/team": "engineering"
        }
      }
    }
  ]
}

// ❌ WRONG: Overly permissive
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": "*"
    }
  ]
}
```

### Service Role for ECS

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "123456789012"
        },
        "ArnLike": {
          "aws:SourceArn": "arn:aws:ecs:us-east-1:123456789012:*"
        }
      }
    }
  ]
}
```

## Service-Specific Patterns

### S3
```hcl
# Secure S3 bucket configuration
resource "aws_s3_bucket" "secure" {
  bucket = "my-secure-bucket"
}

resource "aws_s3_bucket_versioning" "secure" {
  bucket = aws_s3_bucket.secure.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "secure" {
  bucket = aws_s3_bucket.secure.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "secure" {
  bucket = aws_s3_bucket.secure.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

### Lambda
```python
# Lambda with proper error handling and observability
import json
import boto3
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import validator

logger = Logger()
tracer = Tracer()
metrics = Metrics()

@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def handler(event: dict, context: LambdaContext) -> dict:
    try:
        # Process event
        result = process_event(event)

        metrics.add_metric(name="SuccessfulProcessing", unit="Count", value=1)

        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    except ValidationError as e:
        logger.warning("Validation error", error=str(e))
        return {"statusCode": 400, "body": json.dumps({"error": str(e)})}
    except Exception as e:
        logger.exception("Unexpected error")
        raise
```

### RDS
```hcl
# Secure RDS configuration
resource "aws_db_instance" "main" {
  identifier = "mydb-production"

  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.medium"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id           = aws_kms_key.rds.arn

  db_name  = "myapp"
  username = "admin"
  password = random_password.db.result

  multi_az               = true
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "Mon:04:00-Mon:05:00"

  deletion_protection = true
  skip_final_snapshot = false

  performance_insights_enabled = true
  monitoring_interval          = 60

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
}
```

## Security Checklist

```
📋 AWS Security Checklist

□ IDENTITY
  □ MFA enabled for root and all users
  □ IAM Identity Center for human access
  □ Roles for applications (no access keys)
  □ Regular credential rotation
  □ Access Analyzer enabled

□ NETWORK
  □ VPC with private subnets
  □ Security groups (least privilege)
  □ NACLs where needed
  □ VPC Flow Logs enabled
  □ No public IPs unless required

□ DATA
  □ Encryption at rest (KMS)
  □ Encryption in transit (TLS)
  □ S3 bucket policies reviewed
  □ RDS encryption enabled
  □ Backup strategy defined

□ MONITORING
  □ CloudTrail enabled (all regions)
  □ Config rules configured
  □ GuardDuty enabled
  □ Security Hub enabled
  □ CloudWatch alarms set

□ COMPLIANCE
  □ Tags for cost allocation
  □ Resource naming convention
  □ Terraform state encrypted
  □ Secrets in Secrets Manager
```

## Warning Triggers

Automatically warn when:

1. **Overly permissive IAM**
   > "⚠️ AWS: Use least privilege - avoid `*` in actions/resources"

2. **Unencrypted resources**
   > "⚠️ AWS: Enable encryption for S3/RDS/EBS"

3. **Public access**
   > "⚠️ AWS: Block public access unless explicitly required"

4. **Missing monitoring**
   > "⚠️ AWS: Enable CloudTrail, Config, and GuardDuty"

## Research Sources

- **Primary**: docs.aws.amazon.com
- **Security**: AWS Security Best Practices
- **Well-Architected**: AWS Well-Architected Framework
