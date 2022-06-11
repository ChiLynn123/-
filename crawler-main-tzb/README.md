# crawler
Base on selenium stimulate browser to crawl website.

## enviroment. 
wfd docker container.

## linux setup enviroment
### First install chrome browser.
In centos
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm

sudo dnf localinstall google-chrome-stable_current_x86_64.rpm
```
In ubuntu
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

sudo apt install ./google-chrome-stable_current_amd64.deb
```

### Then check chrome version
```bash
google-chrome --version
```
Google Chrome 91.0.4472.114

### Download same version webdriver to `/usr/bin/chromedriver`
In this url `https://chromedriver.storage.googleapis.com/index.html`, you should find same main version of webdriver.
chrome browser version is 91.0.4472.114.
chrome webdriver version  91.0.4472.XX will work.
It works fine for me , my webdriver version is 91.0.4472.19.
```bash
wget https://chromedriver.storage.googleapis.com/91.0.4472.19/chromedriver_linux64.zip --no-check-certificate
sudo unzip chromedriver_linux64.zip
```

Than copy webdriver to code setting driver dir.
```bash
cp ./chromedriver /usr/bin/

```

### watermaker font setup
In centos and ubuntu
First make directory 
```bash
sudo mkdir /usr/share/fonts/chinese
sudo chmod -R 777 /usr/share/fonts/chinese
```
than copy ./fonts/wqy-zenhei.ttc to new directory
```bash
cp ./fonts/wqy-zenhei.ttc /usr/share/fonts/chinese
```
Rebuild the font cache by entering at a terminal:
```bash
sudo fc-cache -f -v
```

### selenium enviroment setup
python 3.7 or higher.
```bash
pip install -r requirements.txt
```



The enviroment setup complete.  Congratulation!!!



## Usage 

```bash
usage: crawler.py [-h] -seed INFILE [-process PROCESS] [-wait TIME_WAIT]
                  [-num NUM] [-logname USER_LOG]
                  [-level {DEBUG,INFO,WARNNING,CRITICAL}]
                  [-scheme {http,https}]

Crawler test function

optional arguments:
  -h, --help            show this help message and exit
  -seed INFILE, -s INFILE
                        input url txt.
  -process PROCESS, -p PROCESS
                        number of process in crawler. default 2.
  -wait TIME_WAIT, -w TIME_WAIT
                        each crawler wait secs. default 30.
  -num NUM, -n NUM      deal numbers lines in url txt. default -1.
  -logname USER_LOG, -l USER_LOG
                        user define log filename.
  -level {DEBUG,INFO,WARNNING,CRITICAL}
                        user define log level. default INFO.
  -scheme {http,https}, -sch {http,https}
                        If user didn't set domain's scheme , program will ping
                        http first. If http scheme connect program will crawl
                        http://{domain}, otherwise it will crawl
                        https://{domain}.

```

```
crawler_result #crawler result in this directory.
crawler_seed # optional input url txt file directory.
Logs/Crawler.log #overwrite when every task run.

the outfile of result directory format in this type.
filename_ymd_hms/ eg:qingdao-0519_20210521_124308
In result directory:
  pics  #screenshot directory
  qingdao.log  # if user define log.
  result_w_30_s_https.csv # crawler txt info. w_{num} means time_wait parameter. s_{schema} means user define schema.

```
