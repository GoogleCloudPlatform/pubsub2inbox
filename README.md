# ![Pubsub2Inbox](img/logo.png)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) ![Tests](https://github.com/GoogleCloudPlatform/pubsub2inbox/actions/workflows/test.yml/badge.svg)


Pubsub2Inbox is a generic tool to handle input from Pub/Sub messages and turn them into
email, webhooks or GCS objects. It's based on an extendable framework consisting of input 
and output processors. Input processors can enrich the incoming messages with details
(for example, fetching the budget from Cloud Billing Budgets API). Multiple output
processors can be chained together. 

Pubsub2Inbox is written in Python 3.8+ and can be deployed as a Cloud Function or as a 
Cloud Run function easily. To guard credentials and other sensitive information, the tool can 
fetch its YAML configuration from Google Cloud Secret Manager.

The tool also supports templating of emails, messages and other parameters through
[Jinja2 templating](https://jinja.palletsprojects.com/en/2.10.x/templates/).

*Please note:* You cannot connect to SMTP port 25 from GCP. Use alternative ports 465 or 587,
or connect via [Serverless VPC Connector](https://cloud.google.com/vpc/docs/configure-serverless-vpc-access) to your own mailservers.

## Out of the box

Out of the box, you'll have the following functionality:

| Title                         | Example use cases                                                                                                                                                                                                                             | Samples                                                                                                                                                                                                                                                                                                                                        |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Budget alerts                 | Get email if a project's budget exceeds certain limit. For more information, see [How to set up programmatic notifications from billing budgets](https://cloud.google.com/billing/docs/how-to/budgets-programmatic-notifications).            | [Budget alerts](examples/budget-config.yaml)                                                                                                                                                                                                                                                                                                   |
| Cloud Security Command Center | Send emails when a new security finding is made (see [how to set up finding notifications from SCC](https://cloud.google.com/security-command-center/docs/how-to-notifications)), or create new findings from any Pub/Sub message.            | [Email notifications of findings](examples/scc-config.yaml)<br />[Create findings from Cloud IDS](examples/scc-cloud-ids.yaml)<br />[Create custom findings](examples/scc-finding-config.yaml)                                                                                                                                                 |
| Cloud Storage                 | When a new report arrives in a bucket, send it out as an email attachment. Or copy files to a backup bucket as soon as they arrive. See: [How to set up Cloud Storage notifications](https://cloud.google.com/storage/docs/reporting-changes) | [Cloud Storage notifications](examples/storage-example.yaml)<br />[Cloud Storage backup copier](examples/gcscopy-example.yaml)                                                                                                                                                                                                                 |
| BigQuery                      | Run BigQuery queries on a schedule and turn the results into CSV or spreadsheets and send them out as email attachments.                                                                                                                      | [BigQuery queries](examples/bigquery-example.yaml)                                                                                                                                                                                                                                                                                             |
| Recommendations               | Generate recommendations and insights for project owner's on a scheduled basis. Uses [Recommender API](https://cloud.google.com/recommender/docs/overview).                                                                                   | [Recommendations and Insights reports](examples/recommendations/)<br />[Example with attached spreadsheet](examples/recommendations/per-project/recommendations.yaml)<br />[Example with with GCS and BigQuery output](examples/recommendations/all-projects/recommendations-example-3.yaml).                                                  |
| Cloud Monitoring              | Send alerts from Cloud Monitoring via your own SMTP servers, or use an unsupported messaging platform. Or run Cloud Monitoring MQL queries and send the results.                                                                              | [Cloud Monitoring alerts](examples/monitoring-alert-config.yaml)<br />[Service account usage reporting using Cloud Monitoring and Cloud Asset Inventory](examples/cai-example.yaml)                                                                                                                                                            |
| Cloud Asset Inventory         | Use Cloud Asset Inventory to fetch resources organization-wide.                                                                                                                                                                               | [Fetch all service accounts from CAI](examples/cai-example.yaml)                                                                                                                                                                                                                                                                               |
| Cloud Identity                | Fetch groups or memberships, or change group settings. For example, build a report of members in a group for review and send it out via email.                                                                                                | [Cloud Identity groups](examples/groups-example.yaml)<br />[Another example](examples/groups-example-2.yaml)<br />[Groups that allow external members](examples/external-groups-example.yaml)<br />[Example of Directory API](examples/directory-example.yaml)<br />[Update group default settings on creation](examples/groups-settings.yaml) |
| Cloud DNS                     | Add or remove records based on Pub/Sub messages.                                                                                                                                                                                              | [Add DNS entries](examples/dns-example.yaml)                                                                                                                                                                                                                                                                                                   |
| Resource Manager              | List and search for GCP projects.                                                                                                                                                                                                             | [GCP projects](examples/projects-example.yaml)                                                                                                                                                                                                                                                                                                 |
| Secret Manager                | Fetch secrets from Secret Manager.                                                                                                                                                                                                            | [Retrieve secret](examples/secret-example.yaml)                                                                                                                                                                                                                                                                                                |
| Scripting                     | Run any binary or shell script and parse the output (supports JSON, YAML, CSV, etc.)                                                                                                                                                          | [Shell processor](examples/shellscript-config.yaml)                                                                                                                                                                                                                                                                                            |
| Transcoder                    | Transcode video and audio using [Transcoder API](https://cloud.google.com/transcoder).                                                                                                                                                        | [Transcoding a video](examples/transcode-example.yaml)                                                                                                                                                                                                                                                                                         |
| Messaging                     | Send messages to Google Chat or SMS messages.                                                                                                                                                                                                 | [Send SMS messages using Twilio](examples/twilio-example.yaml)<br />[Cloud Deploy notifications to Google Chat](examples/chat-example.yaml)                                                                                                                                                                                                    |
|                               |
| JSON                          | Generic JSON parser.                                                                                                                                                                                                                          | [Generic JSON processing](examples/generic-config.yaml)                                                                                                                                                                                                                                                                                        |
  
## Input processors

Available input processors are:

  - [budget.py](processors/budget.py): retrieves details from Cloud Billing Budgets
    API and presents.
  - [scc.py](processors/scc.py): enriches Cloud Security Command Center
    findings notifications.
  - [bigquery.py](processors/bigquery.py): queries from BigQuery datasets.
  - [genericjson.py](processors/genericjson.py): Parses message data as JSON and
    presents it to output processors.
  - [recommendations.py](processors/recommendations.py): Retrieves recommendations
    and insights from the [Recommender API](https://cloud.google.com/recommender/docs/overview).
  - [groups.py](processors/groups.py): Retrieves Cloud Identity Groups 
  - [directory.py](processors/groups.py): Retrieves users, groups, group members and group settings
  - [monitoring.py](processors/monitoring.py): Retrieves time series data from Cloud Ops Monitoring
  - [projects.py](processors/projects.py): Searches or gets GCP project details
  - [cai.py](processors/cai.py): Fetch assets from Cloud Asset Inventory
  - [shellscript.py](processors/shellscript.py): Run any binary or shell script and parse the output (JSON, YAML, CSV, TSV, ...)
  - [transcode.py](processors/transcode.py): Transcode media using Transcoder API.
  - [dns.py](processors/dns.py): Issue change requests to Cloud DNS.
  - [secret.py](processor/secret.py): Fetches (additional) secrets from Secret Manager.

For full documentation of permissions, processor input and output parameters, see [PROCESSORS.md](PROCESSORS.md).

Please note that the input processors have some IAM requirements to be able to
pull information from GCP:

 - Resend mechanism (see below)
    - Storage Object Admin (`roles/storage.objectAdmin`)
 - Signed URL generation (see `filters/strings.py:generate_signed_url`)
    - Storage Admin on the bucket (`roles/storage.admin`)

## Output processors

Available output processors are:

  - [mail.py](output/mail.py): can send HTML and/or text emails via SMTP gateways,
    SendGrid or MS Graph API (Graph API implementation lacks attachment support)
  - [gcs.py](output/gcs.py): can create objects on GCS from any inputs.
  - [webhook.py](output/webhook.py): can send arbitrary HTTP requests, optionally
    with added OAuth2 bearer token from GCP.
  - [gcscopy.py](output/gcscopy.py): copies files between buckets.
  - [logger.py](output/logger.py): Logs message in Cloud Logging.
  - [pubsub.py](output/pubsub.py): Sends one or more Pub/Sub messages.
  - [bigquery.py](output/bigquery.py): Sends output to a BigQuery table via a load job.
  - [scc.py](output/scc.py): Sends findings to Cloud Security Command Center.
  - [twilio.py](output/twilio.py): Sends SMS messages via Twilio API.
  - [groupssettings.py](output/groupssettings.py): Updates Google Groups settings.
  - [chat.py](output/chat.py): Send messages to Google Chat.

Please note that the output processors have some IAM requirements to be able to
pull information from GCP:

 - `mail.py`
    - Group membership expansion requires following the instructions at
      [Groups API: Authenticating as a service account without domain-wide delegation](https://cloud.google.com/identity/docs/how-to/setup#auth-no-dwd)
      to grant permissions to the service account the function is running under. 
    - In addition, the service account that the script runs under will need to have `roles/iam.serviceAccountTokenCreator` on itself when
      running in Cloud Function/Cloud Run (for Directory API scoped tokens).

## Configuring Pubsub2Inbox

## Pipeline-based configuration

Pubsub2Inbox is configured through a YAML file (for examples, see the [examples/](examples/)
directory). 

The YAML file is structured of the following top level keys:

  - `pipeline`: a list of processors and/or outputs to run in sequence.
    - `type`: what processor or output to run (eg. `processor.genericjson` or `output.logger`)
    - `config`: configuration of the processor or output
    - `runIf`: if this evaluates to empty, the processor/output is not run
    - `stopIf`: if this evalues to non-empty, the processing is stopped immediately (before the processor/output is run)
    - `ignoreOn`: skips reprocessing of messages, see below:
      - `bucket`: Cloud Storage bucket to store reprocessing markers (zero-length files), has to exist
      - `period`: textual presentation of the period after which a message can be reprocessed (eg. `2 days`)
      - `key`: the object reprocessing marker name (filename), if not set, it is the message and its properties hashed,
        otherwise you can specify a Jinja expression
    - `canFail`: if set to true, the task can fail but processing will still continue
    - `output`: the output variable for processors (some processors accept a single string, some a list of keys and values)
  - `maximumMessageAge`: a textual representation of maximum age of a message that can be processed (set to `skip` to ignore)
  - `globals`: a dictionary of variables that is evaluated before starting the pipeline, useful for things like localization, 
    or other configuration parameters that get repeatedly used in the pipeline configuration

For example of a modern pipeline, see [shell script example](examples/shellscript-config.yaml) or [test configs](test/configs/).

### Legacy configuration

Input processors are configured under `processors` key and outputs under `outputs`.

The retry mechanism acknowledges and discards any messages that are older than a 
configured period (`retryPeriod` in configuration, default 2 days).

The resend mechanism is to prevent recurring notifications from being send. It relies
on a Cloud Storage bucket where is stores zero-length files, that are named by
hashing the `resendKey` (if it is omitted, all template parameters are used). The
resend period is configurable through `resendPeriod`. To prevent the resend bucket
from accumulating unlimited files, set an [Object Lifecycle Management policy](https://cloud.google.com/storage/docs/lifecycle)
on the bucket.


## Deploying as Cloud Function

### Deploying via Terraform

Sample Terraform module is provided in `main.tf`, `variables.tf` and `outputs.tf`. Pass the following
parameters in when using as a module:

  - `project_id` (string): where to deploy the function
  - `organization_id` (number): organization ID (for organization level permissions)
  - `function_name` (string): name for the Cloud Function
  - `function_roles` (list(string)): list of curated permissions roles for the function (eg. `scc`, `budgets`, `bigquery_reader`, `bigquery_writer`, `cai`, `recommender`, `monitoring`)
  - `pubsub_topic` (string): Pub/Sub topic in the format of `projects/project-id/topics/topic-id` which the Cloud Function should be triggered on
  - `region` (string, optional): region where to deploy the function
  - `secret_id` (string, optional): name for the Cloud Secrets Manager secrets (defaults to `function_name`)
  - `config_file` (string, optional): function configuration YAML file location (defaults to `config.yaml`)
  - `service_account` (string, optional): service account name for the function (defaults to `function_name`)
  - `bucket_name` (string, optional): bucket where to host the Cloud Function archive (defaults to `cf-pubsub2inbox`)
  - `bucket_location` (string, optional): location of the bucket for Cloud Function archive (defaults to `EU`)
  - `helper_bucket_name` (string, optional): specify an additional Cloud Storage bucket where the service account is granted `storage.objectAdmin` on
  - `function_timeout` (number, optional): a timeout for the Cloud Function (defaults to `240` seconds)
  - `retry_minimum_backoff` (string, optional): minimum backoff time for exponential backoff retries in Cloud Run. Defaults to 10s.
  - `retry_maximum_backoff` (string, optional): maximum backoff time for exponential backoff retries in Cloud Run. Defaults to 600s.
  - `vpc_connector` (string, optional): ID of the serverless VPC Connector for the Cloud Function
  - `cloud_run` (boolean, optional): deploy via Cloud Run instead of Cloud Function. Defaults to `false`. If set to `true`, also specify `cloud_run_container`.
  - `cloud_run_container` (string, optional): container image to deploy on Cloud Run. See previous parameter.

## Deploying manually

First, we have the configuration in `config.yaml` and we're going to store the configuration for
the function as a Cloud Secret Manager secret.

Let's define some variables first:

```sh
export PROJECT_ID=your-project # Project ID where function will be deployed
export REGION=europe-west1 # Where to deploy the functions
export SECRET_ID=pubsub2inbox # Secret Manager secret name
export SERVICE_ACCOUNT=pubsub2inbox # Service account name
export SECRET_URL="projects/$PROJECT_ID/secrets/$SECRET_ID/versions/latest"
export FUNCTION_NAME="pubsub2inbox"
export PUBSUB_TOPIC="billing-alerts" # projects/$PROJECT_ID/topics/billing-alerts
```

Then we'll create the secrets in Secret Manager:

```sh
gcloud secrets create $SECRET_ID \
    --replication-policy="automatic" \
    --project $PROJECT_ID

gcloud secrets versions add $SECRET_ID \
    --data-file=config.yaml \
    --project $PROJECT_ID
```

We will also create a service account for the Cloud Function:

```sh
gcloud iam service-accounts create $SA_NAME \
    --project $PROJECT_ID

gcloud secrets add-iam-policy-binding $SECRET_ID \
    --member "serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role "roles/secretmanager.secretAccessor" \
    --project $PROJECT_ID

gcloud iam service-accounts add-iam-policy-binding $SA_NAME@$PROJECT_ID.iam.gserviceaccount.com \
    --member "serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role "roles/iam.serviceAccountTokenCreator" \
    --project $PROJECT_ID

```

Now we can deploy the Cloud Function:

```sh
gcloud functions deploy $FUNCTION_NAME \
    --entry-point process_pubsub \
    --runtime python38 \
    --trigger-topic $PUBSUB_TOPIC \
    --service-account "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --set-env-vars "CONFIG=$SECRET_URL" \
    --region $REGION \
    --project $PROJECT_ID
```

## Deploying via Cloud Run

### Prebuilt image

A prebuilt container image is available on this page. The container is signed and the signature
can be verified with `cosign` for example:

```sh
cosign verify --key container-signature.pub ghcr.io/googlecloudplatform/pubsub2inbox:latest
```

### Building the container

A [`Dockerfile`](Dockerfile) has been provided for building the container. You can build the 
image locally and push it to for example [Artifact Registry](https://cloud.google.com/artifact-registry).

```sh
docker build -t europe-west4-docker.pkg.dev/$PROJECT_ID/pubsub2inbox/pubsub2inbox . 
docker push europe-west4-docker.pkg.dev/$PROJECT_ID/pubsub2inbox/pubsub2inbox
```

### Deploying via Terraform

The provided Terraform scripts can deploy the code as a Cloud Function or Cloud Run. To enable
Cloud Run deployment, build and push the image and set `cloud_run` and `cloud_run_container`
parameters (see the parameter descriptions above).

This is a simple example of deploying the function straight from the repository:

```hcl
locals {
  project_id    = <YOUR-PROJECT-ID>
  region        = "europe-west1"
  helper_bucket = true
}

module "pubsub-topic" {
  source     = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/pubsub"
  project_id = local.project_id
  name       = "pubsub-example-1"
  iam = {}
}

# This optional helper bucket is used to store resend objects for example
module "helper-bucket" {
  count      = local.helper_bucket ? 1 : 0
  source     = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/gcs"
  project_id = local.project_id
  name       = format("pubsub2inbox-helper-%s", module.pubsub2inbox.name)
}

module "pubsub2inbox" {
  source = "github.com/GoogleCloudPlatform/pubsub2inbox"

  project_id = local.project_id
  region     = local.region

  function_name = "function-example-1"
  pubsub_topic  = module.pubsub-topic.id

  config_file     = "<YOUR-CONFIGURATION-FILE>.yaml"
  # Downloads the release from Github
  use_local_files = false

  bucket_name        = format("pubsub2inbox-source-%s", module.pubsub2inbox.name)
  bucket_location    = local.region
  helper_bucket_name = local.helper_bucket ? module.helper-bucket.0.bucket.name : ""

  # Add additional permissions for the service account here
  function_roles = []
}
```

### Generating documentation

Run the command:

```
# cd docs && make markdown
```

### Running tests

Run the command:

```
# python3 -m unittest discover
```

To set against a real cloud project, set `PROJECT_ID` environment variable. 
