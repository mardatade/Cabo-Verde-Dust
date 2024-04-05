# Service: Lidar Preprocessing

Purpose: While it's straightforward to download and pre-process the lidar data, it takes a lot of time (up to 2 seconds per day of data). The final "dust" timeseries we want is average depolarisation from 50 to 200 meters resampled to 6 hours or so.

So let's re-process the data with a daily cron job.

## Resulting timeseries

Stored in: <https://storage.googleapis.com/2024-mardata-oscm-dust/dust.csv>

## Deployment

Submit image build:
```shell
$ gcloud builds submit --async --tag europe-west2-docker.pkg.dev/<project-id>/cloud-run-source-deploy/lidar-preprocessing:latest .
```

Create job, add time and memory:
```shell
$ gcloud run jobs create lidar-preprocessing --image europe-west2-docker.pkg.dev/<project-id>/cloud-run-source-deploy/lidar-preprocessing:latest 
$ gcloud run jobs update lidar-preprocessing --memory 2G --task-timeout 1800
```

Set service account:
```shell
$ gcloud run jobs update lidar-preprocessing --service-account "mardata-oscm-storage@<project-id>.iam.gserviceaccount.com"
```

Schedule:
```shell
$ gcloud scheduler jobs update http lidar-preprocessing-shedule \
  --location europe-west2 \
  --schedule="5 2,8,14,20 * * *" \
  --uri="https://europe-west2-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/<project-id>/jobs/lidar-preprocessing:run" \
  --http-method POST \
  --oauth-service-account-email <project-id>-compute@developer.gserviceaccount.com
```