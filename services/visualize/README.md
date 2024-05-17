# Simple Dust Visualisation

Loads automatically updated `dust.csv` and CHLa data from cloud storage and creates an interactive plot which then can be served using panel running in a Docker container.

## Deployment

```shell
$ gcloud run deploy \
    --allow-unauthenticated \
    --service-account "mardata-oscm-storage@<project-id>.iam.gserviceaccount.com"
    --source . dust-visualization
```