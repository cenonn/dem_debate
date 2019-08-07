import json

import pandas as pd

import scrape_tools


def main():
    debate_url_1 = "https://www.rev.com/blog/transcript-from-first-night-of-democratic-debates"
    candidate_dir_1 = "inputs/debate_1_night_1_.txt"

    debate_url_2 = "https://www.rev.com/blog/transcript-from-night-2-of-the-2019-democratic-debates"
    candidate_dir_2 = "inputs/debate_1_night_2_.txt"

    proctor_dir = "inputs/debate_1_proctor.txt"
    name_dir = "inputs/name_map.json"
    output_name = "output/debate_1_combined.csv"

    with open(name_dir, "r") as name_map:
        name_dict = json.load(name_map)

    night1_df = scrape_tools.process_debate(debate_url_1,
                                            candidate_dir_1,
                                            proctor_dir,
                                            name_dict)
    night2_df = scrape_tools.process_debate(debate_url_2,
                                            candidate_dir_2,
                                            proctor_dir,
                                            name_dict)

    transcript_df = pd.concat([night1_df, night2_df])

    transcript_df.to_csv(output_name, index=False)


if __name__ == '__main__':
    main()
