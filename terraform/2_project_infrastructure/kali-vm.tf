# Uses the Kali Linux image created with Packer.
# This image is stored in a separate resource group dedicated to image preparation.
data "azurerm_image" "kali_image" {
  name                = var.kali_image_name
  resource_group_name = var.kali_image_rg_name
}

# Network interface used by the Kali Linux virtual machine.
resource "azurerm_network_interface" "nic_kali" {
  name                = local.nic_kali_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name      = "internal"
    subnet_id = azurerm_subnet.kali_subnet.id

    # Static private IP used inside the virtual network.
    private_ip_address_allocation = "Static"
    private_ip_address            = var.kali_private_ip

    # Public IP used to access the Kali machine remotely.
    public_ip_address_id = azurerm_public_ip.kali_pip.id
  }
}

# Kali Linux virtual machine used for testing.
# It is created from the custom Kali image.
resource "azurerm_linux_virtual_machine" "vm_kali" {
  name                = local.vm_kali_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  size                = "Standard_B2s_v2"

  # Administrator credentials used to access the Kali VM.
  admin_username                  = var.admin_username
  admin_password                  = var.kali_admin_password
  disable_password_authentication = false

  # Attaches the network interface to the VM.
  network_interface_ids = [
    azurerm_network_interface.nic_kali.id,
  ]

  # Operating system disk configuration.
  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  # Custom Kali image used by the VM.
  source_image_id = data.azurerm_image.kali_image.id

  # Marketplace plan used for the Kali image.
  plan {
    name      = "kali-2026-1"
    publisher = "kali-linux"
    product   = "kali"
  }
}