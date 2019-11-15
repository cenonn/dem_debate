import scrape_tools as st

def main():
    d1n1_url = "https://www.rev.com/blog/transcript-from-first-night-of-democratic-debates"
    d1n2_url = "https://www.rev.com/blog/transcript-from-night-2-of-the-2019-democratic-debates"

    d2n1_url = "https://www.rev.com/blog/transcript-of-july-democratic-debate-night-1-full-transcript-july-30-2019"
    d2n2_url = "https://www.rev.com/blog/transcript-of-july-democratic-debate-2nd-round-night-2-full-transcript-july-31-2019"

    d3n1_url = "https://www.rev.com/blog/democratic-debate-transcript-houston-september-12-2019"

    d4n1_url = "https://www.rev.com/blog/october-democratic-debate-transcript-4th-debate-from-ohio"


    # url_list = [d1n1_url, d1n2_url, d2n1_url, d2n2_url, d3n1_url, d4n1_url]
    # for url in url_list:
    #     st.scrape_prep(url)


    st.process_debate(d1n1_url, 1, 1)
    st.process_debate(d1n2_url, 1, 2)

    st.process_debate(d2n1_url, 2, 1)
    st.process_debate(d2n2_url, 2, 2)

    st.process_debate(d3n1_url, 3, 1)

    st.process_debate(d4n1_url, 4, 1)


if __name__=='__main__':
    main()