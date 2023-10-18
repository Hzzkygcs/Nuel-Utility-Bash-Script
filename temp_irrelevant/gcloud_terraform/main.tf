provider "google" {
    access_token = data.external.gcloud_auth_token.result.token

    project = "traveloka-testing-calendar-api"
    region = "us-central1"
    zone = "us-central1-c"
}

// After applying this, you can see a new Google API Key will be created after applying the terraform:
// https://console.cloud.google.com/apis/credentials/key/some-unique-name?project=traveloka-testing-calendar-api
// or:
// https://console.cloud.google.com/apis/credentials?project=traveloka-testing-calendar-api
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