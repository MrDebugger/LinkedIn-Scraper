from bs4 import BeautifulSoup as bs
from mysql.connector import connect
from os import path
import requests as rq
import json
import csv
import time


def getSettings():
    if path.exists('scraper.conf'):
        with open('scraper.conf') as file:
            lines = file.read().splitlines()
            settings = json.loads(('{"'+'","'.join(lines)+'"}').replace('=','":"'))
            return settings
    else:
        return None

def login():
    global ses, SETTINGS, token, PROXY
    d = {
    'session_key': SETTINGS['email'],
    'session_password': SETTINGS['password'],
    'isJsEnabled': 'false',
    'loginCsrfParam': token,
    'fp_data': 'default'
    }
    r = ses.post('https://www.linkedin.com/uas/login-submit?loginSubmitSource=GUEST_HOME',proxies=PROXY,data=d)

    if 'feed' in r.url:
        return True
    else:
        return False

def getInput():
    user = input("Enter username to scrap (Leave Blank for self profile): ")
    pages = input("Enter Pages Number seperated by Commas (Blank for all): ")
    
    if not pages:
        pages = ['-1']
    else:
        if '-' in pages:
            try:
                pages = [str(page) for page in range(int(pages.split('-')[0]),int(pages.split('-')[1])+1)]
            except:
                print("[-] Invalid Input")
                exit()
        else:
            pages = pages.replace(' ','').split(',')
    return user,pages


def getProfile(user):
    global ses, PROXY
    tries = 0
    while True:
        r = ses.get('https://www.linkedin.com/voyager/api/identity/profiles/{link}/profileView'.format(link=user),proxies=PROXY)
        try:
            j = json.loads(r.text)
            tries = 0
            break
        except:
            if tries>4:
                print("------------- SCRAPER DETECTED OR SECURITY CHECKUP --------------------")
                exit()
            tries+=1
            continue
    Id = j['publicationView']['profileId']
    return Id

def getConnections(profile='',page=-1):
    global ses, PROXY
    names=[]
    links=[]
    counts=0
    prof = ''
    while True:
        if profile:
            if not page == -2:
                i = page+1
                prof = 'https://www.linkedin.com/search/results/people/?facetConnectionOf=["{profile}"]&facetNetwork=["F","S"]&origin=MEMBER_PROFILE_CANNED_SEARCH&page={i}'.format(profile=profile,i=i)
            else:
                print("[-] Please Specify Pages as well")
                return [],[],0
        else:
            if page == -2:
                count = 2000
                i=0
            else:
                count = 40
                i = 40*page
            prof = "https://www.linkedin.com/voyager/api/relationships/connections?count={count}&sortType=RECENTLY_ADDED&start={i}".format(i=i,count=count)
        if not prof:
            break
        r = ses.get(prof,proxies=PROXY)
        t = r.text
        
        if profile:
            soup = bs(r.content,'lxml')
            codes = soup.find_all('code')
            for code in codes:
                code = code.get_text().replace('&quot;',"'")
                if code.count('firstName')>3 and code.count('occupation')>3 and code.count('lastName')>3:
                    t = code
                    break
        try:
            j = json.loads(t)
        except:
            print("[-] Connections of User is not publicly Available")
            return [],[],0
        if profile:
            datas = ''
            for d in j['data']['elements']:
                try:
                    d['elements'][1]['title']['text']
                    d['elements'][1]['publicIdentifier']
                    datas = d['elements']
                except:
                    pass
            if not datas:
                print("[-] Connections of User is not publicly Available")
                return [],[],0
        else:
            datas = j['elements']
        for d in datas:
            try:
                if not profile:
                    data = d['miniProfile']
                    f = data['firstName']
                    l = data['lastName']
                    p = data['publicIdentifier']
                else:
                    data = d
                    name = str(d['title']['text'].encode())[2:-1].replace("\\x",'')
                    f = ''
                    l = ''
                    p = d['publicIdentifier']
                fname = str(f.encode())[2:-1].replace("\\x",'')
                lname = str(l.encode())[2:-1].replace("\\x",'')
                if profile:
                    names.append(name)
                else:
                    names.append(fname+' '+lname)
                links.append(p)
                counts+=1
            except:
                pass
        if not page==-1:
            break
        i+=2000
    return links,names,counts
    
SETTINGS = getSettings()
con = False
if SETTINGS['proxyIp']:
    PROXY = {
        'http' : 'http://{ip}:{port}'.format(ip=SETTINGS['proxyIp'],port=SETTINGS['proxyPort'])
    }
else:
    PROXY = {}
print("+++++LinkedIn SCRAPER++++++++")

try:
    DB = connect(
          host=SETTINGS['dbHost'],
          user=SETTINGS['dbUser'],
          passwd=SETTINGS['dbPass'],
          database=SETTINGS['dbName']
        )
except:
    print("[-] Database Error Occured.")
    if input("[>] Do you want to Continue? (y/n) ").lower()[0]=='n':
        print("Program End")
        exit()
    else:
        con = True

ses = rq.Session()
ses.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
try:
    r = ses.get('https://www.linkedin.com/',proxies=PROXY)
except:
    print("[-] Connection Or Proxy Error")
    exit()
soup = bs(r.content,'lxml')
csrf = soup.find('input',{'name':'loginCsrfParam'})
try:
    token = csrf.attrs['value']
except:
    print("[-] If you have opened used account in Browser, Close it.")
    exit()

print('-'*10)
print("[=] Trying to Login")
if not login():
    print("[-] Failed to login")
    print("\n[=] Trying Again")
    if not login():
        print("[-] Failed to login")
        exit()
    else:
        print("[+] Logged in Successfully")
else:
    print("[+] Logged in Successfully")
print('-'*10)

ses.headers['csrf-token'] = ses.cookies['JSESSIONID'].replace('"','')

try:
    stop = False
    links,names,counts = [],[],0
    username,pages = getInput()
    if username:
        profile = getProfile(username)
    else:
        profile = ''
    print("\n[=] Getting Connections")
    for page in pages:
        l,n,c = getConnections(profile,int(page)-1)
        links+=l
        names+=n
        counts+=c
        if c:
            print("{p}[+] {c} Connections Retrieved from page {page} {o}".format(c=counts,page=page,o=(', Retrieving More','')[page==pages[-1]],p=('','\n')[page==pages[0]]))
            time.sleep(10)
        else:
            break
    print("[+] ",counts,'Connections found')
    allData = []
    emp_id = 0
    cmp_id = 1
    edu_id = 1
    with open('employes.csv','w',newline='',encoding='utf-8') as file:
        with open('companies.csv','w',newline='',encoding='utf-8') as file2:
            with open('educations.csv','w',newline='',encoding='utf-8') as file3:
                emp = csv.writer(file)
                emp.writerow(['id','connection_id','connection_name','title','address','cur_comp','connection_email','connection_phone'])
                Cmp = csv.writer(file2)
                Cmp.writerow(['id','connection_id','company','company_location','job_title','start_date','end_date'])
                edu = csv.writer(file3)
                edu.writerow(['id','connection_id','school','degree','grade','start_date','end_date'])
                
                for link,name in zip(links,names):
                    emp_id += 1
                    print("\nVisiting '"+name+"' Profile")
                    tries = 0
                    while True:
                        r = ses.get('https://www.linkedin.com/voyager/api/identity/profiles/{link}/profileView'.format(link=link),proxies=PROXY)
                        try:
                            j = json.loads(r.text)
                            tries = 0
                            break
                        except:
                            if tries>4:
                                print("------------- SCRAPER DETECTED OR SECURITY CHECKUP -----------------")
                                exit()
                            tries+=1
                            continue
                    tit = 'NULL'
                    address ='NULL'
                    curComp = 'NULL'
                    try:
                        tit = str(j['profile']['headline'].encode())[2:-1].replace('\\x','')
                        address = str(j['profile']['locationName'].encode())[2:-1].replace('\\x','')
                    except:
                        pass
                    for comp in j['positionView']['elements']:
                        try:
                            curComp = str(comp['company']['miniCompany']['name'].encode())[2:-1].replace('\\x','')
                            break
                        except:
                            pass
                   # can you chek it thhrough exlorer it shows blank here ?
                    cp = 0
                    eds = 0
                    for comp in j['positionGroupView']['elements']:
                        try:
                            companyName =str(comp['positions'][0]['companyName'].encode())[2:-1].replace('\\x','')
                            if curComp == 'NULL':
                                curComp = companyName
                            cp+=1
                            try:
                                title = str(comp['positions'][0]['title'].encode())[2:-1].replace('\\x','')
                            except:
                                title = 'NULL'

                            try:
                                cmp_loc = str(comp['positions'][0]['locationName'].encode())[2:-1].replace('\\x','')
                            except:
                                cmp_loc = 'NULL'

                            try:
                                st_date = comp['positions'][0]['timePeriod']['startDate']
                                st_date = ', '.join([str(val) for val in st_date.values()])
                            except:
                                st_date = 'NULL'
                            try:
                                en_date = comp['positions'][0]['timePeriod']['endDate']
                                en_date = ', '.join([str(val) for val in en_date.values()])
                            except:
                                en_date = 'Present'
                            Cmp.writerow([cmp_id,emp_id,title,companyName,cmp_loc,st_date,en_date])
                            try:
                                cursor = DB.cursor()
                                QUERY = "INSERT INTO " + SETTINGS['compTable'] + "(connection_id,company,company_location,job_title,start_date,end_date) VALUES(%s,%s,%s,%s,%s,%s)"
                                VALUES = (emp_id,companyName,cmp_loc,title,st_date,en_date)
                                #it will be great if you shift to 3.6 or abve, sure, let's do it
                                cursor.execute(QUERY,VALUES)
                                DB.commit()
                            except Exception as e:
                                print(e)
                                if not con:
                                    print("\nDATABASE ERROR: Data won't be Saved in Database\n")
                                    if input("Press Enter to continue or write something to exit: "):
                                        print("Program Stopped")
                                        exit()
                                    else:
                                        con = True
                            cmp_id += 1    
                        except:
                            pass


                    for comp in j['educationView']['elements']:
                        try:
                            eduName = str(comp['schoolName'].encode())[2:-1].replace('\\x','')
                            eds+=1
                            try:
                                title = str(comp['degreeName'].encode())[2:-1].replace('\\x','')
                            except:
                                title = 'NULL'
                            
                            try:
                                grade = str(comp['grade'].encode())[2:-1].replace('\\x','')
                            except:
                                grade = 'NULL'

                            try:
                                st_date = comp['timePeriod']['startDate']
                                st_date = ', '.join([str(val) for val in st_date.values()])
                            except:
                                st_date = 'NULL'
                            try:
                                en_date = comp['timePeriod']['endDate']
                                en_date = ', '.join([str(val) for val in en_date.values()])
                            except:
                                en_date = 'Present'
                            edu.writerow([edu_id,emp_id,eduName,title,grade,st_date,en_date])
                            try:
                                cursor = DB.cursor()
                                QUERY = "INSERT INTO " + SETTINGS['eduTable'] + "(connection_id,school,degree,grade,start_date,end_date) VALUES(%s,%s,%s,%s,%s,%s)"
                                VALUES = (emp_id,eduName,title,grade,st_date,en_date)
                                cursor.execute(QUERY,VALUES)
                                DB.commit()
                            except:
                                if not con:
                                    print("\nDATABASE ERROR: Data won't be Saved in Database\n")
                                    if input("Press Enter to continue or write something to exit: "):
                                        print("Program Stopped")
                                        exit()
                                    else:
                                        con = True
                            edu_id += 1
                        except:
                            pass
                            
                    print('\tTitle:',tit)
                    print('\tAddress:',address)
                    print('\tCurrent Company:',curComp)
                    print('\tGetting Companies')
                    print('\t\t[+]',cp,"Companies Found")
                    print('\t\t[+]',eds,"Educations Found")
                    print("\t[=] Getting Contact Infos")
                    tries = 0
                    while True:
                        r = ses.get('https://www.linkedin.com/voyager/api/identity/profiles/{link}/profileContactInfo'.format(link=link),proxies=PROXY)
                        try:
                            j = json.loads(r.text)
                            tries = 0
                            break
                        except:
                            if tries>4:
                                print("------------- SCRAPER DETECTED OR SECURITY CHECKUP -----------------")
                                exit()
                            tries+=1
                            continue
                    try:
                        email = j['emailAddress']
                    except:
                        email = 'NULL'
                    
                    try:
                        phone = []
                        for ph in j['phoneNumbers']:
                            phone.append(ph['number'])
                        phone = ','.join(phone)
                    except:
                        phone = 'NULL'

                    emp.writerow([emp_id,emp_id,name,tit,address,curComp,email,phone])
                    try:
                        cursor = DB.cursor()
                        QUERY = "INSERT INTO " + SETTINGS['empTable'] + "(connection_id,connection_name,title,address,cur_comp,connection_email,connection_phone) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                        VALUES = (emp_id,name,tit,address,curComp,email,phone)
                        cursor.execute(QUERY,VALUES)
                        DB.commit()
                    except Exception as e:
                        if not con:
                            print("\nDATABASE ERROR: Data won't be Saved in Database\n")
                            if input("Press Enter to continue or write something to exit: "):
                                print("Program Stopped")
                                exit()
                            else:
                                con = True
                    
                    if email:
                        print('\t\t[+] Email:',email)
                    
                    if phone:
                        print('\t\t[+] Phone:',phone)
                    if not name == names[-1]:
                        print('\n[------------------------ WAITING 10 SECONDS ------------------]')
                        time.sleep(10)


except KeyboardInterrupt:
    print("Program Stopped")
