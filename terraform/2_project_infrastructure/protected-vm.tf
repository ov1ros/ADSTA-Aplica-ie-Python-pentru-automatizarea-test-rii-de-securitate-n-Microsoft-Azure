# Network interface for the protected Windows VM.
resource "azurerm_network_interface" "nic_protected" {
  name                = local.nic_protected_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name      = "internal"
    subnet_id = azurerm_subnet.protected_subnet.id

    # Static private IP used inside the virtual network.
    private_ip_address_allocation = "Static"
    private_ip_address            = var.protected_private_ip
  }

}

# Protected Windows virtual machine used to have DVWA in impossible level and firewall on for testing.
resource "azurerm_windows_virtual_machine" "vm_protected" {
  name                = local.vm_protected_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  size                = "Standard_B2s_v2"

  # Administrator credentials used to access the Windows VM.
  admin_username = var.admin_username
  admin_password = var.admin_password

  # Attaches the network interface to the VM.
  network_interface_ids = [
    azurerm_network_interface.nic_protected.id,
  ]

  # Operating system disk configuration.
  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  # Windows Server image used for the protected VM.
  source_image_reference {
    publisher = "MicrosoftWindowsServer"
    offer     = "WindowsServer"
    sku       = "2025-datacenter-g2"
    version   = "latest"
  }
}

# Enables WinRM on the protected Windows VM.
# WinRM allows Ansible to connect to the Windows VM.
resource "azurerm_virtual_machine_extension" "winrm_enable_protected" {
  name                 = "winrm-enable"
  virtual_machine_id   = azurerm_windows_virtual_machine.vm_protected.id
  publisher            = "Microsoft.Compute"
  type                 = "CustomScriptExtension"
  type_handler_version = "1.10"

  # Configures WinRM so Ansible can connect to the Windows VM.
  settings = jsonencode({
    commandToExecute = "powershell -Command \"Enable-PSRemoting -Force -SkipNetworkProfileCheck; Set-Service WinRM -StartupType Automatic; Start-Service WinRM; New-NetFirewallRule -DisplayName 'Allow WinRM 5985' -Direction Inbound -Protocol TCP -LocalPort 5985 -Action Allow -Profile Any -ErrorAction SilentlyContinue\""
  })
}