variable "subscription_id" {
  type        = string
  description = "Azure subscription ID used for creating the Kali image."
  sensitive   = true
}

variable "location" {
  type        = string
  description = "Azure region where the Kali image will be created."
}