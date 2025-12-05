---
name: GCP Cloud Services
description: Google Cloud best practices for IAM, GCE, Cloud Storage, Cloud SQL, Cloud Run, GKE, and other services
version: 1.0.0
triggers:
  - gcp
  - google cloud
  - gce
  - cloud storage
  - cloud sql
  - cloud run
  - gke
  - bigquery
  - cloud functions
  - pubsub
  - firebase
---

# GCP Cloud Services Skill

This skill automatically activates when working with Google Cloud Platform services to ensure security best practices, cost optimization, and proper architecture patterns.

## Core Principle

**SECURE, SCALABLE, COST-EFFECTIVE GCP**

```
❌ Primitive roles, unencrypted data, single-zone deployments
✅ Custom roles with least privilege, CMEK encryption, multi-zone resilience
```

## IAM Best Practices

```
GCP IAM SECURITY
════════════════════════════════════════════════════════════

PRINCIPLE OF LEAST PRIVILEGE
├── Prefer predefined roles over primitive
├── Use custom roles for fine-grained control
├── Apply conditions (IAM Conditions)
└── Regular access reviews with Policy Analyzer

IDENTITY PATTERNS
├── Human users → Cloud Identity + IAM
├── Applications → Service Accounts
├── Workload Identity → GKE pods
└── External → Workload Identity Federation
```

### IAM Policy Examples

```hcl
# ✅ CORRECT: Specific permissions with conditions
resource "google_project_iam_binding" "storage_reader" {
  project = var.project_id
  role    = "roles/storage.objectViewer"

  members = [
    "serviceAccount:${google_service_account.app.email}",
  ]

  condition {
    title       = "Only specific bucket"
    description = "Limit access to uploads bucket"
    expression  = "resource.name.startsWith('projects/_/buckets/my-bucket/objects/uploads/')"
  }
}

# Workload Identity for GKE
resource "google_service_account_iam_binding" "workload_identity" {
  service_account_id = google_service_account.app.name
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[${var.namespace}/${var.ksa_name}]",
  ]
}
```

## Service-Specific Patterns

### Cloud Storage
```hcl
resource "google_storage_bucket" "secure" {
  name     = "my-secure-bucket-${var.project_id}"
  location = "US"

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  versioning {
    enabled = true
  }

  encryption {
    default_kms_key_name = google_kms_crypto_key.storage.id
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
}
```

### Cloud Run
```hcl
resource "google_cloud_run_v2_service" "api" {
  name     = "api"
  location = var.region

  template {
    service_account = google_service_account.api.email

    containers {
      image = "gcr.io/${var.project_id}/api:latest"

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }

      env {
        name = "DB_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.db_password.secret_id
            version = "latest"
          }
        }
      }
    }

    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }

    vpc_access {
      connector = google_vpc_access_connector.main.id
      egress    = "PRIVATE_RANGES_ONLY"
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}
```

### BigQuery
```sql
-- Create dataset with CMEK encryption
CREATE SCHEMA IF NOT EXISTS `project.dataset`
OPTIONS (
  location = 'US',
  default_kms_key_name = 'projects/project/locations/us/keyRings/ring/cryptoKeys/key'
);

-- Table with partitioning and clustering
CREATE TABLE `project.dataset.events` (
  event_id STRING NOT NULL,
  user_id STRING,
  event_type STRING,
  event_data JSON,
  created_at TIMESTAMP
)
PARTITION BY DATE(created_at)
CLUSTER BY user_id, event_type
OPTIONS (
  partition_expiration_days = 365,
  require_partition_filter = true
);
```

## Security Checklist

```
📋 GCP Security Checklist

□ IDENTITY
  □ Organization policies configured
  □ Service accounts with minimal roles
  □ Workload Identity for GKE
  □ No user-managed service account keys
  □ IAM Recommender reviewed

□ NETWORK
  □ VPC with private subnets
  □ Firewall rules (least privilege)
  □ Private Google Access enabled
  □ VPC Flow Logs enabled
  □ Cloud NAT for egress

□ DATA
  □ CMEK encryption enabled
  □ Cloud KMS for key management
  □ DLP for sensitive data
  □ Backup strategy defined
  □ Data residency configured

□ MONITORING
  □ Cloud Audit Logs enabled
  □ Security Command Center enabled
  □ Cloud Monitoring alerts
  □ Error Reporting configured
  □ Log-based metrics

□ COMPLIANCE
  □ Labels for cost allocation
  □ Resource naming convention
  □ Terraform state in GCS
  □ Secrets in Secret Manager
```

## Warning Triggers

Automatically warn when:

1. **Primitive IAM roles**
   > "⚠️ GCP: Use predefined or custom roles instead of primitive (Owner/Editor/Viewer)"

2. **Service account keys**
   > "⚠️ GCP: Avoid user-managed keys - use Workload Identity instead"

3. **Public access**
   > "⚠️ GCP: Enable public access prevention on Cloud Storage buckets"

4. **Missing encryption**
   > "⚠️ GCP: Enable CMEK encryption for sensitive data"
