import os
import re
import json

from contextlib import closing
from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException

import pandas as pd


def read_json(jsonfile):
    with open(jsonfile, 'r') as f:
        json_dict = json.load(f)

    return json_dict

def write_json(dictionary, jsonfile):
    with open(jsonfile, 'w') as f:
        json.dump(dictionary, f, indent=2)

def read_list(txtfile):
    with open(txtfile, 'r') as f:
        return f.read().splitlines()

def write_list(arr, txtfile):
    with open(txtfile, 'w') as f:
        for item in arr:
            f.write(item + '\n')


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


def p_has_a_child_ts(tag):
    """ Returns True if tag is <p> tag containing 2 or more 
    elements and has <a> tag child that links to a timestamp.
    """
    try:
        return (tag.name == 'p' 
                and tag.a 
                and tag.a['href'].find('ts=') > -1 
                and len(tag.contents) > 1)
    except AttributeError:
        return False
    except TypeError:
        return False

def scrape_rev(debate_url):
    """scrape the debate transcript from rev.com and returns 
    all tags based on above filter.

    :param debate_url: url to debate transcript
    :type debate_url: str
    """
    raw_page = get_page(debate_url)
    debate_html = BeautifulSoup(raw_page, "html.parser")
    transcipt = debate_html.find_all(p_has_a_child_ts)
    return transcipt


def build_tr_list(transcript):
    """ Creates clean list of statements by stripping spaces and 
    extracting speaker, timestamp, and statement from list of tags.

    :param transcript: transcript from scrape_rev()
    :type transcript: soup
    """

    tr_list = []
    for i in range(len(transcript)):
        stmt_list = list(transcript[i].descendants)

        speaker = stmt_list[0].split(':')[0].replace('\u2019', "'")
        timestamp = transcript[i].find('a').text
        statement = stmt_list[-1].replace('\xa0', "").lstrip()


        stmt_row = [i, speaker, timestamp, statement]

        tr_list.append(stmt_row)

    return tr_list

def tr_list_to_df(tr_list):
    """ Converts clean list of transcript statements into DataFrame.

    :param tr_list: transcipt from build_tr_list()
    :type tr_list: list
    """
    headers = ["statement_no", "speaker", "timestamp", "statement"]
    transcipt_df = pd.DataFrame(tr_list, columns=headers).set_index('statement_no')

    return transcipt_df


def rename_speaker(transcript_df):
    """ Replaces speaker with corresponding mapping from name_map.
    Requires name_map.json from update_speakers_json().

    :param transcript_df: DataFrame of transcipt from tr_list_to_df()
    :type transcript_df: DataFrame
    """
    name_dict = read_json("Input/name_map.json")

    transcript_df["speaker"] = transcript_df["speaker"].map(name_dict)

def get_speaker_type(speaker):
    """ Determines type of speaker.
    Requires candidates.txt and proctors.txt from get_names().

    :param speaker: speaker of statement
    :type speaker: str
    """
    candidate_list = read_list('Input/candidates.txt')
    proctor_list = read_list('Input/proctors.txt')

    if speaker in candidate_list:
        return "candidate"
    elif speaker in proctor_list:
        return "proctor"
    else:
        return "other"

def clean_df(transcript_df, debate_no, night_no):
    """ Remaps speaker names and inserts columns for 
    speaker type, debate number, and night number.

    :param transcript_df: DataFrame of transcript 
    :type transcript_df: DataFrame
    :param debate_no: debate number
    :type debate_no: int
    :param night_no: night number of debate
    :type night_no: int
    """
    rename_speaker(transcript_df)

    speaker_type_series = transcript_df.speaker.apply(get_speaker_type)
    transcript_df.insert(1, "speaker_type", speaker_type_series)

    transcript_df.insert(0, "debate", debate_no)
    transcript_df.insert(1, "night", night_no)


def update_speakers_json(debate_url):
    """ Scrapes transcript from rev.com and store all speakers as keys
    for remapping. Values are empty string to be manually entered.

    :param debate_url: url to debate transcript
    :type debate_url: str
    """
    name_dict = read_json("Input/name_map.json")

    transcript = scrape_rev(debate_url)

    for i in range(len(transcript)):
        stmt_list = list(transcript[i].descendants)
        speaker = stmt_list[0].split(':')[0].replace('\u2019', "'")

        if speaker not in name_dict:
            name_dict.update({speaker:""})

    write_json(name_dict, "Input/name_map.json")

def get_names():
    """ Scrapes candidates and proctors from wikipedia and
    writes them into txt files.
    """
    wiki = "https://en.wikipedia.org/wiki/2020_Democratic_Party_presidential_debates_and_forums"
    wiki_data = pd.read_html(wiki)

    # get list of candidates
    forum_df = wiki_data[28]
    candidates = forum_df.Candidate.Candidate.Candidate
    cand_list = candidates.to_list()

    # get list of proctors
    sched_mod = wiki_data[2]["Moderator(s)"]
    rx = re.compile(r'(?<=[a-z])(?=[A-Z])')

    proc_list=[]
    for sched in sched_mod:
        pr_names = rx.sub(',', sched).split(',')

        for name in pr_names:
            proctor = name.split('[')[0]
            if proctor != 'TBA': 
                proc_list.append(proctor.split(' ')[1])

    # remove duplicate proctors
    proc_list = set(proc_list)

    # save candidate and proctor lists
    write_list(cand_list, "Input/candidates.txt")
    write_list(proc_list, "Input/proctors.txt")


def scrape_prep(debate_url):
    """ Prepares necessary files before processing debate.

    :param debate_url: url to debate transcript
    :type debate_url: str
    """
    if not os.path.isdir("Output"):
        os.makedirs("Output")
    if not os.path.isdir("Input"):
        os.makedirs("Input")

    name_map_dir = "Input/name_map.json"
    if not os.path.exists(name_map_dir):
        with open(name_map_dir, 'w') as f:
            json.dump({}, f, indent=2)

    get_names()
    update_speakers_json(debate_url)

def process_debate(debate_url, debate, night):
    """ Creates csv of debate transcript using above helper functions. 
    Requires candidates.txt, proctors.txt, and name_map.json 
    to be up to date before using.

    :param debate_url: url to debate transcript
    :type debate_url: str
    :param debate: debate number
    :type debate: int
    :param night: night number of debate
    :type night: int
    """
    transcript = scrape_rev(debate_url)
    transcript_list = build_tr_list(transcript)
    transcript_df = tr_list_to_df(transcript_list)

    clean_df(transcript_df, debate, night)

    outfilepath = f"Output/debate_{debate}_night_{night}.csv"
    transcript_df.to_csv(outfilepath)
