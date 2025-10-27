import pandas as pd

df = pd.read_csv("datasets/slng_data_seeded.csv")

df.to_json("datasets/slng_data_seeded_updated.json", orient="records", force_ascii=False, indent=2)