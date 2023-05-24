# GitHub issue bot example

Create a `terraform.tfvars` file containing:

```hcl
project_id        = "<your-project-id>"
region            = "europe-west1"
deployer_sa       = "deploy@PROJECT-ID.iam.gserviceaccount.com"
github_secret     = "<your-token-secret>"
```

## Required permissions to deploy

```sh
export PROJECT_ID=<project-id>
export SERVICE_ACCOUNT=deploy@PROJECT-ID.iam.gserviceaccount.com
for role in cloudfunctions.admin pubsub.admin iam.serviceAccountCreator resourcemanager.projectIamAdmin secretmanager.admin storage.admin browser
do
    gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/$role"
done

```