import datetime
from selenium.webdriver.chrome.options import Options
import os
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import csv

# start time
start_time = datetime.datetime.now()

# read topics form a file
file_question_topics = open("topic_list.txt", mode='r', encoding='utf-8')
topics = file_question_topics.readlines()

for topic in topics:
	# read questions form files under questions directory
	questions_file = topic + '_question_urls.txt'
	questions = open('questions/'+ questions_file, mode='r', encoding='utf-8')

	for question in questions:
		print('Question: ' + question)
		# instantiate a chrome options object so you can set the size and headless preference
		chrome_options = Options()
		chrome_options.add_argument("--headless")
		chrome_options.add_argument(" --window-size=1920x1080")

		# download the chrome driver from https://sites.google.com/a/chromium.org/chromedriver/downloads
		# and put it in the current directory
		chrome_driver = os.getcwd() + "/chromedriver"

		# Set the browser settings to web driver
		driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
		# driver = webdriver.Chrome(executable_path=chrome_driver)

		# give the url to scrap
		driver.get(question)

		# define pause time for browser
		SCROLL_PAUSE_TIME = 3

		# get browser source
		html_source = driver.page_source
		question_count_soup = BeautifulSoup(html_source, 'html.parser')

		# Get scroll height
		last_height = driver.execute_script("return document.body.scrollHeight")
		answer_set = set()

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

			# get html page source
			html_source = driver.page_source
			soup = BeautifulSoup(html_source, 'html.parser')

			# question_link is the class for questions
			answer_texts = soup.find_all('div', attrs={'class': 'ui_qtext_expanded'})

			# add questions to a set for uniqueness
			for answer in answer_texts:
				# <div class=""ui_qtext_expanded""><span class=""ui_qtext_rendered_qtext"">
				answer = str(answer).lstrip("<div class=\"ui_qtext_expanded\"><span class=\"ui_qtext_rendered_qtext\">").rstrip("</span></div>")
				answer_set.add(answer)

			# not able to scroll further, break the infinite loop
			new_height = driver.execute_script("return document.body.scrollHeight")
			if new_height == last_height:
				break
			last_height = new_height

			print('Total Answers: ' + str(len(answer_set)))

		#write contents of set to a file called answers.txt
		answers_directory = 'answers'
		os.makedirs('answers', exist_ok=True)
		file_name = answers_directory + '/' + topic + '_answers.txt'
		file_answers = open(file_name, mode='a', encoding='utf-8')
		writer = csv.writer(file_answers)
		for answer in answer_set:
			# link_url = "http://www.quora.com" + ques.attrs['href']
			print(answer)
			writer.writerows([[answer]])

		print('quitting chrome')
		driver.quit()

# finish time
end_time = datetime.datetime.now()
print(end_time-start_time)