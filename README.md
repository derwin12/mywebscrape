# xLights Sequences For Sale Scraper
#
#

## Notes
The `requirements.txt` file should list all Python libraries that your notebooks
depend on, and they will be installed using:

```
pip install -r requirements.txt
cd webscrape
python.exe app.py
```

Open localhost:5000 from browser


Install in Pi Notes:
``` 
 sudo apt-get install chromium-chromedriver
 sudo apt install zsh fzf curl tmux git neovim automake autoconf libreadline-dev libncurses-dev libssl-dev \
       libyaml-dev libxslt-dev libffi-dev libtool unixodbc-dev libbz2-dev libsqlite3-dev build-essential    zlib1g-dev
 git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.7.1
 asdf update
 asdf plugin-add python
 asdf install python 3.10.4
 asdf global python 3.10.4
 sudo apt-get install liblzma-dev
 sudo apt install libjpeg-dev
 pip3 install pillow
 sudo apt-get install build-essential libssl-dev libffi-dev     python3-dev cargo
 pip install cryptography
 
 CRONJOB
   5 15 * * * cd /home/pi/mywebscrape; sh -x ./runit.sh > /tmp/logit
```
