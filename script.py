import requests
from bs4 import BeautifulSoup

# home = requests.get('https://www.pathologyoutlines.com/')

# chapters = []
# soup = BeautifulSoup(home.text, 'html.parser')
# for chapter in soup.select(".home_content .float_left li a"):
# 	chapters.append((chapter.text, chapter.get('href')))
# print(chapters)

# ------------------------------------------------------------------------

# chapter = requests.get('https://www.pathologyoutlines.com/adrenal.html')
# soup = BeautifulSoup(chapter.text, 'html.parser')
# # print(soup.prettify())
# toc = {}
# for category in soup.select(".page_content > .toc_section"):
# 	diseases = {}
# 	# ids.append(id.get('href'))
# 	# print(category)
# 	cat_name = category.select("span.toc_section_name")[0].text[:-1]
# 	if cat_name == "General" or cat_name == "Superpages":
# 		continue
# 	toc[cat_name]={}
# 	for disease in category.select("a"):
# 		link = disease.get('href')
# 		diseases[disease.text] = link
# 	toc[cat_name] = diseases
# print(toc)

# -----------------------------------------------------------------------------

section_content = {}

disease = requests.get('https://www.pathologyoutlines.com/topic/adrenalprimaryadrenalinsuff.html')
soup = BeautifulSoup(disease.text, 'lxml')

for section in soup.select(".block_content > .block_section"):
	content = []
	sub_section = {}
	title = section.select(".topicheading_title")[0].text
	sub = section.select(".block_body")[0].select("b + ul > li")
	if section.select(".block_body")[0].select("b + ul > li") != None:
		heading = section.select(".block_body > b")[0].text
		# print(heading)
		for y in sub:
			# print(y)
			if y.find('ul') == None:
				content.append(y.text)
			else:
				lis = {}
				lis[y.contents[0]] = [c.text for c in y.select('ul > li')]
				content.append(lis)
		sub_section[heading] = content
	section_content[title] = sub_section

print(section_content)
# section = soup.select(".block_content > .block_section")[0]
# # print(section.select(".block_body")[0].contents)
# for x in section.select(".block_body")[0]:
# 	if x[0].name == 'b':

# 	if x.name == 'b':
# 		sub_section[index] = {x.text}
# 	section_content[section.select(".topicheading_title")[0].text] = sub_section

# print(section.select(".block_body")[0].select(".block_body > b + ul >li")[0])
# print([x.text[:-1] for x in section.select(".block_body")[0].select(".block_body > b + ul > li")])
# content = []
# sub = [x for x in section.select(".block_body")[0].select(".block_body > b + ul > li")]
# block = section.select(".block_body")[0].select(".block_body")



# sub = section.select(".block_body")[0].select("b + ul > li")
# if section.select(".block_body")[0].select("b + ul > li") != None:
# 	heading = section.select(".block_body > b")[0].text
# 	# print(heading)
# 	for y in sub:
# 		# print(y)
# 		if y.find('ul') == None:
# 			content.append(y.text)
# 		else:
# 			lis = {}
# 			lis[y.contents[0]] = [c.text for c in y.select('ul > li')]
# 			content.append(lis)
# 			# print(y.contents[0])
# 			# print([c.text for c in y.select('ul > li')])
# 	sub_section[heading] = content
# print(sub_section)
