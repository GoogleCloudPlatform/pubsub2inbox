# Vertex AI Generative AI Slack bot example

See the article: [Building an AI Slack Bot using Vertex Generative AI](https://taneli-leppa.medium.com/building-an-ai-slack-bot-using-vertex-generative-ai-d5f2c9e5e0b0)

Create a `terraform.tfvars` file containing:

```hcl
project_id        = "<your-project-id>"
region            = "europe-west1"
slack_token       = "xoxb-...." # Slack OAuth token for workspace
slack_signing_key = "8e................02f" # Slack signing key
slack_app_id      = "A........L" # App ID
```