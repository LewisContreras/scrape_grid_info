import os
import csv
import pdfplumber

PDF_FOLDER = "downloaded_pdfs"
OUTPUT_CSV = "power_supply_position.csv"

def extract_table_from_pdf(pdf_path):
    extracted_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words()
            c_position, d_position = None, None

            for i in range(len(words)):
                if (
                    i + 3 < len(words)
                    and words[i]["text"] == "C."
                    and words[i + 1]["text"] == "Power"
                    and words[i + 2]["text"] == "Supply"
                ):
                    c_position = words[i]["top"]

                if (
                    i + 2 < len(words)
                    and words[i]["text"] == "D."
                    and words[i + 1]["text"] == "Transnational"
                    and words[i + 2]["text"] == "Exchanges"
                ):
                    d_position = words[i]["top"]
                    break

            if c_position is None or d_position is None:
                print(f"Headers not found correctly on page {page.page_number}")
                continue


            cropped_page = page.within_bbox((0, c_position, page.width, d_position))
            table = cropped_page.extract_table()
            if table:
                for row in table[1:]:
                    if any(row):
                        extracted_data.append(row)
    return extracted_data


def process_data(raw_data):
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
        }
        processed_data.append(processed_row)
    return processed_data

def write_to_csv(data, output_file):
    if not data:
        print("No data to write.")
        return

    keys = data[0].keys()
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Data written to {output_file}")

def main():
    all_data = []
    cont = 0
    for year in range(2022, 2025):
        year_folder = os.path.join(PDF_FOLDER, str(year))
        if not os.path.exists(year_folder):
            print(f"Folder not found: {year_folder}")
            continue

        for pdf_file in os.listdir(year_folder):
            if cont == 5:
                break
            if pdf_file.endswith(".pdf"):
                cont += 1
                pdf_path = os.path.join(year_folder, pdf_file)
                print(f"Processing: {pdf_path}")
                raw_data = extract_table_from_pdf(pdf_path)
                all_data.extend(process_data(raw_data))

    write_to_csv(all_data, OUTPUT_CSV)

if __name__ == "__main__":
    main()
