# This resource group is created before the main project infrastructure.
# It is used to store the resources needed for the Kali Linux virtual machine image.
resource "azurerm_resource_group" "rg_kali_image" {
  name     = "kali-image-rg"
  location = var.location
}