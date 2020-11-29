import requests
from bs4 import BeautifulSoup
import re
import json

bs4_obj = BeautifulSoup()


def a_to_text(tag):
	for a in tag.select('a'):
		href = a.get('href')
		a_text = a.text
		a_to_b = bs4_obj.new_tag("b")
		a_to_b.string = "< " + a_text + " [href=" + href + "]>"
		a.replace_with(a_to_b)
	return tag.text


def ul_to_list(ul):
	nested = []
	children = ul.find_all("li", recursive=False)
	for y in children:
		if y.find('ul') == None:
			nested.append(a_to_text(y))
			y.decompose()
		else:
			lis = {}
			content = []
			for ul in y.select('ul'):
				content += ul_to_list(ul)
				ul.decompose()
			name = a_to_text(y)
			lis[name] = content
			nested.append(lis)
			y.decompose()
	return nested


def ol_to_list(ol):
	nested = []
	children = ol.find_all("li", recursive=False)
	for y in children:
			if y.find('ol') == None:
				nested.append(a_to_text(y))
				y.decompose()
			else:
				lis = {}
				embedded_ol = y.select('ol')
				content = ol_to_list(embedded_ol[0])
				k = y
				k.select('ol')[0].clear()
				name = a_to_text(k)
				lis[name] = content
				nested.append(lis)
	return nested


def disease_search(d_link):
	section_content = {}
	try:
		disease = requests.get(d_link)
	except:
		return {'error': "link not valid"}
	# print(disease)
	sections = BeautifulSoup(disease.text, 'lxml')

	for section in sections.select(".block_content > .block_section"):
		try:
			change = False
			content = []
			sub_section = {}
			if section.select(".block_content > .block_section > .block_body")[0].text == "[Pending]":
				return "Pending"
			title = section.select(".topicheading_title")[0].text

			# convert all ol to ul
			for all_ol in section.find_all('ol'):
				all_ol.name = "ul"

			# for sections where only ul tag
			if len(section.select(".block_body > ul")) != 0:
				uls = section.select('.block_body > ul')
				for ul in uls:
					try:
						ul_b = ul.previous_sibling.previous_sibling
						heading = ul_b.text
						ul_b.decompose()
					except AttributeError:
						heading = ''
					try:
						sub_section[heading] = sub_section[heading] + ul_to_list(ul)
					except KeyError:
						sub_section[heading] = ul_to_list(ul)
				change = True

			# for section with images
			if len(section.select(".block_body div > a > img")) != 0:
				images_div = section.select(".block_body > div > div")
				if len(images_div) == 0:
					images_div = section.select(".block_body > div")
				for image in images_div:
					image_links = []
					try:
						image_text = image.select('p')[0].text
					except IndexError:
						image_text = ''
					for a in image.select("a"):
						image_links.append(a.get('href'))
					try:
						sub_section[image_text] = image_links + sub_section[image_text]
					except KeyError:
						sub_section[image_text] = image_links
				for image in images_div:
					image.decompose()
				change = True

			# for ol sections
			if len(section.select(".block_body > ol")) != 0:
				ols = section.select('.block_body > ol')
				for ol in ols:
					try:
						heading = ol.previous_sibling.previous_sibling.text
					except AttributeError:
						heading = ''
					try:
						sub_section[heading] = sub_section[heading] + ol_to_list(ol)
					except KeyError:
						sub_section[heading] = ol_to_list(ol)
				for ol in ols:
					ol.decompose()
				change = True

			# for any other element
			if change == False:
				sub_section = a_to_text(section.select(".block_body")[0])

			# for meta text
			if change == True and re.search('[a-zA-Z]', section.select(".block_body")[0].text):
				try:
					sub_section['meta'] = sub_section['meta'] + a_to_text(section.select(".block_body")[0])
				except KeyError:
					sub_section['meta'] = a_to_text(section.select(".block_body")[0])	

			section_content[title] = sub_section
		except:
			errors.append({"section err": d_link})
			continue
	return section_content
	# print(section_content)


def category_search(c_link):
	try:
		chapter = requests.get(c_link)
	except:
		return {'error': "link not valid"}
	soup = BeautifulSoup(chapter.text, 'html.parser')
	toc = {}
	categories = soup.select(".page_content > .toc_section")
	if len(categories) == 0:
		categories = soup.select(".page_content > .toc_links")
	for category in categories:
		diseases = {}
		try:
			try:
				cat_name = category.select(".toc_section_name")[0].text
			except:
				cat_name = category.select(".f12b")[0].text
		except:
			cat_name = "<no name>"

		if "Superpages" in cat_name:
			continue
		toc[cat_name] = {}
		print("\033[1m\u001b[31m--- " + cat_name + "\033[0m")
		for disease in category.select("a"):
			disease_name = disease.text
			if disease_name.strip().lower() == "books":
				try:
					book_list = []
					books = soup.select("#books .chapter_book")
					for book in books:
						link = book.find('a').get('href')
						name = book.find('p').text
						book_list.append({name: link})
					diseases[disease_name] = book_list
					print("\033[96m------>" + disease_name + "\033[0m")
					continue
				except:
					continue
			print("\033[96m------>" + disease_name + "\033[0m")
			link = disease.get('href')
			try:
				diseases[disease.text] = disease_search(link)
			except:
				error_in = cat_name+"->+"+disease.text
				errors.append({"category error(dropped)": error_in})
				continue
		toc[cat_name] = diseases
	return toc


home = requests.get('https://www.pathologyoutlines.com/')
chapters = {}
homepage = BeautifulSoup(home.text, 'html.parser')
ignore = ["Chemistry, toxicology & urinalysis", "Coagulation", "Companion diagnostic testing", "Ear", "Eye", "Informatics, digital & computational", "Muscle & nerve nontumor", "Transfusion medicine"]
errors = []

for chapter in homepage.select(".home_content .float_left li a"):
	if chapter.text in ignore:
		continue
	print("\u001b[33m" + chapter.text + "\033[0m")
	chapters[chapter.text] = category_search(chapter.get('href'))


# errors_json = json.dumps(errors, indent=1)
# with open("errors.json", "w") as errorsJSON:
# 	errorsJSON.write(errors_json)

pasred_json = json.dumps(chapters, indent=1)
with open("pathology.json", "w") as jsonFile: 
	jsonFile.write(pasred_json)
print("DONE!!!")
