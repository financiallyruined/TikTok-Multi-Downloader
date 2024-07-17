# MultiTok
A simple Python script that downloads TikTok videos and photos concurrently, with or without a watermark.

## Features
* Concurrent downloading
* Photo downloading
* Watermark free videos
* Watermarked videos
* Supports all TikTok URL formats
* No proxy needed

## Requirements
* Python 3.6 or higher: https://www.python.org/downloads/

## Installation
Step 1. Clone the repo.
`git clone https://github.com/financiallyruined/TikTok-Multi-Downloader`

Step 2. Enter the directory
`cd TikTok-Multi-Downloader`

Step 3. Create and activate your virtual environment.

Create: `python -m venv venv` or `python3 -m venv venv`

Activate: Windows `.\venv\Scripts\activate` | Linux `. venv/bin/activate`

Step 4. Install requirements
`pip install -r requirements.txt` or `pip3 install -r requirements.txt`

## Available Options
```
usage: multitok.py [-h] [--links LINKS] [--no-watermark | --watermark] [--workers WORKERS] [--api-version {v1,v2}] [--save-metadata] [--skip-existing] [--no-folders] [--output-dir OUTPUT_DIR]

Multitok: A simple script that downloads TikTok videos concurrently.

options:
  -h, --help            show this help message and exit
  --links LINKS         The path to the .txt file that contains the TikTok links. (Default: links.txt)
  --no-watermark        Download videos without watermarks. (Default)
  --watermark           Download videos with watermarks.
  --workers WORKERS     Number of concurrent downloads. (Default: 3)
  --api-version {v1,v2}
                        API version to use for downloading videos. (Default: v2)
  --save-metadata       Write video metadata to file if specified.
  --skip-existing       Skip downloading videos that already exist.
  --no-folders          Download all videos to the current directory without creating user folders.
  --output-dir OUTPUT_DIR
                        Specify the output directory for downloads. (Default: current directory)
```

## How To Use
Paste all the TikTok video links you want to download into a .txt file (one link per line), save it and follow the basic usage examples. 
In the example below, the links are saved in a links.txt file:
```
https://www.tiktok.com/@inter/video/7249049165169315098
https://www.tiktok.com/@inter/video/7247579800242588954
https://www.tiktok.com/@therock/video/7141037553196502318
https://www.tiktok.com/@realmadrid/photo/7375648582063459616
```

### Basic Usage Examples
Run the following commands according to how you want your videos to be downloaded
1. `python multitok.py` : Downloads the videos with default options. It assumes that you want to download watermark free videos and the links are in the links.txt file.

2. `python multitok.py --watermark`: Downloads the watermarked version of the videos. It assumes that the links are in the links.txt file.

3. `python multitok.py --no-watermark`: Downloads the watermark free version of the videos. It assumes that the links are in the links.txt file.

4. `python multitok.py --no-watermark --links example.txt`: Downloads the watermark free version of the videos by using the links in example.txt file.

5. `python multitok.py --watermark --links example.txt --workers 8`: Downloads the watermarked version of the videos by using the links in the `example.txt` file. 8 videos will be downloaded at a time.

6. `python multitok.py --save-metadata`: Saves the metadata of the downloaded videos into the metadata folder.

7. `python multitok.py --api-version v2`: Downloads the videos using the v2 api. v1 can be be used in case v2 isn't working. 

8. `python multitok.py --watermark --links example.txt --workers 4 --api-version v2 --save-metadata`: Downloads the watermarked version of the videos using links in the `example.txt` file and api v2. 4 videos are downloaded at a time and the metadata is saved into the metadata folder. 

9. `python multitok.py --output-dir /home/ubuntu/example`: Videos will be downloaded into the `/home/ubuntu/example` directory.

10. `python multitok.py --skip-existing --no-folders`: No user folders will be created and videos that have already being downloaded will be skipped.

### Note
* A folder will be created for each unique user. This folder will contain the downloaded videos. Use `--no-folders` to download all videos to the current directory without creating user folders.
* Videos that have been previously downloaded will be replaced when the script is run again. Use `--skip-existing` to skip downloading videos that already exist.
* The videos are saved and renamed according to their video IDs.
* Any link that had an error will be logged in an errors.txt file.
