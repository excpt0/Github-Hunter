# -*- coding: utf-8 -*-

import configparser
import os
import re
import smtplib
import sqlite3
import sys
import traceback
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr
from time import gmtime, sleep, strftime
import json

import requests
from lxml import etree
from lxml.html import tostring
from tqdm import tqdm


USE_JSON = True
USE_SQLITE = False

'''
GithubHunter by Allen_Zhang
'''

def login(username, password):
    login_url = 'https://github.com/login'
    session_url = 'https://github.com/session'
    try:
        s = requests.session()
        resp = s.get(login_url).text
        dom_tree = etree.HTML(resp)
        key = dom_tree.xpath('//input[@name="authenticity_token"]/@value')
        user_data = {
            'commit': 'Sign in',
            'utf8': '✓',
            'authenticity_token': key,
            'login': username,
            'password': password
        }

        s.post(session_url,data=user_data)
        s.get('https://github.com/settings/profile')
        return s
    except Exception as e:
        print('Cant login to GitHub')
        handle_exception(str(e), traceback.format_exc())


def hunter(username, password, keywords):

    print('''\033[1;34;0m     #####                                  #     #                                   
    #     # # ##### #    # #    # #####     #     # #    # #    # ##### ###### #####  
    #       #   #   #    # #    # #    #    #     # #    # ##   #   #   #      #    # 
    #  #### #   #   ###### #    # #####     ####### #    # # #  #   #   #####  #    # 
    #     # #   #   #    # #    # #    #    #     # #    # #  # #   #   #      #####  
    #     # #   #   #    # #    # #    #    #     # #    # #   ##   #   #      #   #  
     #####  #   #   #    #  ####  #####     #     #  ####  #    #   #   ###### #    #    V2.1 
                                                                                         Created by Allen   \r\n\r\n\033[0m''')

    s = login(username, password)
    print('Starting...')
    sleep(1)
    results = []
    pbar = tqdm(total=len(keywords) * 9)
    for words in keywords:
        for page in range(1, 10):
            # s=indexed removed
            query = 'o=desc&p={}&q={}&type=Code'.format(page, '+'.join(words))
            resp = s.get('https://github.com/search?' + query)
            dom_tree_code = etree.HTML(resp.text)

            items = dom_tree_code.xpath('//div[@class="hx_hit-code code-list-item d-flex py-4 code-list-item-public "]')

            for item in items:
                url = 'https://github.com' + item.xpath('div/div[@class="f4 text-normal"]/a/@href')[0]
                code_items = item.xpath('div//span[@class="text-bold bg-yellow-light rounded-1 d-inline-block"]')
                code = []

                for div in code_items:
                    result = etree.tostring(div, pretty_print=True, method="html")

                    if any([w.lower() in code for w in words]):
                        code.append(str(result, encoding='utf-8'))

                if code:
                    results.append({'url': url, 'code': '\n'.join(code)})

            pbar.update()

    return results


def make_db_record(url, code):
    try:
        conn = sqlite3.connect('hunter.db')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS Baseline (url varchar(1000) primary key, code varchar(10000))')
        cursor.execute('INSERT OR REPLACE INTO Baseline (url, code) values (?,?)', (url, code))
        cursor.close()
        conn.commit()
        conn.close()
    except Exception as e:
        print("Ooops, something went wrong！\n")
        handle_exception(str(e), traceback.format_exc())
        print(e)


def is_exists(url):
    try:
        con = sqlite3.connect('hunter.db')
        cur = con.cursor()
        cur.execute('SELECT url from Baseline where url = ?', (url,))
        results = cur.fetchall()
        cur.close()
        con.commit()
        con.close()
        return results
    except Exception as e:
        handle_exception(str(e), traceback.format_exc())
        print(e)


def handle_exception(error, tb):
    try:
        with open('error.txt', 'w+', encoding='utf-8') as f:
            f.write(strftime("%a, %d %b %Y %H:%M:%S",gmtime()) + "-" + "Exception Record: " + error + '\n\n' +tb + '\r\n')
    except Exception as e:
        print(e)


def format_record(url, code, words):
    formatted = code.replace(words[0],'<em style="color:red">' + words[0] + '</em>')
    formatted = formatted.replace(words[1],'<em style="color:red">' + words[1] + '</em>')
    return '<br><br><br>' + 'link：' + url + '<br><br>' + \
        'Keywords: <em style="color:red">{}</em><br><br>'.format(', '.join(words)) + \
        'Code： <br><div style="border:1px solid #bfd1eb;background:#f3faff">' + formatted + '</div>'


def save_report(filename, results):
    with open('{}-report.html'.format(filename), 'w') as fileout:
        fileout.write(results)


def run():
    config = configparser.ConfigParser()
    config.read('info.ini')
    username = config['Github']['user']
    password = config['Github']['password']
    keywords = []
    reports = []
    json_data = {}

    for keyword in config['KEYWORDS']['keywords'].split(','):
        for payload in config['KEYWORDS']['payloads'].split(','):
            keywords.append((keyword, payload))

    results = hunter(username, password, keywords)

    dbexists = True

    if not os.path.exists('hunter.db'):
        dbexists = False
        print("DB not exists, so creating new")

    for words in keywords:
        for item in results:
            new_report = False

            if USE_JSON:
                json_data[item['url']] = item['code']
                new_report = True

            if USE_SQLITE and (not dbexists or (dbexists and not is_exists(item['url']))):
                make_db_record(item['url'], item['code'])
                new_report = True

            if new_report:
                reports.append(format_record(item['url'], item['code'], words))

    if reports:
        print('Found %d new items!' % (len(reports)))

        warning = ''.join(reports)
        result = '<html>Found {} new items! '.format(len(reports)) + '<em style="color:red"> {} </em>'.format(
            len(reports)) + warning + '</html>'

        filename = strftime("%a-%d-%b-%Y-%H%M", gmtime())
        save_report(filename, result)

        if USE_JSON:
            with open('{}.json'.format(filename), 'w') as json_file:
                json_file.write(json.dumps(json_data))

    else:
        print('No new founds =(')


if __name__ == '__main__':
    run()
