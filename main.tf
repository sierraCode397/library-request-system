provider "aws" {
  region = local.region
}

resource "aws_s3_bucket" "test_bucket" {
  bucket = "isaac-terraform-test-bucket-${random_id.suffix.hex}"
  tags = {
    Name        = "Terraform Test Bucket"
    Environment = "Test"
  }
}

# Recurso auxiliar para generar un sufijo aleatorio
resource "random_id" "suffix" {
  byte_length = 4
}