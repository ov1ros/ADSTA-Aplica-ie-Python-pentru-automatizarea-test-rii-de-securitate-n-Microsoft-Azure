# This resource group is created for the main project infrastructure.
resource "azurerm_resource_group" "rg" {
  name     = local.rg_name
  location = local.location
}