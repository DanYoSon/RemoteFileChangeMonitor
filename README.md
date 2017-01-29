# Remote File Change Monitor
Monitor files for changes on a remote server over SSH
Created this to help monitor my shared hosted web server for malicious changes to files.

## TODO: (no particular order)
* Add standard SMTP support
* Add status email every X days to monitor running of contianer
* Track Diff's of the files to easily see what changed (assuming they are text based eg. PHP)
* Make command executed on the remote server customizable

## Commands to run the container during dev
### Build the image
`docker build -t rfcm .`
### Run the image
Mount the source as a volume so the image does not have to be built everytime code is changed.
Mount the data folder so sensitive data is stored in a folder not monitored by git
`docker run -it --rm -v $(pwd)/src:/home/rfcm -v $(pwd)/data:/home/rfcm/data rfcm`