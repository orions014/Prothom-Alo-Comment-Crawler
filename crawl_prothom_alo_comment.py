import requests
from bs4 import BeautifulSoup

import re

from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from googletrans import Translator
from dateutil.parser import parse
import numpy as np

article_array = ["sports","economy","bangladesh","opinion","life-style","entertainment","pachmisheli","international"]
translator = Translator()
published_date = ""
topic_title = ""
topic_description = ""
detail_data_url = ""

list_comment = ["Comment"]
list_commenter_name = ["Commenter_name"]
list_comment_url = ["Comment_json_url"]
list_commenter_device = ["Commenter_device"]
list_commenter_id = ["Commenter_id"]
list_news_title = ["News_title"]
list_news_published_date = ["News_published_date"]
list_news_description = ["News_detail"]
list_news_content_url = ["News_content_url"]
list_total_comment_in_this_news = ["Total_Comment_on_this_news"]
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
            get_single_page_comments(href, str(page),topic)
        page += 1
        print("Total Topic comment {}".format(Total_topic_comment))
    print("length of list_comment {} , list_commenter_name {} list_comment_url {} list_commenter_device {} "
          "list_news_title {} list_news_published_date {} list_news_description {} list_news_content_url {} list_commenter_id {} list_total_comment_in_this_news {}"
          .format(len(list_comment), len(list_commenter_name), len(list_comment_url), len(list_commenter_device),
                  len(list_news_title),
                  len(list_news_published_date), len(list_news_description), len(list_news_content_url),
                  len(list_commenter_id),len(list_total_comment_in_this_news)))

    print("Commeter names \n", list_commenter_name)

    # np.savetxt(topic+'.csv', [p for p in zip(list_news_published_date,list_total_comment_in_this_news,list_news_content_url,list_news_title,
    #                                          list_news_description,list_comment_url,list_commenter_id,
    #                                          list_comment,list_commenter_name,
    #                                          list_commenter_device)], delimiter=',', fmt='%s')


def get_single_page_comments(item_url, page,topic):
    global translator
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
        global list_comment
        global list_commenter_name
        global list_comment_url
        global list_commenter_device
        global list_news_title
        global list_news_published_date
        global list_news_description
        global list_news_content_url
        global list_commenter_id
        global Total_topic_comment
        global list_total_comment_in_this_news

        content_id = found_item.group(1)
        # print("Comment json url\n")
        # print('https://www.prothomalo.com/api/comments/get_comments_json/?content_id=' + content_id)
        response = requests.get('https://www.prothomalo.com/api/comments/get_comments_json/?content_id=' + content_id)
        commenter_json_url = 'https://www.prothomalo.com/api/comments/get_comments_json/?content_id=' + content_id
        json_data = response.json()
        # print("Json type \n",type(json_data))
        # print("{} People commented \n".format(len(json_data)))
        Total_topic_comment += 1
        if len(json_data) >= 1:

            try:
                source_code = requests.get(detail_data_url, params=None)
                plain_text = source_code.text
                soup = BeautifulSoup(plain_text, features="lxml")
                topic_title = soup.title.get_text()
                # print("Topic title \n",topic_title)
                topic_description = soup.find(itemprop="articleBody").get_text()

                # print("description \n", topic_description)
                published_date = soup.find(itemprop="datePublished").get_text()
                # print("Date \n",published_date )
                # published_date = published_date.date()
                # print(published_date)

            except:
                print("Exception in souping")


        nonword_pattern = re.compile('[.@_!#$%^&*()<>?/|}{~:DpP0123456789 ১২৩৪৫৬৭৮৯০]*$')

        for comment_id in json_data:
            comment_object = json_data[comment_id]
            comment = comment_object['comment']
            commenter_name = comment_object['commenter_name']
            device = comment_object['device']

            if not nonword_pattern.fullmatch(comment):

                if ' ' not in comment:
                    continue

                try:
                    lang = detect(comment)

                    if lang == "bn" or lang == "en":
                        formatted_comment = '---------------------------------' \
                                            + '\nComment ID: ' + comment_id \
                                            + '\nContent ID: ' + content_id \
                                            + '\nPage no: ' + page + '\n' + commenter_name + '\n'+ device \
                                            + '\n' + comment + '\n\n' + str(published_date)

                        # print(formatted_comment)
                        if commenter_name == "hidden":
                            commenter_name = "নাম প্রকাশে অনিচ্ছুক"

                        list_comment.append(comment)
                        list_commenter_name.append(commenter_name)
                        list_comment_url.append(commenter_json_url)
                        list_commenter_device.append(device)
                        list_news_title.append(topic_title)
                        list_news_published_date.append(str(published_date))
                        list_news_description.append(topic_description)
                        list_news_content_url.append(detail_data_url)
                        list_commenter_id.append(comment_id)
                        list_total_comment_in_this_news.append(str(len(json_data)))
                        # print("Total commec {}".format(len(json_data)))
                        # insert_data_to_file(project_name, formatted_comment)
                except LangDetectException:
                    pass




project_name = "prothomalocrwaler"
# [0 "sports",1 "economy",2 "bangladesh", 3 "opinion", 4 "life-style", 5 "entertainment", 6 "pachmisheli",7 "international"]
choose_topic = article_array[7]

print("The topic you chose {}".format(choose_topic))

start_crawling(1,choose_topic)

