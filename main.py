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

log = {}

def convert_ini(dom, url):
    """
    Scrapes EU initiatives for the theme 'A Europe Fit For the Digital Age'
    """
    eu_title = dom.find("div", class_="d-flex flex-column mb-2").find("h2", class_="erpl_title-h2 mb-1 mb-md-0 mr-md-2 d-md-flex align-items-center").string

    eu_details = dom.find(id="legislativeTxt").find("div", class_="details")
    eu_details = ' '.join(i.text for i in eu_details)
    # print(type(eu_details))
    # for i in eu_details:
    #     print(i.text)

    for section in dom.find_all("ul", class_="mb-3 p-0"):
        for element in section.find_all("li", class_="d-flex"):
            el = element.find("p", class_="col-6 font-weight-bold text-nowrap mr-lg-1 mb-0 px-0")
            if el != None:
                if el.string == "Type:":
                    eu_type = el.find_next("p").string
                    if eu_type in helpers.en_to_nl_type:
                        eu_type = helpers.en_to_nl_type[eu_type]
                if el.string == "Status:":
                    eu_status = el.find_next("span").string
                    if eu_status in helpers.en_to_nl_status:
                        eu_status = helpers.en_to_nl_status[eu_status]
        
    return {
        "Naam": eu_title,
        "Type": eu_type,
        "Status": eu_status,
        "Details": eu_details,
        "URL": url
    }

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the text content, otherwise return None
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
    Returns a list with dictionaries containing the title, the type and the URL of the initiatives.
    """
    data = []

    for url in urls:        
        dom = parse_url(url)
        content = convert_ini(dom, url)
        data.append(content)
    
    return data

def get_urls(dom):
    """
    Returns a list with the urls of all the initiatives.
    """    
    urls = []
    for page in dom.find_all("div", class_="carriage-name-container"):
        url = "https://www.europarl.europa.eu" + page.a["href"]
        urls.append(url)

    return urls

def filter_urls(urls, df_old):
    """
    Returns lists with the urls on the website and urls in the existing Excel (which could be empty)    
    """
    old_urls = df_old['URL'].to_list()

    new_urls = [] 
    for url in urls:
        if url not in old_urls:
            new_urls.append(url)
    return old_urls, new_urls

def find_updates(old_urls, df_old):
    """
    Checks if any of the information from the website is updated and returns the updated DataFrame
    """
    set_inis = set()
    updated_cols = []
    df_old = df_old.drop(columns=["Toelichting", "Impact IenW"])

    for url in old_urls:
        # Find the row in the old df that matches the new url
        old_content = df_old.loc[df_old['URL'] == url].to_dict('records')[0]
        dom = parse_url(url)
        new_content = convert_ini(dom, url)

        # Compare content of the dicts
        for key in old_content:
            if old_content[key] != new_content[key]:
                print(f"There's an update in column {key} of {old_content['Naam']}")
                updated_cols.append(
                    f"{old_content["Naam"]} - {key}")
                set_inis.add(old_content["Naam"])

                # Overwrite the old_content
                old_content[key] = new_content[key]
        for key, value in old_content.items():
            df_old.loc[df_old['URL'] == url, key] = value
    
    log["# Updated initiatives"] = len(set_inis)
    log["Updated initiatives"] = ', '.join(set_inis) if set_inis else None

    log["# Updated columns"] = len(updated_cols)
    log["Updated columns"] = ', '.join(updated_cols) if updated_cols else None

    return df_old

def main():
    print(f"Start: {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}")
    log["Start"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

    # Begin page
    EU_URL = "https://www.europarl.europa.eu/legislative-train/theme-a-europe-fit-for-the-digital-age/"
    print(f"Loading the url: {EU_URL}")

    dom = parse_url(EU_URL)

    urls = get_urls(dom)

    #urls = urls[:5] ## TESTING SAMPLE

    df_ini, df_log = helpers.load()
    print(f"Loaded the existing {len(df_ini)} initiatives")
 
    old_urls, new_urls = filter_urls(urls, df_ini)
    print(f"Found {len(new_urls)} new initiative(s)")
    log["# New initiatives"] = len(new_urls)
    
    new_data = get_content(new_urls)
    df_new = pd.DataFrame(new_data)

    # Temporarily store the manual columns and Naam to later reconnect to dataframe
    manual_cols = df_ini[["Toelichting", "Impact IenW", "URL"]]

    print(f"Checking for updates in the {len(old_urls)} existing initiatives")
    df_old = find_updates(old_urls, df_ini)

    df_final = pd.concat([df_old, df_new])

    print(f"Inserted the {len(new_urls)} new initiatives following the current order on the website")

    # Convert the 'URL' column to a categorical type with the custom order
    df_final['URL_sort'] = df_final['URL'].apply(lambda x: urls.index(x) if x in urls else len(urls))
    df_final = df_final.sort_values(by='URL_sort')
    df_final = df_final.drop(columns=['URL_sort'])

    df_final_manual = pd.merge(df_final, manual_cols, left_on="URL", right_on="URL", how="left")

    # Reorder columns    
    df_final = df_final_manual[['Naam', 'Toelichting', 'Type', 'Impact IenW', 'Status', "Details", 'URL']]

    print(f'Finished at {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')
    # runtime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S") - log["Start"]
    # print(runtime)

    # Assuming log["Start"] is a string representing the start time
    log_start_time = datetime.strptime(log["Start"], "%m/%d/%Y, %H:%M:%S")

    # Get the current time
    current_time = datetime.now()

    # Calculate the runtime as a timedelta object
    runtime = current_time - log_start_time

    # Convert the runtime to minutes and seconds
    minutes, seconds = divmod(runtime.total_seconds(), 60)

    # Print the runtime in minutes and seconds
    print(f"Runtime: {int(minutes)} minutes and {int(seconds)} seconds")
    log["Runtime"] = f"{int(minutes)} minutes:{int(seconds)} seconds"

    df_log = df_log._append(log, ignore_index=True)

    print(df_log)

    helpers.write(df_final, df_log)
    print(f"Wrote out the {len(df_final_manual)} initiatives to Excel")

if __name__ == '__main__':
    main()