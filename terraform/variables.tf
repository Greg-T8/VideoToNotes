# -------------------------------------------------------------------------
# Program: variables.tf
# Description: Input variable declarations for VideoToNotes Azure resources
# Context: VideoToNotes project - Azure AI Services for speech and inference
# Author: Greg Tate
# Date: 2026-03-02
# -------------------------------------------------------------------------

variable "subscription_id" {
  description = "Azure subscription ID for the deployment"
  type        = string
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"

  validation {
    condition     = contains(["eastus", "eastus2", "westus2", "centralus"], var.location)
    error_message = "Location must be a supported US region."
  }
}

variable "owner" {
  description = "Owner tag value applied to all resources"
  type        = string
  default     = "Greg Tate"
}

variable "date_created" {
  description = "Date the resources were created (YYYY-MM-DD format)"
  type        = string
  default     = "2026-03-02"

  validation {
    condition     = can(regex("^\\d{4}-\\d{2}-\\d{2}$", var.date_created))
    error_message = "Date must be in YYYY-MM-DD format."
  }
}

variable "ai_services_sku" {
  description = "SKU tier for the AI Services account"
  type        = string
  default     = "S0"

  validation {
    condition     = contains(["S0"], var.ai_services_sku)
    error_message = "AI Services SKU must be S0."
  }
}

variable "model_name" {
  description = "OpenAI model name to deploy for notes generation"
  type        = string
  default     = "gpt-4.1-mini"
}

variable "model_version" {
  description = "OpenAI model version to deploy"
  type        = string
  default     = "2025-04-14"
}

variable "model_capacity" {
  description = "Model deployment capacity in thousands of tokens per minute (TPM)"
  type        = number
  default     = 10

  validation {
    condition     = var.model_capacity >= 1 && var.model_capacity <= 100
    error_message = "Model capacity must be between 1 and 100."
  }
}

variable "storage_account_tier" {
  description = "Storage account performance tier"
  type        = string
  default     = "Standard"

  validation {
    condition     = contains(["Standard", "Premium"], var.storage_account_tier)
    error_message = "Storage tier must be Standard or Premium."
  }
}

variable "storage_replication" {
  description = "Storage account replication type"
  type        = string
  default     = "LRS"

  validation {
    condition     = contains(["LRS", "GRS", "ZRS"], var.storage_replication)
    error_message = "Replication must be LRS, GRS, or ZRS."
  }
}
