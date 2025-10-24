import csv
import json
import os

def convert_to_csv_from_txt(input_file, output_file):
    data = []

    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read().strip()

        if text.startswith("{") and text.endswith("}"):
            print("Detected JSON dictionary format")
            data_dict = json.loads(text)
            for slang, translation in data_dict.items():
                data.append({"slang": slang.strip(), "translationID": str(translation).strip()})

        else:
            print("Detected text/tab-separated format")
            for line in text.splitlines():
                if not line.strip():
                    continue
                parts = line.split("\t")
                if len(parts) >= 2:
                    slang = parts[0].strip()
                    translation = parts[1].strip()
                    data.append({"slang": slang, "translationID": translation})

    with open(output_file, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["slang", "translationID"])
        writer.writeheader()
        writer.writerows(data)

    print(f"✅ Successfully converted '{input_file}' → '{output_file}' ({len(data)} entries)")

files = [
    "datasets/txt/kbba.txt",
    "datasets/txt/combined_slang_words.txt"
]

for file_path in files:
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = f"datasets/csv/{base_name}.csv"
    convert_to_csv_from_txt(file_path, output_path)
