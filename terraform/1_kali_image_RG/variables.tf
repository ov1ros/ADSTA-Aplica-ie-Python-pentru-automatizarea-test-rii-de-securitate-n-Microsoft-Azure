variable "subscription_id" {
  description = "Azure subscription ID used for resource deployment."
  type        = string
  sensitive   = true
}

variable "location" {
  description = "Azure region where the Kali image resource group is created"
  type        = string
}