variable token {}

terraform {
  required_providers {
    sonarcloud = {
      source  = "rewe-digital/sonarcloud"
      version = "0.2.1"
    }
  }
}

provider "sonarcloud" {
  organization = "petereon"
  token        = "${var.token}"
}

resource "sonarcloud_project" "petereon_woflo" {
  key        = "petereon_woflo"
  name       = "woflo"
  visibility = "public"
}
