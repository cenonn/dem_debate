import re
from contextlib import closing

import pandas as pd
from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException


def get_page(url, headers=None):
    """copied from:
    https://realpython.com/python-web-scraping-practical-introduction/

    :param url: url to page to scape
    :type url: str
    :param headers: browser headers to pass to get(), defaults to None
    :type headers: dict, optional
    """
    try:
        with closing(get(url, stream=True, headers=headers)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        log_error('Error during request to {0} : {1}'.format(url, str(e)))


def is_good_response(resp):
    """copied from:
    https://realpython.com/python-web-scraping-practical-introduction/
    
    :param resp: response from get()
    :type resp: request.models.Response
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    copied from:
    https://realpython.com/python-web-scraping-practical-introduction/
    :param e: exception
    """
    print(e)


def scrape_rev(debate_url, tag_type="div", tag_class="uabb-infobox-text"):
    """scrape the debate transcript from rev.com
    
    :param debate_url: url to the debate transcript
    :type debate_url: str
    :param tag_type: type of html tag, defaults to "div"
    :type tag_type: str, optional
    :param tag_class: class of html tag, defaults to "uabb-infobox-text"
    :type tag_class: str, optional
    """
    raw_page = get_page(debate_url)
    debate_html = BeautifulSoup(raw_page, "html.parser")
    results = debate_html.find_all(tag_type, class_=tag_class)
    # the relevant information is at the 2nd spot in the list
    return results[1]


# TODO see if next debate will include timestamps, if so rewrite and get timestamps for night 2
def rev_to_list(transcript, candidates, proctors, tags="p"):
    """Return a list of all 'p' tags from rev page where the statement
    contains 2 or 3 elements
    
    :param transcript: transcript from scrape_rev()
    :type transcript: soup
    :param candidates: list of candidates
    :type candidates: list
    :param proctors: list of proctors or other speakers
    :type proctors: list
    :param tags: html tag where speaking is, defaults to "p"
    :type tags: str, optional
    """
    results = []
    for tag in transcript.select(tags, text=True, recursive=False):
        # this page has a bunch of \xa0 so replacing any string of 2 or more
        statement = re.sub(u"\xa0" + '{2,}', "|", tag.text)
        statement = statement.split("|")
        statement_len = len(statement)

        # maybe move part of this to another function?
        # may need to change depending on debate 2 webpage
        if statement_len > 1:
            if any(speaker in statement[0] for speaker in candidates):
                statement.append("candidate")
                if statement_len == 2:
                    statement.insert(1, "")
                    results.append(statement)
                elif statement_len == 3:
                    results.append(statement)
            elif any(speaker in statement[0] for speaker in proctors):
                statement.append("proctor")
                if statement_len == 2:
                    statement.insert(1, "")
                    results.append(statement)
                elif statement_len == 3:
                    results.append(statement)

    return results


def read_name_list(name_dir):
    """Read list of names
    
    :param name_dir: directory of name file
    :type name_dir: str
    """
    with open(name_dir) as name_file:
        return name_file.read().splitlines()


def list_to_df(rev_list):
    """Convert results from rev_to_list() to dataframe with candidates
    and statement column
    
    :param rev_list: list from rev_to_list()
    :type rev_list: list
    """
    headers = ["speaker", "timestamp", "statement", "speaker_type"]
    return pd.DataFrame(rev_list, columns=headers)


# TODO create statement number column based on index
def process_debate(debate_url, candidate_dir, proctor_dir, name_dict):
    """Create dataframe of debate using above helper functions.
    Process debate by stripping spaces, remapping names, and 
    adding night and debate number columns.
    
    :param debate_url: url to debate
    :type debate_url: str
    :param candidate_dir: directory to candidate list
    :type candidate_dir: str
    :param proctor_dir: directory to proctor list
    :type proctor_dir: str
    :param name_dict: directionary for mapping
    :type name_dict: dict
    """
    night, debate = get_night_debate(candidate_dir)

    candidates = read_name_list(candidate_dir)
    proctors = read_name_list(proctor_dir)

    transcript = scrape_rev(debate_url)
    transcript_list = rev_to_list(transcript, candidates, proctors)
    transcript_df = list_to_df(transcript_list)

    transcript_df["statement"] = transcript_df["statement"].str.strip()
    transcript_df["timestamp"] = transcript_df["timestamp"].str.strip()
    transcript_df["speaker"] = transcript_df["speaker"].str.replace(":", "")
    transcript_df["speaker"] = transcript_df["speaker"].str.replace(
        u"\u2019", "'")
    transcript_df["speaker"] = transcript_df["speaker"].map(name_dict)
    transcript_df["night"] = night
    transcript_df["debate"] = debate

    transcript_df.reset_index(inplace=True)
    transcript_df.rename(columns={"index": "statement_number"}, inplace=True)

    return transcript_df


def get_night_debate(candidate_dir):
    """Get debate and night numbers from candidate_dir string
    
    :param candidate_dir: directory to candidate list
    :type candidate_dir: str
    """
    dir_split = candidate_dir.split("_")
    return dir_split[1], dir_split[3]
