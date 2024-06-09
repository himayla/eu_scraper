from bs4 import BeautifulSoup
from contextlib import closing
import pandas as pd
from requests import get
from requests.exceptions import RequestException
import digital_init
import helpers
from datetime import datetime

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
    Returns DOM from HTML url
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
        content = digital_init.convert_ini(dom, url)
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
    old_urls = df_old['URL'].to_list()
    new_urls = [] 
    for url in urls:
        if url not in old_urls:
            new_urls.append(url)
    return old_urls, new_urls

def find_updates(old_urls, df_old):
    for url in old_urls:
        # Find the row in the old df that matches the new url
        # print(url)
        old_content = df_old.loc[df_old['URL'] == url].to_dict('records')[0]
        # print(old_content)
        dom = parse_url(url)
        new_content = digital_init.convert_ini(dom, url)

        # Compare content of the dicts
        for key in old_content:
            if old_content[key] != new_content[key]:
                print(f"There's an update in column {key} of {old_content['Naam']}")
                # Overwrite the old_content
                old_content[key] = new_content[key]
            # else:
            #     updated[key] = old_content[key]
        for key, value in old_content.items():
            df_old.loc[df_old['URL'] == url, key] = value
    return df_old


def main():
    print(f"Start: {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}")
    
    EU_URL = "https://www.europarl.europa.eu/legislative-train/theme-a-europe-fit-for-the-digital-age/"

    dom = parse_url(EU_URL)

    urls = get_urls(dom)
    urls = urls[:20] # [:20] for testing
    
    df_old = helpers.read_ini(helpers.output_file)
    print(f'Loaded the existing {len(df_old)} initiatives')

    old_urls, new_urls = filter_urls(urls, df_old)
    print(f'Found {len(new_urls)} new initiative(s)')

    new_data = get_content(new_urls)
    df_new = pd.DataFrame(new_data, index=None)

    print(f'Succesfully downloaded {len(df_new)} new initiatives')

    print(f'Loaded {len(old_urls)} original initiatives')

    df_old = find_updates(old_urls, df_old)
    
    df_final = pd.concat([df_old, df_new]).reset_index(drop=True)
    print(df_final)

    helpers.write_ini(df_final, helpers.output_file)

    print(f'Finished at {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')

if __name__ == '__main__':
    main()