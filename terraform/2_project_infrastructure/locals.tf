locals {

  # Resource group name.
  rg_name = "rg-${var.project_name}"

  # Virtual network name.
  vnet_name = "vnet-${var.project_name}"

  # Azure region used for the deployment. 
  location = var.location

  # Current public IP address of the user.
  # It is used to restrict access to the Kali network security group 
  admin_ip_cidr = "${trimspace(data.http.admin_ip.response_body)}/32"

  # Public IP name for the Kali VM.
  pip_kali_name = "pip-kali-${var.project_name}"

  # Subnet names.
  kali_snet_name       = "snet-kali-${var.project_name}"
  vulnerable_snet_name = "snet-vuln-${var.project_name}"
  protected_snet_name  = "snet-protd-${var.project_name}"

  # Network security group names.
  nsg_kali_name       = "nsg-kali-${var.project_name}"
  nsg_vulnerable_name = "nsg-vuln-${var.project_name}"
  nsg_protected_name  = "nsg-protd-${var.project_name}"

  # Virtual machine names.
  vm_kali_name       = "vmkali-${var.project_name}"
  vm_vulnerable_name = "vmvuln-${var.project_name}"
  vm_protected_name  = "vmprot-${var.project_name}"

  # Network interface names.
  nic_kali_name       = "nic-kali-${var.project_name}"
  nic_vulnerable_name = "nic-vuln-${var.project_name}"
  nic_protected_name  = "nic-protd-${var.project_name}"

}