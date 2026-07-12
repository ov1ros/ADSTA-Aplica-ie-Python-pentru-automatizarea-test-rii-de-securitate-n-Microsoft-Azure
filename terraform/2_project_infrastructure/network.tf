# Network infrastructure for the project.
# It includes the virtual network, subnets, NSGs, and public IP address.

# Gets the current public IP address of the user.
# This IP is used to restrict access to the Kali VM.
data "http" "admin_ip" {
  url = "https://api.ipify.org"
}

# Public IP address for the Kali VM.
resource "azurerm_public_ip" "kali_pip" {
  name                = local.pip_kali_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

# Virtual network.
resource "azurerm_virtual_network" "vnet" {
  name                = local.vnet_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  address_space       = var.vnet_address_space

}

# Subnet for the Kali VM.
resource "azurerm_subnet" "kali_subnet" {
  name                 = local.kali_snet_name
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [var.snet_kali_prefix]
}

# Subnet for the vulnerable Windows VM.
resource "azurerm_subnet" "vulnerable_subnet" {
  name                 = local.vulnerable_snet_name
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [var.snet_vulnerable_prefix]
}

# Subnet for the protected Windows VM.
resource "azurerm_subnet" "protected_subnet" {
  name                 = local.protected_snet_name
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [var.snet_protected_prefix]
}

# Network security group for the Kali VM.
resource "azurerm_network_security_group" "nsg_kali" {
  name                = local.nsg_kali_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  # RDP (3389) access is allowed only from the user's public IP.

  security_rule {
    name                       = "RDP-AdminIP"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_ranges    = "3389"
    source_address_prefix      = local.admin_ip_cidr
    destination_address_prefix = "*"
  }
}

# Network security group for the vulnerable Windows VM.
resource "azurerm_network_security_group" "nsg_vulnerable" {
  name                = local.nsg_vulnerable_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  # All traffic from the Kali subnet is allowed.
  security_rule {
    name                       = "Any-Kali"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = var.snet_kali_prefix
    destination_address_prefix = "*"
  }
}

# Network security group for the protected Windows VM.
resource "azurerm_network_security_group" "nsg_protected" {
  name                = local.nsg_protected_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  # Only required ports are allowed from the Kali subnet.
  security_rule {
    name                       = "Limited-Kali"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_ranges    = ["3389", "80", "443", "5985"]
    source_address_prefix      = var.snet_kali_prefix
    destination_address_prefix = "*"
  }

  # Block everything else from Kali. 
  # Without this rule, the default AllowVnetInBound rule would still allow additional ports.
  security_rule {
    name                       = "Deny-Kali-Other"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = var.snet_kali_prefix
    destination_address_prefix = "*"
  }

}

# Associates each subnet with its network security group.
resource "azurerm_subnet_network_security_group_association" "kali_nsg_assoc" {
  subnet_id                 = azurerm_subnet.kali_subnet.id
  network_security_group_id = azurerm_network_security_group.nsg_kali.id
}

resource "azurerm_subnet_network_security_group_association" "vulnerable_nsg_assoc" {
  subnet_id                 = azurerm_subnet.vulnerable_subnet.id
  network_security_group_id = azurerm_network_security_group.nsg_vulnerable.id
}

resource "azurerm_subnet_network_security_group_association" "protected_nsg_assoc" {
  subnet_id                 = azurerm_subnet.protected_subnet.id
  network_security_group_id = azurerm_network_security_group.nsg_protected.id
}
