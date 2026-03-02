# -------------------------------------------------------------------------
# Program: outputs.tf
# Description: Output values for VideoToNotes Azure resources
# Context: VideoToNotes project - Azure AI Services for speech and inference
# Author: Greg Tate
# Date: 2026-03-02
# -------------------------------------------------------------------------

output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

# =========================================================================
# AI Services Account outputs
# =========================================================================

output "ai_services_name" {
  description = "AI Services account name"
  value       = azurerm_cognitive_account.ai_services.name
}

output "azure_openai_endpoint" {
  description = "Azure OpenAI endpoint for chat completions"
  value       = azurerm_cognitive_account.ai_services.endpoint
}

output "speech_region" {
  description = "Azure region for the Speech Service (used by spx CLI)"
  value       = azurerm_cognitive_account.ai_services.location
}

# =========================================================================
# Model Deployment outputs
# =========================================================================

output "model_deployment_name" {
  description = "Deployed model name (use with --azure-deployment parameter)"
  value       = azurerm_cognitive_deployment.model.name
}

# =========================================================================
# Storage Account outputs
# =========================================================================

output "storage_account_name" {
  description = "Storage account name for batch transcription"
  value       = azurerm_storage_account.transcription.name
}

output "storage_container_name" {
  description = "Blob container for transcription audio uploads"
  value       = azurerm_storage_container.audio.name
}

# =========================================================================
# spx CLI configuration commands
# =========================================================================

output "spx_config_commands" {
  description = "Run these commands to configure the spx CLI for this deployment"
  value       = <<-EOT
    spx config @region --set ${azurerm_cognitive_account.ai_services.location}
    spx config @key --set $(az cognitiveservices account keys list --name ${azurerm_cognitive_account.ai_services.name} --resource-group ${azurerm_resource_group.main.name} --query key1 -o tsv)
  EOT
}

# =========================================================================
# Script invocation examples
# =========================================================================

output "video_notes_usage" {
  description = "Example command to run New-VideoNotes with Azure provider"
  value       = "New-VideoNotes.ps1 -YouTubeUrl <url> -Provider Azure -AzureEndpoint '${azurerm_cognitive_account.ai_services.endpoint}' -AzureDeployment '${azurerm_cognitive_deployment.model.name}'"
}

output "presentation_notes_usage" {
  description = "Example command to run New-PresentationNotes with Azure provider"
  value       = "New-PresentationNotes.ps1 -PdfFile <file.pdf> -VideoFile <file.mp4> -Provider Azure -AzureEndpoint '${azurerm_cognitive_account.ai_services.endpoint}' -AzureDeployment '${azurerm_cognitive_deployment.model.name}'"
}
