import pandas as pd

csv_files = [
    "datasets/csv/slng_data_main.csv",
    "datasets/csv/kamusalay.csv",
    "datasets/csv/slang_indo.csv",
    "datasets/csv/slang-indo.csv",
    "datasets/csv/kbba.csv",
    "datasets/csv/combined_slang_words.csv"
]

possible_slang_cols = ["slang", "alay", "kata", "word", "slang_word"]
possible_translation_cols = ["translationID", "formal", "baku", "arti", "translation", "meaning"]

def find_column(columns, possible_names):
    for col in columns:
        if col.lower().strip() in [name.lower() for name in possible_names]:
            return col
    return None

combined_list = []

for path in csv_files:
    try:
        df = pd.read_csv(path)
    except Exception:
        df = pd.read_csv(path, encoding="utf-8-sig")
    
    slang_col = find_column(df.columns, possible_slang_cols)
    translation_col = find_column(df.columns, possible_translation_cols)
    
    if slang_col and translation_col:
        sub_df = df[[slang_col, translation_col]].copy()
        sub_df.columns = ["slang", "translationID"]
        combined_list.append(sub_df)
        print(f"{path}: kolom terdeteksi -> slang='{slang_col}', translation='{translation_col}'")
    else:
        print(f"{path}: kolom tidak cocok, dilewati (kolom: {list(df.columns)})")

if combined_list:
    combined_df = pd.concat(combined_list, ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset="slang", keep="first")

    combined_df["slang"] = combined_df["slang"].astype(str).str.lower().str.strip()
    combined_df["translationID"] = combined_df["translationID"].astype(str).str.strip()

    combined_df.to_csv("datasets/slng_data_combined.csv", index=False)
    print(f"\nSuccess: Dataset gabungan berhasil disimpan ke 'slng_data_combined.csv' dengan {len(combined_df)} baris.")
else:
    print("Error: Tidak ada dataset yang valid ditemukan.")
