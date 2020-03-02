import requests
import time
import os
import sys
from bs4 import BeautifulSoup

num_visited = 0 #number of visited sites so far
max_visit = 50000 #maximum number of sites to visit
visit_depth = 10000 #how far down a path to go before stopping
time_to_sleep = 500 #how long the script should sleep between visit
max_down_size = 1024*1024*1024*1024 #maximum amount of data to download in a day

def intersperse(i, j):
    print("entering intersperse", len(j))
    new_list = []
    for item in j:
        new_list.append(item)
        new_list.append(i)
    return new_list

def save_data(name, ftext):
    global downloaded
    name = name.replace("/", "_")
    name = name.replace(".", "_")
    fn = name[8:]
    try:
        f = open("data/"+fn, "x+")
    except FileExistsError:
        print("file", fn, "already exists")
       	st = os.stat("data/"+fn)
        fage = (time.time()-st.st_mtime) 
        print(fn, "is", fage, "old")
	#add logic for age testing
        pass
    except:
        print("some error creating the file ", fn)
        pass
    else:
        nftext = "".join(ftext) # intersperse("\n",ftext))
        downloaded += sys.getsizeof(nftext)
        f.write(nftext)
        f.close()

def remove_common(new, old):
    a = list(
	filter(lambda y: y[0:4] == "http",  # filter out relative links
	    filter(lambda x: x != None,     # filter out "None"s, not sure what this represents, but 
		                            # they cause crashes
	           list(set(new).difference(old))  # removing sites already visited 
	    )								
	))
    return a

def pretty(raw_text):
    print("entering clean")
    clean_text = ""
    for i in raw_text:
        if(i.text != '\n'):
            #print(i.text)
            clean_text = clean_text + i.text
    return clean_text

def get_page (addr_list, visited):
    global num_visited
    global downloaded
    cur_page = 0
    while(len(addr_list) > cur_page and num_visited < max_visit):
        print("addresses to visit ", len(addr_list))
        #print(addr_list)
        cur = addr_list[cur_page]
        print("visiting page ", cur)
        if(cur[0:4] == "http"):
            print("if 1")
            visited.append(cur)
            try:
                page_data = requests.get(cur)
                downloaded += sys.getsizeof(page_data)
            except KeyboardInterrupt:
                return 0
            except:
                print("bad page ", cur)
                addr_list = addr_list[1:]
            else:
                print("if 2")
                if(page_data.status_code == 200):
		    #print(page_data)
                    num_visited += 1
                    soup = BeautifulSoup(page_data.text, 'html.parser')
                    save_data(cur, pretty(soup.find_all('p')))
		
                    new_links = []
                    for link in soup.find_all('a'):
                        new_links.append(link.get('href'))

                    #if(len(addr_list) < visit_depth):
                    addr_list = addr_list[1:] + remove_common(new_links, visited)
                else:
                    addr_list = addr_list[1:]
        if(downloaded > max_down_size):
            print("exceeded daily limit, sleeping")
            time.sleep(20*60*60)
            downloaded = 0
        else:
            time.sleep(time_to_sleep)
        #cur_page += 1
        
    return 0

def setup(max_v = 5000000, depth = 100, tts = 1):
    global num_visited, max_visit, visit_depth, time_to_sleep, downloaded, max_down_size
    num_visited = 0
    max_visit = max_v
    visit_depth = depth
    time_to_sleep = tts
    downloaded = 0
    max_down_size = 6442450944 # in bytes

def main(fptv):
    get_page([fptv],[])
    if(downloaded > 1000):
        dt = downloaded / 1024
        if(dt > 1000):
            if((dt / 1024) > 1000):
                hda = str(int((dt / 1024) / 1024)) + 'G'
            else:
                hda = str(int(dt / 1024)) + 'M'
        else:
            hda = str(int(downloaded / 1024)) + 'K'
    else:
        hda = str(int(downloaded)) + 'B'
    print("total amount downloaded = " + hda)

setup()
main("https://en.wikipedia.org/wiki/Yellowstone_National_Park")
