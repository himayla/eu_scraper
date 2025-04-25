# main.py
#
# Mayla Kersten
#
# Program loads and updates European digital initiatives to an Excel file.
#

from bs4 import BeautifulSoup
from contextlib import closing
from datetime import datetime
import helpers
import pandas as pd
from requests import get
from requests.exceptions import RequestException

# URL for European Digital Initiatives
BASE_URL = "https://www.europarl.europa.eu/legislative-train/"

THEME = "theme-a-new-plan-for-europe-s-sustainable-prosperity-and-competitiveness"

EU_URL = f"{BASE_URL}{THEME}"

log = {}

def convert_ini(dom, url):
    """
    Scrapes the EU initiatives' information and returns a dictionary with relevant details.
    
    Args:
        dom (BeautifulSoup): Parsed DOM from the page.
        url (str): URL of the specific initiative.

    Returns:
        dict: A dictionary containing the initiative's details like name, type, status, and URL.
    """
    # Extract the title of the initiative
    eu_title = dom.find("div", class_="d-flex flex-column mb-2").find("h2", class_="erpl_title-h2 mb-1 mb-md-0 mr-md-2 d-md-flex align-items-center").string

    # Extract the initiative details
    eu_details = dom.find(id="legislativeTxt").find("div", class_="details")
    eu_details = ' '.join(i.text for i in eu_details)

    # Iterate through sidebar to find type and status
    for section in dom.find_all("ul", class_="mb-3 p-0"):
        for element in section.find_all("li", class_="d-flex"):
            el = element.find("p", class_="col-6 font-weight-bold text-nowrap mr-lg-1 mb-0 px-0")

            if el != None:
                if el.string == "Type:":
                    eu_type = el.find_next("p").string
                    if helpers.TRANSLATIONS["Type"].get(eu_type) != None :
                        eu_type = helpers.TRANSLATIONS["Type"].get(eu_type)["Nederlands"]
                
                if el.string == "Status:":
                    eu_status_en = el.find_next("span").string
    
    return {
        "Naam": eu_title,
        "Type": eu_type,
        "Status": eu_status_en,
        "Details": eu_details,
        "URL": url
    }

def simple_get(url):
    """
    Makes an HTTP GET request to the specified URL and returns the response content if it is valid HTML.
    
    Args:
        url (str): URL to fetch.

    Returns:
        str: The HTML content of the page, or None if there is an issue.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        print('The following error occurred during HTTP GET request to {0} : {1}'.format(url, str(e)))
        return None

def is_good_response(resp):
    """
    Returns true if the response seems to be HTML, false otherwise
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

def parse_url(url):
    """
    Returns Document Object Model (DOM) from HTML url
    """
    # Get raw HTML content
    html = simple_get(url)

    # Convert to readable DOM
    dom = BeautifulSoup(html, 'html.parser')

    return dom

def get_content(urls):
    """
    Fetches and parses content for a list of URLs, converting each to a dictionary of initiative details.
    
    Args:
        urls (list): List of initiative URLs.

    Returns:
        list: List of dictionaries containing initiative details.
    """
    data = []

    for url in urls:        
        dom = parse_url(url)
        content = convert_ini(dom, url)
        data.append(content)
    
    return data

def get_urls(dom):
    """
    Extracts initiative URLs from the parsed DOM of the main page.
    
    Args:
        dom (BeautifulSoup): Parsed DOM of the main page.

    Returns:
        list: List of initiative URLs.
    """
    urls = ["https://www.europarl.europa.eu" + page.a["href"] for page in dom.find_all("div", class_="carriage-name-container")]
    return urls

def filter_urls(urls, df_old):
    """
    Filters new URLs from the existing data and returns old and new initiative URLs.
    
    Args:
        urls (list): List of URLs scraped from the website.
        df_old (DataFrame): DataFrame of previously stored initiatives.

    Returns:
        tuple: (old_urls, new_urls) where each is a list of URLs.
    """
    old_urls = df_old['URL'].to_list()
    new_urls = [url for url in urls if url not in old_urls]

    log["# New initiatives"] = len(new_urls)
    
    return old_urls, new_urls

def find_updates(old_urls, df_old):
    """
    Compares old initiative data with the current data on the website, identifies updates, and returns an updated DataFrame.
    
    Args:
        old_urls (list): List of URLs for existing initiatives.
        df_old (DataFrame): Existing DataFrame of initiatives.

    Returns:
        DataFrame: Updated DataFrame with any new or modified initiatives.
    """
    updated_inis = set()
    updated_cols = []
    df_old = df_old.drop(columns=["Toelichting", "Impact IenW"])

    for url in old_urls:
        old_content = df_old.loc[df_old['URL'] == url].to_dict('records')[0]
        dom = parse_url(url)
        new_content = convert_ini(dom, url)

        # Compare content of the dicts
        for key in old_content:
            if old_content[key] != new_content[key]:
                print(f"There's an update in column {key} of {old_content['Naam']}")
                updated_cols.append(f"{old_content['Naam']} - {key}")
                updated_inis.add(old_content["Naam"])

                # Overwrite the old_content
                old_content[key] = new_content[key]
        for key, value in old_content.items():
            df_old.loc[df_old['URL'] == url, key] = value
    
    log["# Updated initiatives"] = len(updated_inis)
    log["Updated initiatives"] = ', '.join(updated_inis) if updated_inis else None

    log["# Updated columns"] = len(updated_cols)
    log["Updated columns"] = ', '.join(updated_cols) if updated_cols else None

    return df_old

def sort_df(df, urls):
    """
    Sorts the DataFrame based on the order of URLs on the website.
    
    Args:
        df (DataFrame): DataFrame to be sorted.
        urls (list): List of URLs in the correct order.

    Returns:
        DataFrame: Sorted DataFrame.
    """
    df['URL_sort'] = df['URL'].apply(lambda x: urls.index(x) if x in urls else len(urls))
    df = df.sort_values(by='URL_sort').drop(columns=['URL_sort'])
    return df

def log_runtime():
    """
    Logs and prints the total runtime of the script.
    """
    log_start_time = datetime.strptime(log["Start"], "%m/%d/%Y, %H:%M:%S")
    current_time = datetime.now()
    runtime = current_time - log_start_time

    minutes, seconds = divmod(runtime.total_seconds(), 60)
    log["Runtime"] = f"{int(minutes)} minutes, {int(seconds)} seconds"
    print(f"Runtime: {int(minutes)} minutes and {int(seconds)} seconds")

def main():
    """
    Main function to load, update, and write European digital initiatives to an Excel file.
    """
    log["Start"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    print(f"Start: {log['Start']}")

    # Load the DOM and URLs
    print(f"Loading URL: {EU_URL}")
    dom = parse_url(EU_URL)
    urls = get_urls(dom)
    # urls = urls[:10]  # For testing, limit the sample size

    # Load existing initiatives from Excel
    df_ini, df_log = helpers.load_initiatives()
    print(f"Loaded {len(df_ini)} existing initiatives")

    # Filter URLs and find new initiatives
    old_urls, new_urls = filter_urls(urls, df_ini)
    print(f"Found {len(new_urls)} new initiative(s)")

    # Get content for new initiatives and create DataFrame
    new_data = get_content(new_urls)
    df_new = pd.DataFrame(new_data)

    # Temporarily store manual columns for re-merging later
    manual_cols = df_ini[["Toelichting", "Impact IenW", "URL"]]

    # Check for updates in existing initiatives
    print(f"Checking for updates in {len(old_urls)} existing initiatives")
    df_old = find_updates(old_urls, df_ini)

    # Concatenate old and new DataFrames
    df_final = pd.concat([df_old, df_new])
    print(f"Inserted {len(new_urls)} new initiatives")

    # Sort the DataFrame by URL order
    df_final = sort_df(df_final, urls)

    # Merge with manual columns and reorder columns
    df_final = pd.merge(df_final, manual_cols, on="URL", how="left")
    df_final = df_final[['Naam', 'Toelichting', 'Type', 'Impact IenW', 'Status', "Details", 'URL']]

    # Append new log entry
    df_log = df_log._append(log, ignore_index=True)

    # Finish up
    print(f"Finished at {datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")
    log_runtime()


    # Write out the final data
    helpers.write_to_excel(df_final, df_log)
    print(f"Wrote out {len(df_final)} initiatives to Excel")
if __name__ == '__main__':
    main()