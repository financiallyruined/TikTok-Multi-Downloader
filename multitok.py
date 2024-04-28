import requests
from bs4 import BeautifulSoup
from concurrent import futures
from tqdm import tqdm
import argparse
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.4',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://tmate.cc',
    'Connection': 'keep-alive',
    'Referer': 'https://tmate.cc/',
}

parser = argparse.ArgumentParser(description="Multitok: A simple script that downloads TikTok videos concurrently.")
watermark_group = parser.add_mutually_exclusive_group()
parser.add_argument("--links", default="links.txt", help="The path to the .txt file that contains the TikTok links. (Default: links.txt)")
watermark_group.add_argument("--no-watermark", action="store_true", help="Download videos without watermarks. (Default)")
watermark_group.add_argument("--watermark", action="store_true", help="Download videos with watermarks.")
parser.add_argument("--workers", default=3, help="Number of concurrent downloads. (Default: 3)", type=int)

args = parser.parse_args()

def downloader(file_name, link, response, extension):
    file_size = int(response.headers.get("content-length", 0))
    folder_name = link.split("/")[-3]

    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
        print(f"Folder created: {folder_name}\n")

    with open(f"{folder_name}/{file_name}.{extension}", 'wb') as video_file, tqdm(
        total=file_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
        bar_format='{percentage:3.0f}%|{bar:20}{r_bar}{desc}', colour='green', desc=f"[{file_name}]"
    ) as progress_bar:
        for data in response.iter_content(chunk_size=1024):
            size = video_file.write(data)
            progress_bar.update(size)


with open(args.links, "r") as links:
    tiktok_links = links.read().split("\n")


    def download(link):
        with requests.Session() as s:
            try:
                response = s.get("https://tmate.cc/", headers=headers)

                soup = BeautifulSoup(response.content, 'html.parser')
                token = soup.find("input", {"name": "token"})["value"]
                data = {'url': link, 'token': token,}

                response = s.post('https://tmate.cc/action', headers=headers, data=data).json()["data"]

                soup = BeautifulSoup(response, 'html.parser')

                if not "photo" in link:
                    download_link_index = 3 if args.watermark else 0
                    file_name = link.split("/")[-1]
                    download_link = soup.find(class_="downtmate-right is-desktop-only right").find_all("a")[download_link_index]["href"]
                    response = s.get(download_link, stream=True, headers=headers)

                    downloader(file_name, link, response, extension="mp4")
                else:
                    download_links = [i["src"] for i in soup.find_all(class_="card-img-top")]
                    for index, download_link in enumerate(download_links):
                        file_name = f"{link.split('/')[-1]}_{index}"
                        response = s.get(download_link, stream=True, headers=headers)

                        downloader(file_name, link, response, extension="jpeg", )

            except Exception:
                print(f"\033[91merror\033[0m: {link}")
                with open("errors.txt", 'a') as error_file:
                    error_file.write(link + "\n")

if __name__ == "__main__":                
    with futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        executor.map(download, tiktok_links)
