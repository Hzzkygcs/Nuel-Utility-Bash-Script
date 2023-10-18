data "external" "gcloud_auth_token" {
  program = [
    "sh", "${path.module}/gcloud-token.sh",
  ]
  query = {
    # You can pass something to STDIN of your program here, 
    # but as per current version, the input will be given as JSON (map of string)
  }
}

data "google_project" "project" {}  # will read metadata based on `provider "google"{} `