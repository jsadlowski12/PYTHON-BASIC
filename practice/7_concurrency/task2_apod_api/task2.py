import requests
import os
from concurrent.futures import ThreadPoolExecutor

API_KEY = "EhL6LdJzceIKGSfxSW2WfbvTfx0EHOQnLELqkHsA"
APOD_ENDPOINT = "https://api.nasa.gov/planetary/apod"
OUTPUT_IMAGES = "./output_images"


def get_apod_metadata(start_date: str, end_date: str, api_key: str) -> list:
    response = requests.get(
        f"{APOD_ENDPOINT}?api_key={api_key}&start_date={start_date}&end_date={end_date}"
    )
    return response.json()


def download_image(day: dict):
    print(f"Downloading {day['date']}")
    img = requests.get(day["url"])

    file_ext = day["url"].split(".")[-1]
    if file_ext not in ["jpg", "jpeg", "png", "gif"]:
        file_ext = "jpg"

    with open(f"{OUTPUT_IMAGES}/{day['date']}.{file_ext}", "wb") as f:
        f.write(img.content)


def download_apod_images(metadata: list):
    images_only = [day for day in metadata if day["media_type"] == "image"]
    print(f"Found {len(images_only)} images to download")

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(download_image, images_only)


def main():
    metadata = get_apod_metadata(
        start_date="2021-08-01",
        end_date="2021-09-30",
        api_key=API_KEY,
    )
    download_apod_images(metadata)
    print("Download complete!")


if __name__ == "__main__":
    if not os.path.exists(OUTPUT_IMAGES):
        os.makedirs(OUTPUT_IMAGES)
    main()