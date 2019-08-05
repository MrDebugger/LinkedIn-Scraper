# LinkedIn SCRAPER
  This scraper scraps connections data of own profile or someone else profile that has connections publicely or relatively available and save it to 3 csv files as well as upload to 3 tables in mysql database.

# INSTALLATION
  Installation is just easy, just copy and paste these files into a directory and run it.

# REQUIREMENTS
  * Python 3.6.x
  * MySQL Database
  * written Directory
  * LinkedIn Account
  * Proxy Ip and Port (optional)

# USAGE
  To Use this scraper, You need to do the following things.
  * Install Required Packages.
     Run the following Command to install required packages.
     `pip install -r requirements.txt`

  * Create Database and Tables
     Modify the details in `scraper.conf` file according to your need and run the following command in current directory.
     `python connector.py`

  * Running the Script
     Fill the details in `scraper.conf` and run following command in current directory.
     `python scraper.py`
 
  * Giving Inputs to Scraper
     On Running the scraper, it will ask for username of a person. 

     - To Scrap your own profile, Leave it blank and hit `Enter` or `RETURN`
     - To Scrap someone else profile,  enter his username.

     Next thing it will ask is page number
     
     - If you selected your own profile, then by leaving blank you can scrap all of your connections profile.
     - If you selected someone else profile, then you need to enter pages, seperated by commas (if you want to add more than one)

# PROXIES
  Proxies can be retrieved from here, Make sure you are picking http proxy not https, ftp or socks
  <a href='http://free-proxy.cz/en/proxylist/city/Toronto/all/ping'>Toronto Proxy List</a>