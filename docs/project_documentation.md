# Drop

A simple self-hosted file sharing service.

## Features

1. Allows to quickly deploy with Docker
2. Exposes upload and download
3. Upload page allows to upload any file. By default the file will be deleted after successful download but it's also possible to set expiration:
  - 5 minutes
  - 30 minutes
  - 2 hours
  - Forever
4. Upon upload the file is available by random, easy to read and remember path e.g. {url}/d/maple-turkey-ghost
5. The download url is returned after successful upload
6. UI is very simple, upload form, radio buttons to select expiration and upload button
7. It's also possible to use CLI with curl to both upload and download.

## User flow

### Upload

1. User wants to share file from PC A to PC B using local network.
2. User opens the browser and navigates to drop service
3. User is presented with upload form
4. User selects the file, chooses the expiration (by default it's delete after successful download)
5. User clicks Upload button
6. After successful upload user is give the download url for the file

### Download

1. User visits the download url
2. Download starts imidietly 

## Out of scope

1. RBAC and login
2. Database - files should be stores with original name but inside random directories provided in url

