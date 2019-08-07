import sqlite3

import pandas as pd


def main():
    # night 1
    input_dir = "output/debate_1_combined.csv"
    db_name = "dem_debate.db"

    transcript_df = pd.read_csv(input_dir)
    con = sqlite3.connect(db_name)
    transcript_df.to_sql(
        name="transcripts", 
        con=con, 
        if_exists='append', 
        index=False)


if __name__ == "__main__":
    main()
