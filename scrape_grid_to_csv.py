from get_pdfs_from_web import main as get_pdfs
from from_pdf_to_csv import main as pdfs_to_csv
import asyncio

def main():
    asyncio.run(get_pdfs())
    pdfs_to_csv()

if __name__ == "__main__":
    main()
    