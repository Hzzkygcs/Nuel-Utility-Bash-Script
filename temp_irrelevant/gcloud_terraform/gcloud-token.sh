

AUTH_TOKEN=$(gcloud auth print-access-token)
# AUTH_TOKEN="YourTokenGoesHere"
OUTPUT=$(jq --null-input --arg token "$AUTH_TOKEN" '{"token": $token}')

echo "$OUTPUT"

# This will give output: 
# {
#   "token": "YourTokenGoesHere"
# }