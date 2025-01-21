import os
from datetime import date, timedelta
import aiohttp
import asyncio
from bs4 import BeautifulSoup

BASE_URL = "https://report.grid-india.in/"
DATE_FORM_URL = f"{BASE_URL}/psp_report.php"
PDF_FOLDER = "downloaded_pdfs"

# Create folders for storing PDFs
def setup_folders():
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
    for year in range(2014, 2025):
        year_folder = os.path.join(PDF_FOLDER, str(year))
        if not os.path.exists(year_folder):
            os.makedirs(year_folder)

# Download a file asynchronously
async def download_file(session, url, folder):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            filename = os.path.join(folder, url.split("/")[-1])
            with open(filename, "wb") as file:
                while chunk := await response.content.read(1024):
                    file.write(chunk)
            print(f"Downloaded: {filename}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

# Get PDF URL for a specific date asynchronously
async def get_pdf_url(session, target_date):
    formatted_date = target_date.strftime("%Y-%m-%d")
    try:
        async with session.post(DATE_FORM_URL, data={"selected_date": formatted_date}) as response:
            soup = BeautifulSoup(await response.text(), "html.parser")
            iframe = soup.find("iframe", class_="pdf-frame")
            if iframe and "src" in iframe.attrs:
                pdf_url = iframe["src"]
                if not pdf_url.startswith("http"):
                    pdf_url = BASE_URL + pdf_url
                return (pdf_url, target_date.year)
    except Exception as e:
        print(f"Failed to get PDF URL for {formatted_date}: {e}")
    return None

# Process a single date asynchronously
async def process_date(session, target_date):
    result = await get_pdf_url(session, target_date)
    if result:
        pdf_url, year = result
        year_folder = os.path.join(PDF_FOLDER, str(year))
        await download_file(session, pdf_url, year_folder)
    else:
        print(f"No PDF found for {target_date.strftime('%Y-%m-%d')}")

# Main asynchronous function
async def main():
    setup_folders()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for year in range(2014, 2025):
            start_date = date(year, 1, 1)
            end_date = date(year, 1, 31)
            dates_to_process = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
            for target_date in dates_to_process:
                tasks.append(process_date(session, target_date))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
