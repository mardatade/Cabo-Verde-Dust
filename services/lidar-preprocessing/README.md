# Service: Lidar Preprocessing

Purpose: While it's straightforward to download and pre-process the lidar data, it takes a lot of time (up to 2 seconds per day of data). The final "dust" timeseries we want is average depolarisation from 50 to 200 meters resampled to 6 hours or so.

So let's re-process the data with a daily cron job.
