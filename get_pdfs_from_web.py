import os
import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta


BASE_URL = "https://report.grid-india.in/" 
DATE_FORM_URL = f"{BASE_URL}/psp_report.php"
PDF_FOLDER = "downloaded_pdfs"

# Create folders for storing PDFs
def setup_folders():
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
    for year in range(2022, 2025):
        year_folder = os.path.join(PDF_FOLDER, str(year))
        if not os.path.exists(year_folder):
            os.makedirs(year_folder)

# Download a file from a URL
def download_file(url, folder):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        filename = os.path.join(folder, url.split("/")[-1])
        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f"Downloaded: {filename}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

# Scrape PDF files for a specific date
def scrape_date(session, target_date):
    formatted_date = target_date.strftime("%Y-%m-%d")
    response = session.post(DATE_FORM_URL, data={"selected_date": formatted_date})
    soup = BeautifulSoup(response.text, "html.parser")

    # Locate the iframe containing the PDF
    iframe = soup.find("iframe", class_="pdf-frame")
    if iframe and "src" in iframe.attrs:
        pdf_url = iframe["src"]
        if not pdf_url.startswith("http"):
            pdf_url = BASE_URL + pdf_url
        year_folder = os.path.join(PDF_FOLDER, str(target_date.year))
        download_file(pdf_url, year_folder)
    else:
        print(f"No PDF found for {formatted_date}")

# Main script
def main():
    setup_folders()

    with requests.Session() as session:
        for year in range(2022, 2025):
            start_date = date(year, 1, 1)
            end_date = date(year, 1, 31)

            current_date = start_date
            while current_date <= end_date:
                print(f"Processing date: {current_date}")
                scrape_date(session, current_date)
                current_date += timedelta(days=1)

if __name__ == "__main__":
    main()
