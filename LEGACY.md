# Legacy

## Legacy configuration

Input processors are configured under `processors` key and outputs under `outputs`.

The retry mechanism acknowledges and discards any messages that are older than a 
configured period (`retryPeriod` in configuration, default 2 days).

The resend mechanism is to prevent recurring notifications from being send. It relies
on a Cloud Storage bucket where is stores zero-length files, that are named by
hashing the `resendKey` (if it is omitted, all template parameters are used). The
resend period is configurable through `resendPeriod`. To prevent the resend bucket
from accumulating unlimited files, set an [Object Lifecycle Management policy](https://cloud.google.com/storage/docs/lifecycle)
on the bucket.

## Deploying via gcloud

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
