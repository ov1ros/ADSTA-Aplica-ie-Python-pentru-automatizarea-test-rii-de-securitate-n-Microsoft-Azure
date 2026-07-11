variable "subscription_id" {
  description = "Azure subscription ID used for deploying the project infrastructure."
  type        = string
  sensitive   = true
}

variable "location" {
  description = "Azure region where all project resources will be deployed."
  type        = string
}

variable "project_name" {
  description = "Project name used to generate Azure resource names."
  type        = string
}

variable "admin_username" {
  description = "Administrator username used for the Windows VMs and the Kali VM."
  type        = string
}

variable "admin_password" {
  description = "Administrator password used for the vulnerable and protected Windows VMs."
  type        = string
  sensitive   = true
}

variable "kali_admin_password" {
  description = "Administrator password used for the Kali Linux VM."
  type        = string
  sensitive   = true
}

variable "vnet_address_space" {
  description = "Address space used by the virtual network."
  type        = list(string)
}

variable "snet_kali_prefix" {
  description = "CIDR address range used by the Kali subnet."
  type        = string
}

variable "snet_vulnerable_prefix" {
  description = "CIDR address range used by the vulnerable Windows VM subnet."
  type        = string
}

variable "snet_protected_prefix" {
  description = "CIDR address range used by the protected Windows VM subnet."
  type        = string
}

variable "kali_private_ip" {
  description = "Static private IP address assigned to the Kali Linux VM."
  type        = string
}

variable "vulnerable_private_ip" {
  description = "Static private IP address assigned to the vulnerable Windows VM."
  type        = string
}

variable "protected_private_ip" {
  description = "Static private IP address assigned to the protected Windows VM."
  type        = string
}

variable "kali_image_name" {
  description = "Name of the custom Kali Linux image built with Packer."
  type        = string
  default     = "kali-image"
}

variable "kali_image_rg_name" {
  description = "Name of the resource group where the custom Kali Linux image is stored."
  type        = string
  default     = "kali-image-rg"
}
