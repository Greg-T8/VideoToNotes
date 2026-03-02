# -------------------------------------------------------------------------
# Program: main.tf
# Description: Deploy Azure AI Services (Speech + OpenAI) and Storage for
#              the VideoToNotes transcription and notes generation pipeline
# Context: VideoToNotes project - Azure AI Services for speech and inference
# Author: Greg Tate
# Date: 2026-03-02
# -------------------------------------------------------------------------

# =========================================================================
# Local values
# =========================================================================

locals {
  resource_group_name = "project-videonotes-tf"

  common_tags = {
    Environment      = "Production"
    Project          = "VideoToNotes"
    Purpose          = "Speech Transcription and AI Notes Generation"
    Owner            = var.owner
    DateCreated      = var.date_created
    DeploymentMethod = "Terraform"
  }
}

# Random suffix for globally unique resource names
resource "random_string" "suffix" {
  length  = 4
  upper   = false
  special = false
}

# =========================================================================
# Resource Group
# =========================================================================

resource "azurerm_resource_group" "main" {
  name     = local.resource_group_name
  location = var.location
  tags     = local.common_tags
}

# =========================================================================
# Azure AI Services Account (Speech + OpenAI + Vision)
# =========================================================================

# AIServices kind provides both Speech transcription and OpenAI inference
resource "azurerm_cognitive_account" "ai_services" {
  name                = "cog-videonotes-${random_string.suffix.result}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  kind                  = "AIServices"
  sku_name              = var.ai_services_sku
  custom_subdomain_name = "cog-videonotes-${random_string.suffix.result}"

  # Enable public network access for API and spx CLI calls
  public_network_access_enabled = true

  # System-assigned managed identity
  identity {
    type = "SystemAssigned"
  }

  tags = local.common_tags
}

# =========================================================================
# Model Deployment (GPT-4.1-mini for notes extraction and merge)
# =========================================================================

# Deploy GPT-4.1-mini with GlobalStandard SKU for pipeline throughput
resource "azurerm_cognitive_deployment" "model" {
  name                 = var.model_name
  cognitive_account_id = azurerm_cognitive_account.ai_services.id

  sku {
    name     = "GlobalStandard"
    capacity = var.model_capacity
  }

  model {
    format  = "OpenAI"
    name    = var.model_name
    version = var.model_version
  }

  depends_on = [azurerm_cognitive_account.ai_services]
}

# =========================================================================
# Storage Account (batch transcription audio upload/results)
# =========================================================================

# Storage account for batch transcription input audio and output results
resource "azurerm_storage_account" "transcription" {
  name                = "stvideonotes${random_string.suffix.result}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  account_tier             = var.storage_account_tier
  account_replication_type = var.storage_replication

  # Enable blob public access for batch transcription SAS URIs
  allow_nested_items_to_be_public = false

  tags = local.common_tags
}

# Blob container for batch transcription audio uploads
resource "azurerm_storage_container" "audio" {
  name                  = "transcription"
  storage_account_id    = azurerm_storage_account.transcription.id
  container_access_type = "private"
}

# =========================================================================
# RBAC: Grant deployer access for inference and storage
# =========================================================================

# Get current client config for role assignments
data "azurerm_client_config" "current" {}

# Cognitive Services User - required for OpenAI chat completions and Speech API
resource "azurerm_role_assignment" "deployer_cognitive_user" {
  scope                = azurerm_cognitive_account.ai_services.id
  role_definition_name = "Cognitive Services User"
  principal_id         = data.azurerm_client_config.current.object_id
  description          = "Deployer access for Azure OpenAI and Speech Services"
}

# Storage Blob Data Contributor - required for batch transcription uploads
resource "azurerm_role_assignment" "deployer_storage_contributor" {
  scope                = azurerm_storage_account.transcription.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = data.azurerm_client_config.current.object_id
  description          = "Deployer access for batch transcription audio storage"
}
