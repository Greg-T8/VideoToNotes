# -------------------------------------------------------------------------
# Program: providers.tf
# Description: Provider configuration for VideoToNotes Azure resources
# Context: VideoToNotes project - Azure AI Services for speech and inference
# Author: Greg Tate
# Date: 2026-03-02
# -------------------------------------------------------------------------

terraform {
  required_version = ">= 1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

# Configure the Azure provider
provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }

    cognitive_account {
      purge_soft_delete_on_destroy = false
    }
  }

  subscription_id = var.subscription_id
}
