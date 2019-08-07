import scrape_tools


def main():
    debate_url = "https://www.rev.com/blog/transcript-from-night-2-of-the-2019-democratic-debates"
    candidate_dir = "inputs/debate_1_night_2_.txt"
    proctor_dir = "inputs/debate_1_proctor.txt"
    output_name = "output/debate_1_night_2.csv"

    night, debate = scrape_tools.get_night_debate(candidate_dir)
    candidates = scrape_tools.read_name_list(candidate_dir)
    proctors = scrape_tools.read_name_list(proctor_dir)

    transcript = scrape_tools.scrape_rev(debate_url)
    transcript_list = scrape_tools.rev_to_list(transcript, candidates, proctors)
    transcript_df = scrape_tools.list_to_df(transcript_list)
    transcript_df = scrape_tools.clean_df(transcript_df)

    transcript_df.to_csv(output_name)


if __name__ == '__main__':
    main()


