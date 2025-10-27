import pandas as pd
import json
import csv
import time
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

input_file = "datasets/slng_data_combined.csv"
output_file = "datasets/slng_data_seeded.csv"

df = pd.read_csv(input_file)

if os.path.exists(output_file):
    processed = pd.read_csv(output_file)
    done = set(processed["slang"].str.lower())
    print(f"Resuming from {output_file}, {len(done)} entries already processed.")
    mode = "a"  # append mode
else:
    done = set()
    mode = "w"  # write mode

with open(output_file, mode, newline="", encoding="utf-8") as f_out:
    writer = csv.DictWriter(
        f_out,
        fieldnames=[
            "slang",
            "translationID",
            "translationEN",
            "contextID",
            "contextEN",
            "exampleID",
            "exampleEN",
            "sentiment"
        ],
    )
    if mode == "w":
        writer.writeheader()

    for index, row in df.iterrows():
        slang = str(row["slang"]).strip()
        translationID = str(row["translationID"]).strip()

        if slang.lower() in done:
            print(f"[{index+1}/{len(df)}] Skipping already processed: {slang}")
            continue

        prompt = f"""
        Kamu adalah ahli linguistik bahasa Indonesia dan Inggris.
        Tugasmu adalah menulis entri kamus untuk slang berikut:
        Slang: "{slang}"
        Arti formal dalam bahasa Indonesia: "{translationID}"

        Keluarkan hasil dalam format JSON valid TANPA penjelasan tambahan.
        Pastikan:
        - "translationEN" adalah terjemahan natural dalam bahasa Inggris.
        - "contextID" berisi PENJELASAN SINGKAT tentang bagaimana slang ini digunakan, kapan dipakai, atau nuansa emosionalnya (bukan kalimat contoh).
        - "contextEN" adalah versi bahasa Inggris dari penjelasan tersebut.
        - "exampleID" berisi SATU kalimat contoh alami dalam bahasa Indonesia yang menggunakan slang itu.
        - "exampleEN" adalah terjemahan natural dari kalimat contoh tersebut.
        - "sentiment" adalah salah satu dari: "positive", "negative", atau "neutral", menggambarkan nada umum slang tersebut. Kamu harus menilai ini berdasarkan arti dan penggunaan slang. Satu slang bisa memiliki sentimen yang berbeda tergantung konteksnya, jadi pilih yang paling sesuai.

        Format JSON wajib:
        {{
          "translationEN": "...",
          "contextID": "...",
          "contextEN": "...",
          "exampleID": "...",
          "exampleEN": "...",
          "sentiment": "..."
        }}

        Contoh gaya jawaban yang diharapkan (tapi jangan gunakan isinya):
        {{
          "translationEN": "nosy / overly curious",
          "contextID": "Dari singkatan 'knowing every particular object', digunakan untuk orang yang terlalu ingin tahu urusan orang lain.",
          "contextEN": "Derived from 'knowing every particular object'; refers to someone who is overly curious about others’ business.",
          "exampleID": "Duh kepo banget sih lu.",
          "exampleEN": "You're so nosy, dude."
          "sentiment": "neutral"
        }}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )

            answer = response.choices[0].message.content.strip()

            if not answer:
                print(f"Empty response for '{slang}'")
                continue

            if answer.startswith("```"):
                answer = answer.strip("`").replace("json", "").strip()

            try:
                data = json.loads(answer)
            except json.JSONDecodeError:
                print(f"Invalid JSON for '{slang}': {answer[:80]}...")
                continue

            writer.writerow({
                "slang": slang,
                "translationID": translationID,
                "translationEN": data.get("translationEN", "").strip(),
                "contextID": data.get("contextID", "").strip(),
                "contextEN": data.get("contextEN", "").strip(),
                "exampleID": data.get("exampleID", "").strip(),
                "exampleEN": data.get("exampleEN", "").strip(),
                "sentiment": data.get("sentiment", "").strip()
            })

            f_out.flush()
            print(f"[{index+1}/{len(df)}] ✅ Processed: {slang}")

        except Exception as e:
            print(f"Error processing '{slang}': {e}")
            time.sleep(5)

        time.sleep(1.2)

print(f"Successfully seeded data to '{output_file}'")
