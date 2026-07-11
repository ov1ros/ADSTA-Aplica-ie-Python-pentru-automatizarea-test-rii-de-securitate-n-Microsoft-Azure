# Terraform provider configuration.
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.69.0"
    }
  }
}

# Azure provider configuration.
provider "azurerm" {
  # The Azure subscription where the resources will be created.
  subscription_id = var.subscription_id
  features {
    resource_group {
      # Allow `terraform destroy` to remove this resource group even though.
      # Packer creates a managed image inside it that is not tracked by this Terraform state.
      prevent_deletion_if_contains_resources = false
    }
  }
}
