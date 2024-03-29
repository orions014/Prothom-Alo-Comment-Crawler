# -*- coding: utf-8 -*-
"""TotalComment.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1eaKqCf6RqpaWGMONHwHCQS8OZvUO5Yw2
"""

import requests
from bs4 import BeautifulSoup
import re
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from dateutil.parser import parse
import numpy as np
import pandas as pd
import nltk
nltk.download('punkt')

article_array = ["sports","economy","bangladesh","opinion","life-style","entertainment","pachmisheli","international"]
monthDictionary = {"জানুয়ারি":1,"ফেব্রুয়ারি":2,"মার্চ":3,"এপ্রিল":4,"মে":5,"জুন":6,"জুলাই":7,"আগস্ট":8,"সেপ্টেম্বর":9,"অক্টোবর":10,"নভেম্বর":11,"ডিসেম্বর":12}
digitDictionary = {"০":0,"১":1,"২":2,"৩":3,"৪":4,"৫":5,"৬":6,"৭":7,"৮":8,"৯":9}

published_date = ""
topic_title = ""
topic_description = ""
detail_data_url = ""
list_news_title = []
list_news_published_date = []
list_news_description = []
list_news_content_url = []
list_total_comment_in_this_news = []
Total_topic_comment = 0

def start_crawling(max_pages,topic):
    global Total_topic_comment
    page = 1
    while page <= max_pages:
        Total_topic_comment = 0
        url = 'https://www.prothomalo.com/'+topic+'/article/?page=' + str(page)
        print("{} Article url\n".format(topic))
        print(url)
        source_code = requests.get(url, params=None)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, features="lxml")
        for link in soup.findAll('a', {'class': 'link_overlay'}):
            href = link.get('href')
            if topic not in href:
                continue
            get_stat_of_comments(href, str(page),topic)
        page += 1
        print("Total Topic {}".format(Total_topic_comment))
#     print("length of list_comment {} , list_commenter_name {} list_comment_url {} list_commenter_device {} "
#           "list_news_title {} list_news_published_date {} list_news_description {} list_news_content_url {} list_commenter_id {} list_total_comment_in_this_news {}"
#           .format(len(list_comment), len(list_commenter_name), len(list_comment_url), len(list_commenter_device),
#                   len(list_news_title),
#                   len(list_news_published_date), len(list_news_description), len(list_news_content_url),
#                   len(list_commenter_id),len(list_total_comment_in_this_news)))

#     print("Commeter names \n", list_commenter_name)
    
    
    myDataFrame = pd.DataFrame(list_news_published_date,columns=['Date']) 
    myDataFrame ["Title"] = list_news_title
    myDataFrame ["Detail"] = list_news_description
    myDataFrame ["Content_url"] = list_news_content_url
    myDataFrame ["Total_Comment_on_this_news"] = list_total_comment_in_this_news
    
    return myDataFrame

def convertToEnglishDate(publishedDateinBangla):
  nltk_tokens = nltk.word_tokenize(publishedDateinBangla)
#   print (nltk_tokens)
  date = ""
  month = ""
  year = ""

  for i,word in enumerate(nltk_tokens[:3]):
  #   print("GE",i,word)
    if (i == 0):
      for c in word:
#         print(digitDictionary[c])
        date += str(digitDictionary[c])
      pass
    elif (i == 1):
      month = str(monthDictionary[word])
#       print(monthDictionary[word])
    else:
      for c in word:
#         print(digitDictionary[c])
        year += str(digitDictionary[c])

  return date+"-"+month+"-"+year

def get_stat_of_comments(item_url, page,topic):
    global detail_data_url
    # print("Item url\n")
    # print("https://www.prothomalo.com{}".format(item_url))
    detail_data_url = "https://www.prothomalo.com"+item_url
    found_item = re.search('/'+topic+'/article/(.+?)/', item_url)
    # print("Found item")

    if found_item:
        global published_date
        global topic_title
        global topic_description
        global list_news_title
        global list_news_published_date
        global list_news_description
        global list_news_content_url
        global Total_topic_comment
        global list_total_comment_in_this_news

        content_id = found_item.group(1)
        # print("Comment json url\n")
        # print('https://www.prothomalo.com/api/comments/get_comments_json/?content_id=' + content_id)
        response = requests.get('https://www.prothomalo.com/api/comments/get_comments_json/?content_id=' + content_id)
        commenter_json_url = 'https://www.prothomalo.com/api/comments/get_comments_json/?content_id=' + content_id
        json_data = response.json()
        # print("Json type \n",type(json_data))
#         print("{} People commented \n".format(len(json_data)))
        Total_topic_comment += 1
        if len(json_data) >= 1:

            try:
                source_code = requests.get(detail_data_url, params=None)
                plain_text = source_code.text
                soup = BeautifulSoup(plain_text, features="lxml")
                topic_title = soup.title.get_text()
                topic_description = soup.find(itemprop="articleBody").get_text()

                published_date = soup.find(itemprop="datePublished").get_text()
               

            except:
                print("Exception in souping")


        list_news_title.append(topic_title)
        list_news_published_date.append(convertToEnglishDate(published_date))
        list_news_description.append(topic_description)
        list_news_content_url.append(detail_data_url)
        list_total_comment_in_this_news.append(str(len(json_data)))

# [0 "sports",1 "economy",2 "bangladesh", 3 "opinion", 4 "life-style", 5 "entertainment", 6 "pachmisheli",7 "international"]
choose_topic = article_array[0]

print("The topic you chose {}".format(choose_topic))

myDataFrame = start_crawling(3,choose_topic)

from google.colab import files
myDataFrame.to_csv(choose_topic+"_stat.csv", encoding='utf-8', index=False)

files.download(choose_topic+"_stat.csv")

