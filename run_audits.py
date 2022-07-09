import os
import json
import argparse
import sys
import random
from datetime import datetime
from typing import Optional
from tracking_audit import Audit, DEFAULT_AUDIT_NAME, current_location

## Constants (mostly default args)
# number of browsers per treatment condition
BROWSER_N = 1
# Number of websites, if none all will be used
WEBSITES_N = None
# Seed profile
# SEED_PROFILE = "./resources/profile_archive/seed_with_lightbeam/profile.tar"
# SEED_PROFILE = "./resources/profile_archive/seed_idontcareaboutcookies/profile.tar"
# SEED_PROFILE = "./resources/profile_archive/clean_seed/profile.tar"
SEED_PROFILE = None

RANDOM_SEED = None

# path to the websites
WEBSITES_PATH = "./resources/governmental_websites/governmental_websites.json"

HEADLESS = True

## argument parser
def parse_args() -> dict:

    ## parse CLI args
    parser = argparse.ArgumentParser(
        prog="run_audits", description="Run a tracking audit."
    )
    # screenshots
    parser.add_argument(
        "-ss",
        "--store-screenshots",
        dest="store_screenshots",
        action="store_true",
        default=False,
        help="Should it take and store screenshots?",
    )
    # page source
    parser.add_argument(
        "-ps",
        "--store-source",
        dest="store_source",
        action="store_true",
        default=False,
        help="Should it extract and store the html documents of the pages visited?",
    )
    # location flag
    parser.add_argument(
        "-l",
        "--location",
        dest="location",
        nargs="?",
        type=str,
        default=None,
        help="Location used alias. Used for directory naming, does not actually start a vpn.",
    )
    # headless flag
    parser.add_argument(
        "-headless", dest="headless", action="store_true", help="Run headless?"
    )
    # number of websites flag
    parser.add_argument(
        "-n",
        "--n-websites",
        dest="websites_n",
        nargs="?",
        default=WEBSITES_N,
        help="Number of websites to use in the audit",
    )
    # number of websites flag
    parser.add_argument(
        "-b",
        "--browser-n",
        dest="browser_n",
        type=int,
        default=BROWSER_N,
        help="Number of browsers to use",
    )
    # max_cookies
    parser.add_argument(
        "-mc",
        "--max-cookies",
        dest="max_cookies",
        nargs="?",
        type=int,
        default=None,
        help="As a stoping rule, define a maximum number of cookies a bot is allowed to set. Once reached, the crawl will stop.",
    )
    # trial name
    parser.add_argument(
        "-name",
        "--trial-name",
        dest="trial_name",
        nargs="?",
        type=str,
        default="test_trial",
        help="Trail name to be used as a prefix to the name of the directory/db/profile of the crawl session",
    )
    # path to seed profile
    parser.add_argument(
        "-s",
        "--seed-profile",
        dest="path_to_seed_profile",
        nargs="?",
        type=str,
        default=SEED_PROFILE,
        help="Path to a compressed firefox profile to be used as the seed profile, e.g. 'profile_archive/clean_seed/profile.tar'",
    )
    # random seed
    parser.add_argument(
        "-r",
        "--random-seed",
        dest="random_seed",
        nargs="?",
        type=int,
        default=RANDOM_SEED,
        help="Random state seed integer to use while sampling.",
    )
    args_pprint = "\n".join(
        [f"{k} ---> {v}" for k, v in vars(parser.parse_args([])).items()]
    )
    # no args, notify that defaults will be used
    if len(sys.argv) == 1:
        print(f"[!] No arguments provided, going with the defaults:\n{args_pprint}")
    else:
        print(
            f"[+] Starting a new tracking audit with the following parameters:\n{args_pprint}"
        )

    args = parser.parse_args()
    return vars(args)


## crawler
def crawl(
    websites_n: Optional[int] = WEBSITES_N,
    browser_n: int = BROWSER_N,
    headless: bool = HEADLESS,
    location: str or None = None,
    trial_name: str = "test_crawl",
    max_cookies: Optional[int] = None,
    random_seed: Optional[int] = None,
    store_screenshots: bool = False,
    store_source: bool = False,
    **kwargs,
) -> None:
    """
    Run a crawler using openwpm
        websites_n: int or None; number of websites to crawl;
        browser_n: int; number of crawlers to visit the websites in parallel, set to 1 unless if focusing on tracking
        location: str; expressvpn alias. Check VPNHandler.get_aliases().
        trial_name: str; prefix to the directory/db of the crawl session, e.g. "pilot 2"
        max_cookies: int or None: stop after collect n cookies (a type of control)
        random_seed: it or None: random seed to use in sampling the websites if websites_n != None
        store_screenshots: bool: take a screenshot of the page visited
        store_source: bool: store source page of the page visited
    """
    ## prepare the name of the crawl audit used for the directory/db
    # the audit name will be trial_name + location (where applicable) + treatment + YYYYMMDDHH (for replications)
    # Make the audit name and add a time stamp following (_YYYYMMDDHHMM) for replications
    audit_name = trial_name
    if location:
        audit_name = "_".join([audit_name, location])
    audit_name = "_".join([audit_name, datetime.now().strftime("%Y%m%d")])
    ## read the websites
    with open(WEBSITES_PATH, "r", encoding="utf-8") as f:
        websites = json.load(f)
    # covert to list
    websites = [w.get("url") for _, w in websites.items()]
    # if user defined websites_n sample, else take all
    if websites_n:
        # if missing, generate the random seed
        if not random_seed:
            random_seed = random.randint(1, (2**32 - 1))  # random seed limit
        random.seed(int(random_seed))
        websites = random.sample(websites, int(websites_n))
    
    # shuffle
    random.shuffle(websites)
    ## Run the crawler
    # create an audit instance
    audit = Audit(
        websites=websites,
        headless = headless,
        audit_name=audit_name,
        browser_n=browser_n,
        max_cookies=max_cookies
    )
    # create the status file if missing
    status_file = os.path.join(audit.parent_output_dir, "crawl_done.txt")
    if not os.path.isfile(status_file):
        # start
        start = datetime.now().strftime("%Y%m%d%H%M")
        # crawl
        audit.crawl_audit(
            take_screenshot=store_screenshots, fetch_source_code=store_source
        )
        end = datetime.now().strftime("%Y%m%d%H%M")
        with open(status_file, "w") as fp:
            pass
        # clean up
        audit.clean_up()
        # fetch all the arguments passed to crawl turn to dict and export as audit.parent_output_dir/crawl_config.json
        config_dict = {
            "audit_name": audit_name,
            "websites_n": websites_n,
            "browser_n": browser_n,
            "location": location,
            "seed_profile_used": kwargs.get("path_to_seed_profile")
            if "path_to_seed_profile" in kwargs
            else None,
            "trial_name": trial_name,
            "max_cookies": max_cookies,
            "started_at": start,
            "ended_at": end,
            "random_seed": random_seed,
            "ran_from_location": current_location(),
        }
        # run the sanity check and add the results to the crawl config
        sanity_dict = audit.crawl_sanity_check()
        config_dict = {**config_dict, **sanity_dict}
        # write it to the crawls parent output directory
        with open(
            os.path.join(audit.parent_output_dir, "crawl_config.json"), "w+"
        ) as f:
            json.dump(config_dict, f, indent=4)


if __name__ == "__main__":
    ## parse CLI args
    args_dict = parse_args()
    ## run the crawl
    crawl(**args_dict)
