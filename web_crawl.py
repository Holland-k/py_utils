import requests
import time
import os 
from bs4 import BeautifulSoup

num_visited = 0
max_visit = 50000
visit_depth = 10000
time_to_sleep = 500

def intersperse(i, j):
	print("entering intersperse", len(j))
	new_list = []
	for item in j:
		new_list.append(item)
		new_list.append(i)
	return new_list

def save_data(name, ftext):
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
		f.write(nftext)
		f.close()

def remove_common(new, old):
	return list(
		filter(lambda y: y[0:4] == "http",  # filter out relative links
			filter(lambda x: x != None, 	# filter out "None"s, not sure 
											# what this represents, but 
											# they cause crashes
				list(set(new).difference(old)) 	# removing sites already 
			)									# visited
		)
	)    
													
def get_page (addr_list, visited):
	global num_visited
	if(len(addr_list) > 0):
		print("addresses to visit ", len(addr_list))
		#print(addr_list)
		cur = addr_list[0]
		print("visiting page ", cur)
		if(cur[0:4] == "http"):
			visited.append(cur)
			try:
				page_data = requests.get(cur)
			except KeyboardInterrupt:
				return 0
			except:
				print("bad page ", cur)
			else:
				if(page_data.status_code == 200):
					#print(page_data)
					num_visited += 1
					soup = BeautifulSoup(page_data.text, 'html.parser')

					save_data(cur, soup.get_text())
					
					new_links = []
					for link in soup.find_all('a'):
						new_links.append(link.get('href'))

					if(len(addr_list) < visit_depth):
						addr_list = addr_list + remove_common(new_links, 
							visited)

		if(num_visited < max_visit):
			time.sleep(time_to_sleep)
			get_page(addr_list[1:], visited)
		else:
			print("already visited enough sites")
	return 0

def setup(max_v = 15, depth = 100, tts = 1):
	global num_visited, max_visit, visit_depth, time_to_sleep
	num_visited = 0
	max_visit = max_v
	visit_depth = depth
	time_to_sleep = tts

def main():
	get_page(["https://en.wikipedia.org/wiki/Hurricane_Dorian"],[])
