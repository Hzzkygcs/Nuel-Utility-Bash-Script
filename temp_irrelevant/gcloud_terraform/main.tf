provider "google" {
    access_token = data.external.gcloud_auth_token.result.token

    project = "traveloka-testing-calendar-api"
    region = "us-central1"
    zone = "us-central1-c"
}


resource "google_apikeys_key" "google_calendar_api_key" {
  name         = "some-unique-name"
  display_name = "Google Calendar API Key"
  project      = data.google_project.project.project_id

  restrictions {
    api_targets {
      methods = []
      // Service name is retrieved from
      // https://console.cloud.google.com/apis/library > Calendar > Additional details > Service name
      service = "calendar-json.googleapis.com"
    }
  }

  timeouts {}
}


# resource "google_storage-bucket" "sample_bucket" {
#    name = "demo"
#    location = "US"
#
#    website {
#
#    }
# }