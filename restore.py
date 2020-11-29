import requests
from bs4 import BeautifulSoup
import re

bs4_obj = BeautifulSoup()

def a_to_text(tag):
	for a in tag.select('a'):
		href = a.get('href')
		a_text = a.text
		a_to_b = bs4_obj.new_tag("b")
		a_to_b.string = "< " + a_text + " [href=" + href + "]>"
		a.replace_with(a_to_b)
	return tag.text

def ul_to_dict(ul):
	nested = []
	children = ul.find_all("li", recursive=False)
	for y in children:
		if y.find('ul') == None:
			nested.append(a_to_text(y))
			y.decompose()
		else:
			lis = {}
			embedded_ul = y.select('ul')
			content = ul_to_dict(embedded_ul[0])
			k = y
			k.select('ul')[0].clear()
			name = a_to_text(k)
			lis[name] = content
			nested.append(lis)
	return nested


def ol_to_dict(ul):
	nested = []
	children = ul.find_all("li", recursive=False)
	for y in children:
			if y.find('ol') == None:
				nested.append(a_to_text(y))
			else:
				lis = {}
				embedded_ol = y.select('ol')
				content = ol_to_dict(embedded_ol[0])
				k = y
				k.select('ol')[0].clear()
				# name = k.text
				name = a_to_text(k)
				lis[name] = content
				nested.append(lis)
	return nested



section_content = {}
disease = requests.get('http://www.pathologyoutlines.com/topic/breastcollageneousspherulosis.html')
print(disease)
soup = BeautifulSoup(disease.text, 'lxml')

for section in soup.select(".block_content > .block_section"):
	try:
		change = False
		content = []
		sub_section = {}
		if section.select(".block_content > .block_section > .block_body")[0].text == "[Pending]":
			continue
		title = section.select(".topicheading_title")[0].text

		# for sections where only ul tag
		if len(section.select(".block_body > ul")) != 0:
			uls = section.select('.block_body > ul')
			for ul in uls:
				try:
					heading = ul.previous_sibling.previous_sibling.text
				except AttributeError:
					heading = ''
				try:
					sub_section[heading] = sub_section[heading] + ul_to_dict(ul)
				except KeyError:
					sub_section[heading] = ul_to_dict(ul)
			# for ul in uls:
			# 	ul.decompose()
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
					heading = ul.previous_sibling.previous_sibling.text
				except AttributeError:
					heading = ''
				try:
					sub_section[heading] = sub_section[heading] + ol_to_dict(ol)
				except KeyError:
					sub_section[heading] = ol_to_dict(ol)
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
		continue

print(section_content)