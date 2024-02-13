import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def scraper(url, resp):
    if resp.status == 200: #only scraped success page
        links = extract_next_links(url, resp)
    else:
        links = [] # return empty links for not successful visit page
    #return []
    return [link for link in links if is_valid(link)]

def get_hrefs(resp):
    #return all hyperlink found from the url
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    return [tag.get('href') for tag in soup.find_all('a')]

def extract_next_links(url, resp):
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    '''
    Expected cases & handle:
        1.absolute url: append directly to links
        2.relative url: convert to absolute and append to links
        3.fragment: ignore, don't append
        5.None: ignore, don't append
        6.Non website scheme: ignore, don't append
        7.url lacking scheme: apply scheme and append to links
    '''
    links = []
    hyperlinks = get_hrefs(resp)
    #print(hyperlinks)
    for link in hyperlinks:
        if not link:
            continue #skip None
        if link.startswith('http') or link.startswith('https'):
            links.append(link)
        if link.startswith('//'):
            #missing scheme
            links.append(f'{urlparse(url).scheme}:{link}') #Give it the same scheme as the original url
        elif link.startswith('/'):
            #is relative
            if url[-1] == '/':
                url = url[:-1] #normalize self-directing page, ie: http://www.ics.uci.edu/ -> http://www.ics.uci.edu
            absolute_url = f'{url}{link}'
            links.append(absolute_url)
        else:
            # The fragment, mailto, tel got ignored
            continue
    return links

def exceedRepeatedThreshold(url)-> True|False:
    #return true indicating if the url's path contain repeated pattern that exceed a certain threshold
    '''
    Definition of threshold
    THRESHOLD = 1 We don't allow there to be recurring path

    THRESHOLD = 2 We allowed once recurrent, but more than that smell fishy
    
    '''
    repeat_THRESHOLD = 1 #if the same token appear more than three time in the path, the url is consider a trap that has infinite pattern
    d = {}
    tokens = url.split('/')
    for x in tokens:
        if x != '':
            d[x] = d.get(x,0) + 1 #record frequency of token
    return any(value > repeat_THRESHOLD for value in d.values())

def is_valid(url):
    #return True or False that determine whether to crawl
    '''
    Expected Cases & handle:
    1. Illegal domain: if netloc not in one of the four allowed domain
    2. Repeated Pattern: fetch path and determine if there are repeated path exceeding certain threshold
    3. Document: use regular expression
    4. .php script: ignore them
    5. query: ignore them
    
    
    '''
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            #print(f'{url} will not be crawl due to <<<<<invalid scheme error>>>>>')
            return False
        elif parsed.netloc not in {"www.ics.uci.edu", "www.cs.uci.edu", "www.informatics.uci.edu", "www.stat.uci.edu"}:
            #print(f'{url} will not be crawl due to <<<<<illegal domain error>>>>>')
            return False
        elif '.php' in url:
            return False
        elif parsed.query:
            return False
        elif exceedRepeatedThreshold(url):
            #print(f'{url} will not be crawl due to <<<<<exceedRepeatedThreshold error>>>>>')
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise