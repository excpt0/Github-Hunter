# Github-Hunter v2.3
This tool is for sensitive information searching on Github.
The fast version Please go to https://github.com/Hell0W0rld0/Github_Hunter_By_Golang
## Requirements
Python 3.x <br>
## OS Support
Linux,MacOS,Windows<br>
## Installation
1.`git clone https://github.com/Hell0W0rld0/Github-Hunter.git`<br>
Notice:Github Hunter only supports Python3.x, if you are using Python2.x,do some tests before use it<br>
2.`cd Github-Hunter`<br>
3.`pip install virtualenv`<br>
4.`virtualenv --python=/usr/local/bin/python3 env`<br>
5.`source venv/bin/activate`<br>
6.`pip install -r requirements`<br>
## Settings
Befor use it,you must change parameters in `info.ini.example`,then change filename(just delete `.example`)
### Example
`[KEYWORDS]`<br>
`keywords = your main keywords here, separated by "," (comma symbol)`<br>
`payloads = your payloads here, separated by "," (comma symbol)`<br>
`[Github]`<br>
`user = Github Username`<br>
`password = Github Password`<br>
<br>
### Keyword and Payloads
You can add many main keywords as you like, but i suggest add 2~5 keywords.<br>
The tool will combine keyword and payload. So keywords for searching will be "keyword + payload".You can customize your payloads,the more you add, the more sensitive information will be found.
## Run
`python GithubHunter.py`<br>
You will receive emails when application completes.<br>
There will be a .db file named hunter.db, this baseline includes urls and codes. Do not remove it<br>
The emails will be send contain urls and code.
## Screenshoot
### Running:
![Running](https://github.com/Hell0W0rld0/Github-Hunter/blob/master/1.jpg)
<br>
### Result:
![Result](https://github.com/Hell0W0rld0/Github-Hunter/blob/master/0.jpg)
