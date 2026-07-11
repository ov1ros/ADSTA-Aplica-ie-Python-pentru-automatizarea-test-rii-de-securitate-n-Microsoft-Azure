# Public IP address used to connect to the Kali VM.
output "kali_public_ip" {
  description = "Public IP address of the Kali VM."
  value       = azurerm_public_ip.kali_pip.ip_address
}

# Admin username used for the Kali VM.
output "kali_admin_username" {
  description = "Admin username for the Kali VM"
  value       = azurerm_linux_virtual_machine.vm_kali.admin_username
}

# Admin password used for the Kali VM.
output "kali_admin_password" {
  description = "Admin password for the Kali VM"
  value       = nonsensitive(var.kali_admin_password)
}