# Functions to adapt scraper specifically EU initiatives for the theme 'A Europe Fit For the Digital Age'
import helpers

def convert_ini(dom, url):
    eu_title = dom.find("div", class_="d-flex flex-column mb-2").find("h2", class_="erpl_title-h2 mb-1 mb-md-0 mr-md-2 d-md-flex align-items-center").string

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
        "URL": url
    }

