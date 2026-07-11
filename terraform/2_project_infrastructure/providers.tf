# Terraform provider configuration for the main project infrastructure.
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.69.0"
    }

    # HTTP provider used to get the user's current public IP address.
    http = {
      source  = "hashicorp/http"
      version = "3.5.0"
    }
  }
}

# Azure provider configuration.
provider "azurerm" {
  # The Azure subscription where the resources will be created.
  subscription_id = var.subscription_id
  features {

  }
}