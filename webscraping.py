# from bs4 import BeautifulSoup
# import requests
from selenium import webdriver
from datetime import datetime, timedelta
# from csv import writer
# from webdriver_manager.chrome import ChromeDriverManager
import time
# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client
import smtplib
import os
import schedule

from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)



# i is increased as a job that was posted on the correct day is collected
i = 0
pg_num = 1
# job_num increases with every job iterated through, even if not posted that day (this is used to figure out if we need to go to page 2)
job_num = 0
# res_num iterates through the results we are interested in (posted that day) (same as i, but we use this instead of moving i back to 0 and reusing i)
res_num = 0

# jobs_searched_thru = 0

# sms_body will be sent over text
sms_body = ""
# email_body will be sent over email
email_body = ""
# driver = webdriver.Chrome(ChromeDriverManager().install())
email_subject = ""
# print(jobs)

# d is today's date (or yesterday's date depending if job was posted midnight est or pst)
d = (datetime.now()).strftime("%m/%d/%Y")
# d = (datetime.now() - timedelta(1)).strftime("%m/%d/%Y")
# results holds all results from that day
results = []
# relevant_results are results from that day that we are interested in
relevant_results = []

print("will search now...")
def running(i, pg_num, job_num, res_num, sms_body, email_body, email_subject):

    list_words = ["Technician", "Park", "Technology", "Ranger", "Interp", "Interpretation", "Guide"]

    PATH = "C:\Program Files (x86)\chromedriver.exe"
    driver = webdriver.Chrome(PATH)


    # https://www.usajobs.gov/Search/Results?g=6&g=7&g=5&d=IN&show=ser&hp=public&k=nps&s=startdate&p=1&gs=true&smin=34916&smax=56222
    url = "https://www.usajobs.gov/Search/Results?hp=public&k=nps&s=startdate&p=" + str(pg_num)

    # comp is slow, gotta wait to get all the results
    driver.implicitly_wait(20)
    driver.get(url)

    # jobs is a list of all jobs on pg 1
    jobs = driver.find_elements_by_class_name("usajobs-search-result--core")



    # jobs_searched_thru will be len(jobs) and subtract 1 each time we iterate through a job. used to decide if its time to go to page 2 or if its time to send notifications
    jobs_searched_thru = len(jobs)


    for job in jobs:
        print("jobs_searched_thru = " + str(jobs_searched_thru))
        jobs_searched_thru -= 1
        job_num += 1
        print("____________________________________________________")
        # figure out the date it was posted
        opendate = job.find_element_by_class_name("usajobs-search-result--core__closing-date")
        print("today is " + str(d) + " and opendate is " + str(opendate.text[31:41]))
    # [31:41]
    # [5:15]

        # if the job was posted today, add info to results
        if str(opendate.text[31:41]) == str(d):
            for value in job.find_elements_by_class_name("usajobs-search-result--core__title"):
                print("i = " + str(i))
                # create dict, then start adding to results
                results.append("result_" + str(i))
                results[i] = {}
                # job title below
                results[i]['title'] = value.text
                # link to job below
                results[i]['link'] = value.get_attribute("href")
                print(results[i])
            for location in job.find_elements_by_class_name("usajobs-search-result--core__location-link"):
                print("location is:")
                print(location)
                # job location below
                results[i]['location'] = location.text[:len(location.text)//2]
                print(results[i]['location'])
            # search gs level and time on job (seasonal? temp? perm?)
            gs = job.find_element_by_class_name("usajobs-search-result--core__details-list")
            items = gs.find_elements_by_tag_name("li")
            # for item in items:
            results[i]['GS and salary'] = items[0].text
            results[i]['time commitment'] = items[1].text.replace("\u2022", "-")
            # if we are on the last entry on page one and we've gotten this far..
            print("i = " + str(i))
            print("jobs len = " + str(len(jobs)-1))
            print("job_num = " + str(job_num))
            print("lenjobs = " + str(len(jobs)))
            print(job_num == len(jobs))
            if (job_num == len(jobs)):
                print("moving to page 2")
                pg_num += 1
                job_num = 0
                running(i, pg_num, job_num, res_num, sms_body, email_body, email_subject)
            # elif jobs_searched_thru == 0:
            #     print("=================================---------------------===============================")
            #     print("serached through all jobs on the page")
            #     organize_and_send(list_words, results, res_num, relevant_results, sms_body, email_body, email_subject)



            i += 1
            print("i is now " + str(i))
            # results.append(value.text)
            print("-------------------------------")

        if jobs_searched_thru == 0:
            print("=================================---------------------===============================")
            print("serached through all jobs on the page")
            organize_and_send(list_words, results, res_num, relevant_results, sms_body, email_body, email_subject)
    print(results)



def organize_and_send(list_words, results, res_num, relevant_results, sms_body, email_body, email_subject):
    # entry_number = 0
    print(results)
    # only print jobs you're intersted in
    for word in list_words:
        # print(results)
        print("____________________________________________________")
        print("searching in list_words : " + word)
        for entry in results:
            print("ASDFASDFASDFASDFADFS")
            print("entry:")
            print(entry)
            # print(entry['title'])
            # print("title: ")
            # print(entry[entry_number].title)
            # if it matches, print
            # if entry_number + 1 != len(results):
            if word in entry["title"]:
                relevant_results.append(entry)
                # entry_number+=1


    # prep body for sms, email

    # if no results
    if len(relevant_results) == 0:
        sms_body = "No relevant jobs today"
        email_subject = 'No relevant USAJOBS jobs posted for ' + str(d)
        email_body = "No relevant jobs today"
    else:
        # set email subject
        email_subject = 'USAJOBS posted for ' + str(d)
        # format relevant info for each item
        for item in relevant_results:

            sms_body += f'{relevant_results[res_num]["title"]}, {relevant_results[res_num]["location"]}  {relevant_results[res_num]["link"]} .\n'

            email_body += f'{relevant_results[res_num]["title"]}\n{relevant_results[res_num]["location"]}\n{relevant_results[res_num]["GS and salary"]}\n{relevant_results[res_num]["time commitment"]}\n{relevant_results[res_num]["link"]}\n\n'

            res_num += 1

    print(sms_body)
    print(email_body)








    ACCOUNT_SID = os.getenv('ACCOUNT_SID')
    AUTH_TOKEN = os.getenv('AUTH_TOKEN')
    FROM_NUMBER = os.getenv('FROM_NUMBER')
    TO_NUMBER = os.getenv('TO_NUMBER')

    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    message = client.messages \
                    .create(
                         body=sms_body,
                         from_=FROM_NUMBER,
                         to=TO_NUMBER
                     )

    print(message.sid)





    # EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
    # EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')

    EMAIL_ADDRESS = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASS')
    SEND_TO_EMAIL = os.getenv('SEND_TO_EMAIL')

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        subject = email_subject
        body = email_body

        msg = f'Subject: {subject}\n\n{body}'

        # THIS IS THE FORMAT = smtp.sendmail(SENDER, RECIEVER, msg)
        smtp.sendmail(EMAIL_ADDRESS, SEND_TO_EMAIL, msg)


schedule.every().day.at("00:02").do(running, i, pg_num, job_num, res_num, sms_body, email_body, email_subject)
while True:
    schedule.run_pending()
    time.sleep(1)

# PATH = "C:\Program Files (x86)\chromedriver.exe"
# driver = webdriver.Chrome(PATH)
#
# list_words = ["Technician", "Park", "Technology", "Ranger", "Guide"]
# i = 0
# pg = 1
# url = "https://www.usajobs.gov/Search/Results?hp=public&k=nps&s=startdate&p=" + str(pg)
# results = []
# d = datetime.now().strftime("%m/%d/%Y")
#     # + timedelta(1)
# print(url)
# print(type(url))
# print("pg=" + str(pg))
# def search_page(url):
#     global jobs
#     print(str(url))
#     driver.get(url)
#     jobs = driver.find_elements_by_class_name("usajobs-search-result--core")
#     print(type(jobs))
#     print(jobs)
#
# def search_jobs(jobs):
#     print("running search_jobs")
#     print(jobs)
#     for job in jobs:
#         print("____________________________________________________")
#         opendate = job.find_element_by_class_name("usajobs-search-result--core__closing-date")
#         print("today is " + str(d) + " and opendate is " + str(opendate.text[5:15]))
#
#         # if the job was posted today, add info to results
#         if str(opendate.text[5:15]) == str(d):
#             for value in job.find_elements_by_class_name("usajobs-search-result--core__title"):
#                 print("i = " + str(i))
#                 # create dict, then start adding to results
#                 results.append("result_" + str(i))
#                 results[i] = {}
#                 # job title below
#                 results[i]['title'] = value.text
#                 # link to job below
#                 results[i]['link'] = value.get_attribute("href")
#                 print(results[i])
#             for location in job.find_elements_by_class_name("usajobs-search-result--core__location-link"):
#                 print("location is:")
#                 print(location)
#                 # job location below
#                 results[i]['location'] = location.text
#                 print(results[i])
#             # search gs level and time on job (seasonal? temp? perm?)
#             gs = job.find_element_by_class_name("usajobs-search-result--core__details-list")
#             items = gs.find_elements_by_tag_name("li")
#             # for item in items:
#             results[i]['GS and salary'] = items[0].text
#             results[i]['time commitment'] = items[1].text
#             # if we are on the last entry on page one and we've gotten this far..
#             if jobs[len(jobs)-1] == false:
#                 print("search page 2")
#
#
#
#
#
#
#         i += 1
#         print("i is now " + str(i))
#         # results.append(value.text)
#         print("-------------------------------")
#     print(results)
#
#     # only print jobs you're intersted in
#     for word in list_words:
#         # print(results)
#         print("running second loop ____________________________________________________")
#         print("searching in list_words : " + word)
#         for entry in results:
#             # if it matches, print
#             if word in entry['title']:
#                 print(entry)
#
# print("running stuff now!")
# search_page(url)
# search_jobs(jobs)















#                 results.append("result_" + str(i))
#                 results[i] = {}
#                 results[i]['title'] = value.text
#                 results[i]['num'] = i
#                 i += 1
# print(results)
#
#
#
# # results_i = []
# #
# # dict_results = {}
# # for i in range(5):
# #     results_i.append("result_" + str(i))
# #     results_i[i] = {}
# #     results_i[i]['name'] = "hello"
# #     results_i[i]['num'] = i
# #
# #     # ("result_" + str(i))['title'] = "name # " + str(i)
# #     # ("result_" + str(i))['number'] = i
# #     # dict_results.append("result_" + str(i))
# #     # results_i.append(dict_results["result_" + str(i)] = "name # " + str(i))
# #     # results_i.append(dict_results["result_" + str(i)] = "name # " + str(i))
# #     print(i)
# #     print(dict_results)
# #     print(results_i[i])
# #
# # # print(dict_results)
# # print(results_i)





# driver.quit()

# response = requests.get("https://www.usajobs.gov/Search/Results?hp=public&k=nps&s=startdate&p=1")
# print('request ran')
# print(response)
# soup =  BeautifulSoup(response.text, "html.parser" )
#
# # posts = soup.find_all("div", class_="usajobs-search-result--core")
# posts = soup.find_all("div", class_="usajobs-search-results-container")
# print("posts ran")
# print(posts)
#
# print(soup.title)
# # print(soup.find_all(class_="usajobs-search-result--core__agency"))
# for post in posts:
#     print(post)
#     # title = post.find(class_="usajobs-search-result--core__title search-joa-link").get_text().replace('\n', '')
#     # print(title)
