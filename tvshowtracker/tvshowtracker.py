'''
UK TV show tracker.

Extracts information from tvguide.co.uk and for user selected shows
sends a daily email reminder letting the user know if the one of the
selected shows is on for the given day.

Uses postgresql for the database and scrapy for retrieving the data
from the webpage.  

Mailing is set up for gmail currently.
'''

import datetime
import time 
from twisted.internet import reactor
from scrapy.crawler import Crawler
import scrapy.settings.default_settings as default_settings
from scrapy.settings import Settings
from scrapy import signals
from spiders import MySpiders 
import smtplib
import sys
import json
from multiprocessing import Process
import psycopg2

class Database(object):
    
    def __init__(self):
        #init connection and cursor
        try:
            self.conn = psycopg2.connect("dbname='showdb' user='someuser' host='localhost' password='12345678'")
        except psycopg2.DatabaseError, e:
            print 'Error %s' % e  
        self.cur = self.conn.cursor()
    
    def update(self):
        #update the table
        data = self._yield_data()
        for item in data:
            self.cur.execute("INSERT INTO shows VALUES (%(show)s, %(channel)s, %(time)s)", item)
            self.conn.commit()

    def query(self, show):
        self.cur.execute("SELECT * FROM shows WHERE show=%(show)s", {'show':show})
        return self.cur.fetchall()
    
    def clear(self):
        self.cur.execute("DELETE FROM shows")
        self.conn.commit()
                    
    def _yield_data(self):
        with open('my_spider_items.json') as f:
            my_dict = json.load(f)
            for item in my_dict:
                yield item
      
class WebCrawler():
    
    def __init__(self):
        default_settings.ITEM_PIPELINES = 'pipelines.JsonExportPipeline' #EDIT THIS TO PICKLE OR WORK OUT JSON
        self.crawler = Crawler(Settings())
        self.crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
        self.crawler.configure()
            
    def _crawl(self, url):
        spider = MySpiders.TvShowSpider(start_url=url)
        self.crawler.crawl(spider)
        self.crawler.start()
        reactor.run()
        
    def run(self, url):
        p = Process(target=self._crawl, args=[url])
        p.start()
        p.join()
        
class Mailer(object):
    
    def __init__(self, fromaddr,toadrrs,username,password):
        self.fromaddr = fromaddr
        self.toaddrs  = toadrrs 
        self.username = username 
        self.password = password
        self.subject = 'Show Reminder!'
        
    def send_mail(self, body):
        server = smtplib.SMTP('smtp.gmail.com:587')  
        server.starttls()  
        server.login(self.username,self.password)  
        msg = 'Subject: %s\n\n%s' % (self.subject, body)
        server.sendmail(self.fromaddr, self.toaddrs, msg)  
        server.quit()  
        
class ChannelTracker(object):
    
    def __init__(self, database, webcrawler, mailer, shows):
        self.database = database 
        self.webcrawler = webcrawler
        self.mailer = mailer
        self.shows = shows 
        
    def update_channels(self, now):
        #clear db
        self.database.clear()
        
        #crawl and insert crawled data into db
        for url in self._get_urls(now):
            self.webcrawler.run(url=url) #run is multithreaded
            self.database.update()
                             
    def todays_shows(self):
        if len(self.shows) != 0:
            for selected_show in self.shows:
                show_list = self.database.query(selected_show)
                if show_list != None:
                    show_list = self._remove_duplicates(show_list)
                    for each_show in show_list:
                        self._send_alert(each_show)
                        
    def _remove_duplicates(self, show_list):
        return list(set(show_list))
                    
    def _get_urls(self, now):
        url_list = []
        base_url = 'http://www.tvguide.co.uk/?systemid=&thistime=%s&thisday=%s&ProgrammeTypeID=&gridSpan=06:00&catColor='
        
        #define the urls for the day
        date = str(now.month) + '/' + str(now.day) + '/' + str(now.year)
        for hour in ['1','7','13','19']:
            url_list.append(base_url % (hour,date))
    
        return url_list
                    
    def _send_alert(self, show_info): 
        msg = show_info[0] + ' is starting at ' + str(show_info[2]) + ' on ' + show_info[1]  
        self.mailer.send_mail(body=msg)
                 
    
def main():

    #parse the user info.  
    mail_info = raw_input("Enter email address to recieve notifications (only works with gmail): ")
    passwd = raw_input("Enter email account password: ")
    shows = []
    while True:
        user_input = raw_input("Enter shows to track.  If all shows to track entered, then enter 'n': ")
        if user_input == "n":
            break
        else:
            shows.append(user_input)

    #generate objects
    database = Database()
    webcrawler = WebCrawler()
    mailer = Mailer(mail_info, mail_info, mail_info, passwd)
    tracker = ChannelTracker(database, webcrawler, mailer, shows)
    
    #preset current day
    current_day = (datetime.datetime.now() - datetime.timedelta(1)).day
    
    #iterate
    while True:
                
        #if a new day run the tracker...
        if datetime.datetime.now().day != current_day:
            tracker.update_channels(datetime.datetime.now())
        
            #...and check for upcoming shows
            tracker.todays_shows()
            
            current_day = datetime.datetime.now().day
            
        #sleep for some time
        time.sleep(36000)
        
        #TODO implement a process to kill the app

if __name__ == '__main__':
    sys.exit(main())
