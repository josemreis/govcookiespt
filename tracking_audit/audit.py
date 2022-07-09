from pathlib import Path
import os
import random
import sqlite3
from typing import Optional
import pandas as pd
import sys
import time
from datetime import datetime
from .other_commands import ScheduleManager
from .constants import (
    GET_REQUEST_TIMEOUT,
    PATH_TO_OPENWPM,
    OUTPUT_DIR,
    PROFILES_SUBDIR,
    DEFAULT_AUDIT_NAME,
    SLEEP_TIME_UNIFORM_DIST_MAX,
    SLEEP_TIME_UNIFORM_DIST_MIN,
    ACTIVE_STATUS_START,
    ACTIVE_STATUS_STOP,
)
from .utils import _tar

sys.path.insert(0, PATH_TO_OPENWPM)
from openwpm.command_sequence import CommandSequence
from openwpm.commands.browser_commands import (
    GetCommand,
    ScreenshotFullPageCommand,
    RecursiveDumpPageSourceCommand,
)
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider
from openwpm.storage.leveldb import LevelDbProvider
from openwpm.task_manager import TaskManager


class Audit(object):
    """Create instance of audit object"""

    def __init__(
        self,
        headless: bool = False,
        websites: list or None = ["https://web.lip.pt/"],
        max_cookies: int or None = None,
        browser_n: int = 1,
        path_to_seed_profile: str or None = None,
        audit_name: str = DEFAULT_AUDIT_NAME,
        resources_to_save: Optional[str] = None,
        scrape_ads: bool = True,
        output_dir: str = OUTPUT_DIR,
        timeout=87000,
    ) -> None:
        """
        headless: bool; should the browser be launched in headless mode (see: https://github.com/mozilla/OpenWPM/blob/491262e9a9f1a9397abba47bc500f2495971bce4/docs/Configuration.md)
        websites: list; list of websites to crawl
        browser_n: int; number of crawlers
        path_to_seed_profile: str; path to the tar or tar.gz profile defaults to an existing profile in the folder /resources/profile_archive/[AUDIT_NAME], if missing it creates a new one
        audit_name: name of the output folder for this audit
        """
        # run the browser client in headless mode ?
        self.display_mode = "headless" if headless else "native"
        # how many browsers to run in parallel
        self.browser_n = browser_n
        # path to seed profile
        self.path_to_seed_profile = path_to_seed_profile
        # Make the audit name
        self.audit_name = audit_name
        # timeout for selenium
        self.timeout = timeout
        ## Create some relevant directories
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        # parent directory for the output
        parent_output_dir = os.path.join(output_dir, self.audit_name)
        if not os.path.isdir(parent_output_dir):
            os.mkdir(parent_output_dir)
        self.parent_output_dir = parent_output_dir
        # output sqlite database
        self.output_db = Path(
            os.path.join(parent_output_dir, self.audit_name + ".sqlite")
        )
        # output content db
        self.content_db = Path(os.path.join(parent_output_dir, "saved_content"))
        # comma-separated resources to save. On the resources see: https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/webRequest/ResourceType
        self.resources_to_save = resources_to_save
        # should we scrape ads using gpt api?
        self.scrape_ads = scrape_ads
        ## assign the websites
        # Remove websites already visited by the crawler from the list
        # if the database exists already, grab all the top_urls from the http_visits table
        if not websites and not self.search_engine_queries:
            raise TypeError("No websites were provided.")
        elif websites:
            self.websites = self.remove_already_visited(websites=websites)
            print(
                f'[+] Going to crawl the following websites: {", ".join(self.websites)}'
            )
        else:
            pass
        ## assignt the cookies ceiling
        self.max_cookies = max_cookies
        # profile sub-dir
        profile_subdir = os.path.join(PROFILES_SUBDIR, self.audit_name)
        self.profile_subdir = profile_subdir
        ## Define the manager parameters
        self.manager_config()
        ## Define the browser params
        self.browser_config()

    def remove_already_visited(self, websites: list) -> list or None:
        """Remove websites already visited from the websites list"""
        if os.path.isfile(self.output_db):
            conn = sqlite3.connect(self.output_db)
            cur = conn.cursor()
            already_visited = set()
            for url, top_url in cur.execute(
                "SELECT DISTINCT h.url, v.site_url "
                "FROM http_requests as h JOIN site_visits as v ON "
                "h.visit_id = v.visit_id;"
            ):
                already_visited.add(top_url)
            already_visited = list(already_visited)
            return [w for w in websites if w not in already_visited]
        else:
            return websites

    def get_failed_visits(self):
        """Fetch the visits which failed during the crawl"""
        """Count failed visits during the crawl"""
        query = """
        SELECT DISTINCT c.*, v.site_url
        FROM crawl_history as c JOIN site_visits as v ON
        c.visit_id = v.visit_id AND c.browser_id = v.browser_id
        WHERE c.command == "GetCommand" AND c.error IS NOT NULL;
        """
        with sqlite3.connect(self.output_db) as con:
            result = pd.read_sql_query(sql=query, con=con)
        return result[["browser_id", "visit_id", "site_url", "error", "retry_number"]]

    def count_cookies(self):
        """Count how many unique cookies we have already in the db. Unique if (host, name, value) is unique"""
        query = (
            """ SELECT count(*) FROM javascript_cookies GROUP BY host, name, value;"""
        )
        with sqlite3.connect(self.output_db) as con:
            result = pd.read_sql_query(sql=query, con=con)
        return result.shape[0]

    def crawl_sanity_check(self) -> dict:
        """
        1. total number of cookies,
        2. failed visits,
        3. number of failed visits
        """
        ## count the cookies collected
        cookie_count = self.count_cookies()
        ## failed visits
        failed = self.get_failed_visits()
        # turn to dict
        failed_dict = failed.to_dict("list")
        ## failed visits count
        failed_count = failed.shape[0]
        return {
            "total_cookies_collected": cookie_count,
            "failed_visits_count": failed_count,
            "failed_visits_dict": failed_dict,
        }

    def manager_config(self) -> None:
        # Loads the default ManagerParams and NUM_BROWSERS copies of the default BrowserParams
        manager_params = ManagerParams(num_browsers=self.browser_n)
        # Update TaskManager configuration (use this for crawl-wide settings)
        manager_params.data_directory = Path(self.parent_output_dir)
        manager_params.log_path = Path(
            os.path.join(self.parent_output_dir, f"{self.audit_name}.log")
        )
        # memory_watchdog and process_watchdog are useful for large scale cloud crawls.
        # Please refer to docs/Configuration.md#platform-configuration-options for more information
        manager_params.memory_watchdog = True
        manager_params.process_watchdog = True
        self.manager_params = manager_params

    def browser_config(self) -> None:
        # create a browser params instance for all browsers
        browser_params = [
            BrowserParams(display_mode=self.display_mode) for _ in range(self.browser_n)
        ]
        # define the remaining browser parameters
        for browser_param in browser_params:
            # browser profilek archive
            browser_param.profile_archive_dir = Path(self.profile_subdir)
            # Record HTTP Requests and Responses
            browser_param.http_instrument = True
            # Record cookie changes
            browser_param.cookie_instrument = True
            # Record Navigations
            browser_param.navigation_instrument = True
            # Record JS Web API calls
            browser_param.js_instrument = True
            # Record the callstack of all WebRequests made
            browser_param.callstack_instrument = True
            # Record DNS resolution
            browser_param.dns_instrument = True
            # Bot mitigation
            browser_param.bot_mitigation = True
            # allow third party cookies
            browser_param.tp_cookies = "always"
            # do not track options
            browser_param.donottrack = False
            # tracking protection
            browser_param.tracking_protection = False
            # browser profile archive
            browser_param.profile_archive_dir = Path(self.profile_subdir)
            self.audit_profile_dir = Path(self.profile_subdir)  # assign as attribute
            # path to seed profile
            if self.path_to_seed_profile:
                browser_param.seed_tar = Path(self.path_to_seed_profile)
            else:
                # creating a new one
                pass
            self.browser_params = browser_params
            # resources to save
            if self.resources_to_save:
                browser_param.save_content = self.resources_to_save

    def crawl_audit(
        self, take_screenshot: bool = False, fetch_source_code: bool = False
    ) -> None:
        """Crawl websites using an audit instance"""
        if self.websites:
            unstructed_content_provider = (
                None
                if not self.resources_to_save
                else LevelDbProvider(Path(self.content_db))
            )
            with TaskManager(
                self.manager_params,
                self.browser_params,
                structured_storage_provider=SQLiteStorageProvider(Path(self.output_db)),
                unstructured_storage_provider=unstructed_content_provider,
            ) as manager:
                # Visits the sites
                # last_site = self.websites[-1]
                for index, site in enumerate(self.websites):
                    ## call back function for the logger
                    def callback(success: bool, val: str = site) -> None:
                        print(
                            f"[+] CommandSequence for {val} ran {'successfully' if success else 'unsuccessfully'}"
                        )

                    ## check if max cookies ceiling was reached
                    # if applicable
                    if self.max_cookies:
                        # check if we reached that threshold
                        if self.count_cookies() >= self.max_cookies:
                            # yes, stop the crawl
                            print(
                                f"[!] Reached the user defined max cookies ceiling of {self.max_cookies}\n Exiting the crawl."
                            )
                            break
                    # Parallelize sites over all number of browsers set above.
                    command_sequence = CommandSequence(
                        site,
                        site_rank=index,
                        callback=callback,
                    )
                    # check if the bot should be active at this time of the day
                    hour_now = datetime.now().hour
                    if hour_now < ACTIVE_STATUS_START or hour_now > ACTIVE_STATUS_STOP:
                        print(
                            f"[!] It is {hour_now} o'clock. Will sleep until the next active start time at {ACTIVE_STATUS_START}"
                        )
                        while abs(datetime.now().hour - ACTIVE_STATUS_START) != 0:
                            time.sleep(1)
                    # command_sequence.append_command(
                    #     ScheduleManager()
                    # )
                    # visit a page and sleep for n sec
                    command_sequence.append_command(
                        GetCommand(
                            url=site,
                            sleep=random.uniform(
                                SLEEP_TIME_UNIFORM_DIST_MIN, SLEEP_TIME_UNIFORM_DIST_MAX
                            ),
                        ),
                        timeout=GET_REQUEST_TIMEOUT,
                    )
                    # browse internal links. Risky due to un-accepted cookie banners crashing the crawl
                    # command_sequence.append_command(BrowseCommand(url=site, num_links = int(random.uniform(0,5)), sleep=random.uniform(5, 20)), timeout=self.timeout)
                    # Have a look at custom_command.py to see how to implement your own command
                    # command_sequence.append_command(LinkCountingCommand()) # this is an example of a custom command
                    # Fetch and dump the page source
                    if fetch_source_code:
                        command_sequence.append_command(
                            RecursiveDumpPageSourceCommand(suffix=self.audit_name)
                        )
                    # Take a screenshot...too large, save it for paris!
                    if take_screenshot:
                        command_sequence.append_command(
                            ScreenshotFullPageCommand(suffix=self.audit_name)
                        )
                    # if site == last_site:
                    # download light beam data
                    # command_sequence.append_command(DownloadLightbeamData(output_dir=self.parent_output_dir), timeout=self.timeout)
                    # Run commands across all browsers (simple parallelization)
                    manager.execute_command_sequence(command_sequence)

    def clean_up(self) -> None:
        """
        some cleaning up:
            * tar very large files
        """
        ## compress some heavy dirs/files
        to_tar = [
            os.path.join(self.parent_output_dir, "screenshots"),
            os.path.join(self.parent_output_dir, "sources"),
            os.path.join(self.parent_output_dir, f"openwpm_{self.audit_name}.log"),
        ]
        for _ in to_tar:
            if os.path.isdir(_):
                _files = os.listdir(_)
            else:
                _files = [_]
            _tar(files=_files)
