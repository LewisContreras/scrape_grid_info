import os
import csv
import pdfplumber
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor
import logging

PDF_FOLDER = "downloaded_pdfs"
OUTPUT_CSV = "power_supply_position.csv"

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)


def extract_table_from_pdf(pdf_path):
    extracted_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words()
            c_position, d_position = None, None

            for i in range(len(words)):
                if i + 3 < len(words) and (
                    (
                        words[i]["text"] == "C."
                        and words[i + 1]["text"] == "Power"
                        and words[i + 2]["text"] == "Supply"
                    )
                    or (
                        words[i]["text"] == "C.Power"
                        and words[i + 1]["text"] == "Supply"
                    )
                ):
                    c_position = words[i]["top"]

                if i + 2 < len(words) and (
                    (
                        words[i]["text"] == "D."
                        and words[i + 1]["text"] == "Transnational"
                        and words[i + 2]["text"] == "Exchanges"
                    )
                    or (
                        words[i]["text"] == "D.Transnational"
                        and words[i + 1]["text"] == "Exchanges"
                    )
                ):
                    d_position = words[i]["top"]
                    break

            if c_position is None or d_position is None:
                continue

            cropped_page = page.within_bbox((0, c_position, page.bbox[2], d_position))
            table = cropped_page.extract_table()
            if table:
                for row in table[1:]:
                    if any(row):
                        extracted_data.append(row)
                return extracted_data

    logging.error(f"Table not found in PDF: {pdf_path}")
    return extracted_data


def propagate_region(data):
    current_region = None
    for row in data:
        if row["Region"]:
            current_region = row["Region"]
        else:
            row["Region"] = current_region
    return data


def process_data(raw_data, date):
    processed_data = []
    for row in raw_data:
        while len(row) < 9:
            row.append(None)

        processed_row = {
            "Region": row[0],
            "State": row[1],
            "Max_Demand_Met_Day_MW": row[2],
            "Shortage_Max_Demand_MW": row[3],
            "Energy_Met_MU": row[4],
            "Drawal_Schedule_MU": row[5],
            "OD_UD_MU": row[6],
            "Max_OD_MW": row[7],
            "Energy_Shortage_MU": row[8],
            "Date": date,
        }
        processed_data.append(processed_row)
    return processed_data


def write_to_csv(data, output_file):
    if not data:
        logging.warning("No data to write.")
        return

    keys = data[0].keys()
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    logging.info(f"Data written to {output_file}")


def extract_date_from_filename(filename):
    try:
        date_part = filename.split("_")[0]
        parsed_date = datetime.strptime(date_part, "%d.%m.%y")
        return parsed_date.strftime("%Y-%m-%d")
    except ValueError:
        logging.error(f"Error parsing date from filename: {filename}")
        return "Unknown"


def process_pdf_file(pdf_file, year_folder):
    pdf_path = os.path.join(year_folder, pdf_file)
    date = extract_date_from_filename(pdf_file)
    raw_data = extract_table_from_pdf(pdf_path)
    return process_data(raw_data, date)


def main():
    all_data = []
    tasks = []

    with ProcessPoolExecutor() as executor:
        for year in range(2014, 2025):
            year_folder = os.path.join(PDF_FOLDER, str(year))
            if not os.path.exists(year_folder):
                logging.warning(f"Folder not found: {year_folder}")
                continue

            for pdf_file in os.listdir(year_folder):
                if pdf_file.endswith(".pdf"):
                    tasks.append(
                        executor.submit(process_pdf_file, pdf_file, year_folder)
                    )

        for future in tasks:
            try:
                result = future.result()
                all_data.extend(result)
            except Exception as e:
                logging.error(f"Error processing file: {e}")

    all_data = propagate_region(all_data)
    write_to_csv(all_data, OUTPUT_CSV)


if __name__ == "__main__":
    main()
