import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep

API_URL = "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env','HuggingFaceAPIKey')}"}
print(get_key('.env', 'HuggingFaceAPIKey'))

async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.text}")
        return None
    return response.content

async def generate_images(prompt: str):
    check_and_create_folder()  # Ensure the folder exists
    tasks = []

    for _ in range(4):
        payload = {
            "inputs": f"{prompt},quality=4K, sharpness=maximum, Ultra High details,high resolution,seed = {randint(0, 1000000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes is not None:
            with open(fr"Data\{prompt.replace(' ','_')}{i + 1}.jpg", "wb") as f:
                f.write(image_bytes)
        else:
            print(f"Error generating image {i + 1}")

async def open_images(prompt):
    folder_path = r"Data"
    prompt = prompt.replace(" ", "_")
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)
        
        if not os.path.exists(image_path):
            print(f"File does not exist: {image_path}")
            continue
        
        try:
            img = Image.open(image_path)
            print(f"Opening Image: {image_path}")
            img.show()
            await asyncio.sleep(1)
        except IOError:
            print(f"Unable to open {image_path}")

def check_and_create_folder():
    folder_path = r"Data"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")

async def main():
    while True:
        try:
            with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
                Data: str = f.read()

            Prompt, Status = Data.split(",")   

            if Status == "True":
                print("Generating Images ...")
                await generate_images(prompt=Prompt)
                await open_images(prompt=Prompt)

                with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                    f.write("False,False")
                    break
            else:
                await asyncio.sleep(1)
        except FileNotFoundError as e:
            print(f"File not found: {e}")
            await asyncio.sleep(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            await asyncio.sleep(1)

# Run the main loop
if __name__ == "__main__":
    asyncio.run(main())  # Start the event loop here
