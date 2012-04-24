from BeautifulSoup import BeautifulSoup
import urllib,urllib2,cookielib
import logging
import os,re

#Variants used by spider
JIRA_LOGIN_URL = 'http://jirads3.ams.apc.com/login.jsp'
JIRA_LOGIN_REDIRECT = '/secure/IssueNavigator!executeAdvanced.jspa'
JIRA_SEARCH_URL = 'http://jirads3.ams.apc.com/secure/IssueNavigator!executeAdvanced.jspa'
JIRA_USER = 'qivhou'
JIRA_PASSWORD = 'starblue24' 

class JiraSpider:
    def __init__(self):
        self.isLogin = False
        #Simulate as a browser
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:10.0.2) Gecko/20100101 Firefox/10.0.2'
        }        
        logging.basicConfig(level=logging.DEBUG,format='%(asctime)-15s %(message)s') 
        
    def connect(self):
        # Post login info to server
        logindata = {
            'os_username' : JIRA_USER,
            'os_password' : JIRA_PASSWORD,
            'os_cookie' : 'true',
            'os_destination' : JIRA_LOGIN_REDIRECT
        }
        req = urllib2.Request(
            url = JIRA_LOGIN_URL,
            data = urllib.urlencode(logindata),
            headers = self.headers
        )
        #Enable cookie
        cjar = cookielib.LWPCookieJar()
        handler = urllib2.HTTPCookieProcessor(cjar)
        self.opener = urllib2.build_opener(handler)
        urllib2.install_opener(self.opener) 
        content =  urllib2.urlopen(req).read()
        #Global variant to store cookie
        #cookieFile = "cookies.dat"
        #self.cookie = page.info()['set-cookie'] 
        #cjar.save(cookieFile)
        #print  self.cookie
        logging.info("Connectting to " + JIRA_LOGIN_URL)
        soup = BeautifulSoup(content)
        #Validate if it redirects to JIRA_LOGIN_REDIRECT page
        if soup.findAll(attrs={'id' : 'jqltext'}) :
            self.isLogin = True
            logging.info("Connected to %s" % JIRA_LOGIN_URL)
        else :
            logging.info("Connect failed to %s" % JIRA_LOGIN_URL)
        
    def getCount(self, filter):
        ret = 0
        if self.isLogin :
            # Post login info to server
            filterdata = {
                'jqlQuery' : filter,
                'runQuery' : 'true'
            }
            req = urllib2.Request(
                url = JIRA_SEARCH_URL,
                data = urllib.urlencode(filterdata),
                headers = self.headers
            )
            #Enable cookie
            #req.add_header('Cookie',self.cookie)
            #print  self.cookie
            #Added cookiet to header
            #urllib2.install_opener(self.opener) 
            content = urllib2.urlopen(req).read()
            logging.info("post filterData to " + JIRA_SEARCH_URL)
            #self.saveData(content,'jira.html')
            soup = BeautifulSoup(content)
            find_tag =  soup.find(attrs={'class' : 'results-count'}) 
            if find_tag != None:
                # Use re to find out the count
                pattern = re.compile(r'\d+')
                matchlist = pattern.findall(str(find_tag))
                ret = int(matchlist[len(matchlist)-1])
                logging.info("Filter : %s ,count : %s" % (filter,ret))   
            else :
                ret = 0
                logging.info("Filter Error : %s" % filter)
        else :
            ret = 0
            logging.info("Logging failed to %s" % JIRA_LOGIN_URL)                
        return  ret
         
    def saveData(self,content,filename):
        f = file(filename, 'wb')
        f.write(content)
        f.close()

# example        
if __name__ == '__main__':       
    jiratest = JiraSpider()
    jiratest.connect()
    print jiratest.getCount('project in (PROD)')
    print jiratest.getCount('project in (SEL)')
    print jiratest.getCount('project in (APCPRODOC)')