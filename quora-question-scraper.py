from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
import datetime
import time
import csv

# start time
start_time = datetime.datetime.now()

# read topics form a file
file_question_topics = open("topic_list.txt", mode='r', encoding='utf-8')
topics = file_question_topics.readlines()

for topic in topics:

	print('starting new topic: ' + str(topic))
	# instantiate a chrome options object so you can set the size and headless preference
	chrome_options = Options()
	chrome_options.add_argument("--headless")
	chrome_options.add_argument(" --window-size=1920x1080")

	# download the chrome driver from https://sites.google.com/a/chromium.org/chromedriver/downloads
	# and put it in the current directory
	chrome_driver = os.getcwd() +"/chromedriver"

	# Set the browser settings to web driver
	driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
	# driver = webdriver.Chrome(executable_path=chrome_driver)

	# give the url to scrape
	url = "https://www.quora.com/topic/" + topic + "/all_questions"
	driver.get(url)
	# driver.get("https://www.quora.com/topic/Indian-School-of-Business/all_questions")
	# driver.get("https://www.quora.com/topic/Royal-Enfield-Thunderbird/all_questions")

	# define pause time for browser
	SCROLL_PAUSE_TIME = 3

	# get browser source
	html_source = driver.page_source
	question_count_soup = BeautifulSoup(html_source, 'html.parser')

	#  get total number of questions
	question_count_str = question_count_soup.find('a', attrs={'class': 'TopicQuestionsStatsRow'})
	print(question_count_str)
	question_count = question_count_str.contents[0].contents[0]
	if 'k' in question_count:
		question_count = question_count[:-1]
		question_count = int(float(question_count)*1000)
		print(type(question_count))
	print(question_count)

	# Get scroll height
	last_height = driver.execute_script("return document.body.scrollHeight")
	question_set = set()

	# infinite while loop, break it when you reach the end of the page or not able to scroll further.
	while True:
		html_source = " "
		i = 0

		# try to scroll 20 times in case of slow connection
		while i < 20:

			# Scroll down to one page length
			driver.execute_script("window.scrollBy(0, 1080);")

			# Wait to load page
			time.sleep(SCROLL_PAUSE_TIME)

			# get page height in pixels
			new_height = driver.execute_script("return document.body.scrollHeight")

			# break this loop when you are able to scroll futher
			if new_height != last_height:
				break
			i += 1
			print(new_height)
			print(i)

		# get html page source
		html_source = driver.page_source
		soup = BeautifulSoup(html_source, 'html.parser')

		# question_link is the class for questions
		question_link = soup.find_all('a', attrs={'class': 'question_link'}, href=True)

		# add questions to a set for uniqueness
		for ques in question_link:
			question_set.add(ques)

		# not able to scroll further, break the infinite loop
		new_height = driver.execute_script("return document.body.scrollHeight")
		if new_height == last_height:
			break
		last_height = new_height

		print(len(question_set))

	# write content of set to a file called question_urls.txt
	questions_directory = 'questions'
	os.makedirs('questions', exist_ok=True)
	file_name = questions_directory + '/' + topic + '_question_urls.txt'
	file_question_urls = open(file_name, mode='w', encoding='utf-8')
	writer = csv.writer(file_question_urls)
	for ques in question_set:
		link_url = "http://www.quora.com" + ques.attrs['href']
		print(link_url)
		writer.writerows([[link_url]])

	print('quitting chrome')
	driver.quit()

# finish time
end_time = datetime.datetime.now()
print(end_time-start_time)
