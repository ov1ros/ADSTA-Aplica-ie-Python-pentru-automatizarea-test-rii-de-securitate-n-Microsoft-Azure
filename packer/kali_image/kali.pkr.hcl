# Azure source configuration used by Packer to build the custom Kali Linux image.
source "azure-arm" "kali_image" {
  subscription_id    = var.subscription_id
  use_azure_cli_auth = true

  # Azure location and managed image settings.
  location                          = var.location
  managed_image_name                = "kali-image"
  managed_image_resource_group_name = "kali-image-rg"

  # Operating system type used for the image.
  os_type = "Linux"

  # Kali Linux Marketplace image used as the base image.
  image_publisher = "kali-linux"
  image_offer     = "kali"
  image_sku       = "kali-2026-1"
  image_version   = "latest"

  # Marketplace plan information required for the Kali Linux image.
  plan_info {
    plan_name      = "kali-2026-1"
    plan_product   = "kali"
    plan_publisher = "kali-linux"
  }

  # Temporary VM size and SSH user used during the image build process.
  vm_size      = "Standard_B2s_v2"
  ssh_username = "packer"
}

# Builds the custom Kali image.
build {
  sources = ["source.azure-arm.kali_image"]

  # Installs the required packages and tools.
  provisioner "shell" {
    inline = [
      "export DEBIAN_FRONTEND=noninteractive",
      "sudo apt-get update",
      "sudo apt-get upgrade -y",
      "sudo apt-get install -y kali-desktop-xfce xrdp dbus-x11 ansible python3-tk python3-requests python3-winrm python3-requests-ntlm freerdp-x11 nmap netcat-traditional iputils-ping",

      "ansible-galaxy collection install ansible.windows --force",
      "ansible-galaxy collection install chocolatey.chocolatey --force",
      "ansible-galaxy collection install community.windows --force",

      "echo 'startxfce4' | sudo tee /etc/skel/.xsession",
      "sudo adduser xrdp ssl-cert || true",
      "sudo systemctl enable xrdp",
      "sudo apt-get clean"
    ]
  }

  # Uploads the Ansible project.
  provisioner "file" {
    source      = "../../ansible/windows_configurations"
    destination = "/tmp"
  }

  # Uploads the Python application.
  provisioner "file" {
    source      = "../../python_app"
    destination = "/tmp"
  }

  # Place the project 
provisioner "shell" {
  inline = [
    "sudo mkdir -p /usr/share/adsta",
    "sudo cp -r /tmp/python_app /usr/share/adsta/",
    "sudo cp -r /tmp/windows_configurations /usr/share/adsta/",
    "sudo chmod -R 755 /usr/share/adsta",

    "sudo mkdir -p /etc/skel/Desktop",
    "sudo cp /usr/share/adsta/python_app/adsta.desktop /etc/skel/Desktop/adsta.desktop",
    "sudo chmod +x /etc/skel/Desktop/adsta.desktop"
  ]
}

  # Deprovisions the Azure agent so the image can be generalized and reused.
  provisioner "shell" {
    inline = [
      "if command -v waagent >/dev/null 2>&1; then sudo waagent -force -deprovision+user; elif [ -x /usr/sbin/waagent ]; then sudo /usr/sbin/waagent -force -deprovision+user; else echo 'waagent not found, skipping deprovision'; fi",
      "export HISTSIZE=0",
      "sync"
    ]
  }
}