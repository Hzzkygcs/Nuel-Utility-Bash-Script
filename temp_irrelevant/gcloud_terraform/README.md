Make sure you install Gcloud CLI and run `gcloud auth login` before running terraform commands.

You may also need to run this on your first timeinstalling GCloud CLI (and before running login command):
```
gcloud config set account immanuel01@ui.ac.id
gcloud config set project traveloka-testing-calendar-api
gcloud config list 
```



Complete example of terraform output after applying:
```
google_calendar_api_key__encrypted_apikey = AIzaSyBot2ymMBuHhq1wUcAPoA29IO1DxZvUiZc
google_calendar_api_key__id = projects/traveloka-testing-calendar-api/locations/global/keys/some-unique-name
google_calendar_api_key__uid = d4f869dc-3cb6-49cf-b3bf-f60a89f9aea9
google_project_id = traveloka-testing-calendar-api
google_project_number = 997581467976
token = ya29.a0AfB_byB2IVgx6wsvv8XQTn9dpHv2p4X2JEGLkqYqVwhOouxFh6pI-Kx86h8rZheDLfTNr-Tvshr19nqHbzpkjb00qoZShm08brrdnukFqsw4yndb0l-d9bVxYqguW0eeR-tmgBVaAuRLeCux10ttUJGkqbmYvbfTZkkuKIVOzwaCgYKASgSARASFQGOcNnCotxAO0Za7JYQfWw2TbYiqg0177
```