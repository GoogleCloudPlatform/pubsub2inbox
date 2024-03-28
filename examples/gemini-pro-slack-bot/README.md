# Vertex AI Gemini Pro Slack bot example

A Slack chat bot that uses the Gemini 1.0 Pro Vision model. It can accept images and text from Slack.

## Deploying

1. Navigate to Slack settings, `Tools & Settings > Manage apps`.
2. Click on `Build` in the top right corner.
3. Click on `Create new app` and select `From manifest`.
4. Copy the contents [slack-manifest.yaml](slack-manifest.yaml) into the text box.
5. Proceed with creation of the Slack application and install it to your workspace.
6. You should now be able to view application credentials. Take the `App ID` and `Signing Secret` and place them in `terraform.tfvars` (`slack_app_id` and `slack_signing_key`).
7. Next click on `OAuth & Permissions` and take the `Bot User OAuth Token` and place it in `terraform.tfvars` (`slack_token`).
8. You can now run `terraform apply` to deploy the bot. After deployment, you should see the Cloud Run Json2Pubsub URL in the output.
9. In Slack app settings, click on `Event Subscriptions` and replace the `Request URL` with the URL from the previous step.
10. In Slack, create a channel and add the bot to it (channel settings, `Integrations > Add an app`).
11. You can now discuss with the bot via private messages or tagging it in a channel!

## Integrating Vertex AI Search

By setting `vertex_search` parameter, you can deploy an additional Gemini function call which can search
your Vertex AI Datastore. Follow the [Vertex AI Search quickstart](https://cloud.google.com/generative-ai-app-builder/docs/try-enterprise-search)
(which uses Alphabet's financial documents) and enable it in `terraform.tfvars`:

```
vertex_search = {
  enabled      = true
  location     = "eu" # or global, us
  datastore_id = "YOUR_DATASTORE_ID_12345678" # replace this with your datastore ID
}
```

Once deployed, Gemini is given the possibility to function call the Vertex Search function
and integrate the results.

### Example Terraform connfiguraiton

Example `terraform.tfvars` file:

```hcl
project_id        = "<your-project-id>"
region            = "europe-west1"
slack_token       = "xoxb-...." # Slack OAuth token for workspace
slack_signing_key = "8e................02f" # Slack signing key
slack_app_id      = "A........L" # App ID
```

See the previous article: [Building an AI Slack Bot using Vertex Generative AI](https://taneli-leppa.medium.com/building-an-ai-slack-bot-using-vertex-generative-ai-d5f2c9e5e0b0)
