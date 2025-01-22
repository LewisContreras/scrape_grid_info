# Scrape Grid Info

This project is a Python-based tool to scrape energy production and consumption data from Indian grid reports. It downloads PDF reports, extracts the relevant tables, and consolidates the information into a CSV file (`power_supply_position.csv`) for further analysis.

## Project Overview

The script:
- Fetches PDF files containing energy data and stores them in the `downloaded_pdfs` directory.
- Extracts the "Power Supply Position in States" table from the PDFs.
- Compiles the data into a CSV file named `power_supply_position.csv`.

The script takes a few minutes to run depending on your system and network speed (approximately one minute on a modern machine).

---

## Prerequisites

Ensure you have the following installed:

- Python 3.10.12 (other Python 3.10 versions may also work)
- Pip (Python package manager)

---

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone git@github.com:LewisContreras/scrape_grid_info.git
   cd scrape_grid_info
   ```

2. **Create a Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # For Linux/MacOS
    venv\Scripts\activate     # For Windows
   ```

3. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
   ```

---

## Running the Script

To run the script, execute the following command:
  ```bash
    python scrape_grid_to_csv.py
  ```
## What to Expect:
- The script downloads PDF files to the `downloaded_pdfs`  directory.
- It processes the PDFs to extract relevant data.
- A `power_supply_position.csv` file is created in the root of the project.

---

## Notes
- The script has been tested with Python 3.10.12.
- If you encounter any issues, ensure all dependencies are installed correctly and that your Python environment matches the required version.
- Ensure a stable internet connection to allow the script to fetch the PDFs.
  