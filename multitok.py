import requests
from parsel import Selector
import argparse
import os
from tqdm import tqdm
from concurrent import futures
import re

parser = argparse.ArgumentParser(description="Multitok: A simple script that downloads TikTok videos concurrently.")
watermark_group = parser.add_mutually_exclusive_group()
parser.add_argument("--links", default="links.txt", help="The path to the .txt file that contains the TikTok links. (Default: links.txt)")
watermark_group.add_argument("--no-watermark", action="store_true", help="Download videos without watermarks. (Default)")
watermark_group.add_argument("--watermark", action="store_true", help="Download videos with watermarks.")
parser.add_argument("--workers", default=3, help="Number of concurrent downloads. (Default: 3)", type=int)
parser.add_argument("--api-version", choices=['v1', 'v2'], default='v2', help="API version to use for downloading videos. (Default: v2)")
args = parser.parse_args()

def extract_video_id(url):
    username_pattern = r"@([A-Za-z0-9_.]+)"
    content_type_pattern = r"/(video|photo)/(\d+)"

    username_match = re.search(username_pattern, url)
    username = username_match.group(0)

    content_type_match = re.search(content_type_pattern, url)
    content_type = content_type_match.group(1)
    video_id = content_type_match.group(2)

    return username, video_id, content_type

def downloader(file_name, link, response, extension):
    file_size = int(response.headers.get("content-length", 0))
    folder_name = extract_video_id(link)[0]

    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
        print(f"Folder created: {folder_name}\n")

    with open(f"{folder_name}/{file_name}.{extension}", 'wb') as file, tqdm(
        total=file_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
        bar_format='{percentage:3.0f}%|{bar:20}{r_bar}{desc}', colour='green', desc=f"[{file_name}]"
    ) as progress_bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            progress_bar.update(size)


def download_v2(link):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Sec-Fetch-Site': 'same-origin',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://musicaldown.com',
    'Connection': 'keep-alive',
    'Referer': 'https://musicaldown.com/en?ref=more',
    }

    if 'vm.tiktok.com' in link:
        response = requests.get(link, headers=headers)
        link = response.url

    _, file_name, content_type = extract_video_id(link)

    with requests.Session() as s:
        try:
            r = s.get("https://musicaldown.com/en", headers=headers)

            selector = Selector(text=r.text)

            token_a = selector.xpath('//*[@id="link_url"]/@name').get()
            token_b = selector.xpath('//*[@id="submit-form"]/div/div[1]/input[2]/@name').get()
            token_b_value = selector.xpath('//*[@id="submit-form"]/div/div[1]/input[2]/@value').get()

            data = {
                token_a: link,
                token_b: token_b_value,
                'verify': '1',
            }

            response = s.post('https://musicaldown.com/download', headers=headers, data=data)

            selector = Selector(text=response.text)

            if content_type == "video":
                watermark = selector.xpath('/html/body/div[2]/div/div[3]/div[2]/a[4]/@href').get()
                no_watermark = selector.xpath('/html/body/div[2]/div/div[3]/div[2]/a[1]/@href').get()

                download_link = watermark if args.watermark else no_watermark

                response = s.get(download_link, stream=True, headers=headers)

                downloader(file_name, link, response, extension="mp4")
            else:
                download_links = selector.xpath('//div[@class="card-image"]/img/@src').getall()
                
                for index, download_link in enumerate(download_links):
                    response = s.get(download_link, stream=True, headers=headers)
                    downloader(f"{file_name}_{index}", link, response, extension="jpeg")

        except Exception as e:
            print(f"\033[91merror\033[0m: {link} - {str(e)}")
            with open("errors.txt", 'a') as error_file:
                error_file.write(link + "\n")


def download_v1(link):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.4',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://tmate.cc',
    'Connection': 'keep-alive',
    'Referer': 'https://tmate.cc/',
    'Sec-Fetch-Site': 'same-origin',
    }

    if 'vm.tiktok.com' in link:
        response = requests.get(link, headers=headers)
        link = response.url

    _, file_name, content_type = extract_video_id(link)

    with requests.Session() as s:
        try:
            response = s.get("https://tmate.cc/", headers=headers)

            selector = Selector(response.text)
            token = selector.css('input[name="token"]::attr(value)').get()
            data = {'url': link, 'token': token}

            response = s.post('https://tmate.cc/action', headers=headers, data=data).json()["data"]
            
            selector = Selector(text=response)

            if content_type == "video":
                download_link_index = 3 if args.watermark else 0
                download_link = selector.css('.downtmate-right.is-desktop-only.right a::attr(href)').getall()[download_link_index]

                response = s.get(download_link, stream=True, headers=headers)

                downloader(file_name, link, response, extension="mp4")
            else:
                download_links = selector.css('.card-img-top::attr(src)').getall()
                for index, download_link in enumerate(download_links):
                    response = s.get(download_link, stream=True, headers=headers)

                    downloader(f"{file_name}_{index}", link, response, extension="jpeg")

        except Exception:
            print(f"\033[91merror\033[0m: {link}")
            with open("errors.txt", 'a') as error_file:
                error_file.write(link + "\n")


if __name__ == "__main__":
    with open(args.links, "r") as links:
        tiktok_links = links.read().strip().split("\n")

    with futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        if args.api_version == 'v2':
            executor.map(download_v2, tiktok_links)
        elif args.api_version == 'v1':
            executor.map(download_v1, tiktok_links)
