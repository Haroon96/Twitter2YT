from selenium.webdriver import Chrome
from argparse import ArgumentParser
import pandas as pd

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('actor_file', help="Input file containing list of actors")
    parser.add_argument('output_file', help="Output file to write results to")
    return parser.parse_args()

def twitter2yt(driver, handle):
    
    # load twitter profile
    driver.get('https://twitter.com/' + handle)
 
    # get name from twitter xpath
    name = driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div[1]/div/span[1]/span').text
    
    # search channels by this name on youtube
    search_url = f'https://www.youtube.com/results?search_query={"+".join(name.split())}&sp=EgIQAg%253D%253D'
    driver.get(search_url)
    
    # extract top result
    elem = driver.find_element_by_id('main-link')
    
    # get channel URL
    href = elem.get_attribute('href')
    
    # parse text from result
    name, meta = elem.text.split('\n')[:2]
    
    # return findings
    return href, name, meta
  
def get_subs_from_meta(x):
    if '•' in x:
        t = x.split('•')
    else:
        t = x.split()
    vids = None
    subs = None
    for i in t:
        if 'subscriber' in i:
            return i.split()[0]
    return None

def get_vids_from_meta(x):
    if '•' in x:
        t = x.split('•')
    else:
        t = [x]
    vids = None
    subs = None
    for i in t:
        if 'video' in i:
            return i.split()[0]
    return None
    
def main():
    # parse arguments
    args = parse_args()
    actor_file = args.actor_file
    output_file = args.output_file
    
    # init chromedriver
    driver = Chrome()
    driver.implicitly_wait(30)
    driver.set_page_load_timeout(120)
    
    # load twitter handles from input_file
    with open(actor_file) as f:
        actors = f.read().strip().split('\n')
        
    results = []
        
    # find yt channels for each actor
    for actor in actors:
        try:
            channel_url, channel_name, channel_meta = twitter2yt(driver, actor)
            videos = get_vids_from_meta(channel_meta)
            subscribers = get_subs_from_meta(channel_meta)
            results.append({
                'channel_url': channel_url,
                'channel_name': channel_name,
                'channel_meta': channel_meta,
                'videos': videos,
                'subscribers': subscribers
            })
        except Exception as e:
            print("Error parsing actor", actor, e)
        
    # write results to csv
    pd.DataFrame(results).to_csv(output_file, index=False)

    

    
if __name__ == '__main__':
    main()
    