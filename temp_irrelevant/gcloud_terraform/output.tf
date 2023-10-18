output "terraform_google_temporary_auth_token" {
    value = data.external.gcloud_auth_token.result.token
}

output "google_project_id" {
    value = data.google_project.project.project_id
}

output "google_project_number" {
    value = data.google_project.project.number
}

output "google_calendar_api_key__id"{
    value = google_apikeys_key.google_calendar_api_key.id
}

output "google_calendar_api_key__uid"{
    value = google_apikeys_key.google_calendar_api_key.uid
}

output "google_calendar_api_key__encrypted_apikey"{
    value = google_apikeys_key.google_calendar_api_key.key_string
    description = <<EOF
        This is not plain API key. It is encrypted. You may need to read https://cloud.google.com/api-keys/docs/reference/rest/v2/projects.locations.keys/getKeyString or 
        
        EDIT:
        They say it is encrypted but it's somehow not. 
        I tried to run this and success:
        https://www.googleapis.com/calendar/v3/calendars/id.indonesian%23holiday%40group.v.calendar.google.com/events?key=AIzaSyBot2ymMBuHhq1wUcAPoA29IO1DxZvUiZc
        
        where the output of `terraform apply` is this:
        google_calendar_api_key__encrypted_apikey = AIzaSyBot2ymMBuHhq1wUcAPoA29IO1DxZvUiZc
    EOF
}