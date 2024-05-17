# Service: CHLa Preprocessing

Purpose: Store the CHLa data directly in the cloud to avoid latency when accessing the copernicus store and to avoid providing CMEMS credentials to the vis app.

## Resulting fields

Stored in: <https://storage.googleapis.com/2024-mardata-oscm-dust/>

## Deployment

Submit image build:
```shell
$ gcloud builds submit --async --tag europe-west2-docker.pkg.dev/<project-id>/cloud-run-source-deploy/chla-preprocessing:latest .
```

Create job, add time and memory:
```shell
$ gcloud run jobs create chla-preprocessing --image europe-west2-docker.pkg.dev/<project-id>/cloud-run-source-deploy/chla-preprocessing:latest 
$ gcloud run jobs update chla-preprocessing --memory 2G --task-timeout 1800
```

Set service account:
```shell
$ gcloud run jobs update chla-preprocessing --service-account "mardata-oscm-storage@<project-id>.iam.gserviceaccount.com"
```

Schedule:
```shell
$ gcloud scheduler jobs update http chla-preprocessing-shedule \
  --location europe-west2 \
  --schedule="4 14 * * *" \
  --uri="https://europe-west2-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/<project-id>/jobs/chla-preprocessing:run" \
  --http-method POST \
  --oauth-service-account-email <project-id>-compute@developer.gserviceaccount.com
```