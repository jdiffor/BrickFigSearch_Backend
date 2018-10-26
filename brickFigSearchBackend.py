from flask import Flask, request, jsonify
import urllib
import urllib.request as ur
from bs4 import BeautifulSoup as BS
import os
#import config

brickset_base_url = 'http://brickset.com/api/v2.asmx/getSets?apiKey=TOAZ-NCTf-LK5p&userHash=&theme=&subtheme=&setNumber=&year=&owned=&wanted=&orderBy=&pageSize=&pageNumber=&userName=&query='
bricklink_base_url = 'https://www.bricklink.com/catalogItemInv.asp?S='
bricklink_extension_url = '-1&viewItemType=M'
bricklink_image_base_url = 'https://www.bricklink.com/ML/'
bricklink_price_url = 'https://www.bricklink.com/catalogPG.asp?M='
jpg = '.jpg'

hdr = {'User-Agent': 'Chrome/23.0.1271.65 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

app = Flask(__name__)

def search_for_set(query):
	search_url = brickset_base_url + query
	req = ur.Request(search_url, headers=hdr)
	res = ur.urlopen(req)
	html = res.read()
	res.close()
	soup = BS(html, "xml")
	sets = soup.find_all('sets')
	results = []
	for this_set in sets:
		res_set = {}
		res_set['number'] = this_set.find('number').text
		res_set['name'] = this_set.find('name').text
		results.append(res_set)
	return jsonify({'sets': results})

def get_minifigs(number):
	url = bricklink_base_url + number + bricklink_extension_url
	req = ur.Request(url, headers=hdr)
	res = ur.urlopen(req)
	html = res.read()
	res.close()
	soup = BS(html, "html.parser")
	table_container = soup.find('table', class_='ta')
	minifigs = []
	lego_set = {'minifigs': minifigs}
	i = 0
	total_price = 0
	for tr in table_container:
		if i > 3:
			lis = tr.text.split()
			if lis[0] == '*':
				minifig_code = lis[2]
				quantity = lis[1]
				fig = {'minifig_code': minifig_code}
				fig['quantity'] = quantity
				fig['price'] = get_fig_price(minifig_code)
				total_price += (float(fig['price'][1:]) * int(quantity))
				fig['image'] = '<img src=' + bricklink_image_base_url + minifig_code + jpg + '>'
				minifigs.append(fig)
		i += 1
	lego_set['price'] = total_price
	return jsonify({'set': lego_set})

def get_fig_price(fig_code):
	fig_url = bricklink_price_url + fig_code
	req = ur.Request(fig_url, headers=hdr)
	res = ur.urlopen(req)
	html = res.read()
	res.close()
	soup = BS(html, "html.parser")
	table_container = soup.find('table', class_='fv')
	i = 0
	for tr in table_container:
		if i == 2:
			j = 0
			for t in tr:
				if j == 0:
					a = (str(t).split())
					return (a[23].split('</b>')[0])
				j += 1
		i += 1
	return "$0.00"

# root
@app.route("/")
def index():
	"""
	this is a root dir of my server
	:return: str
	"""
	return "Welcome to the backend of BrickFigSearch"

# GET
@app.route('/sets/<number>')
def get_set_data_endpoint(number):
	"""
	output minifig codes for a set identified by number
	:param number:
	:return: str
	"""
	return get_minifigs(number)

# GET
@app.route('/search/<query>')
def get_search_results_endpoint(query):
	"""
	output results for a given search query
	:param number:
	:return: str
	"""
	return search_for_set(query)

# running web app in local machine
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
