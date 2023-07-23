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

## Database Migrations
Edit the classes in app/__init__.py for the database schema

```$ flask db migrate -m "Some comment"```

```$ flask db upgrade ```

Sample: 
```
    flask db migrate -m "Adding vendor count"
    INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
    INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
    INFO  [alembic.autogenerate.compare] Detected added column 'vendor.sequence_count'
    Generating migrations/versions/f38b854cb661_adding_vendor_count.py ...  done
    flask db upgrade
    INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
    INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
    INFO  [alembic.runtime.migration] Running upgrade 77fdfbc43629 -> f38b854cb661, Adding vendor count
```
## Analytics
Cloudflare dashboard provides data on hits and data transfers
Google Analytics provides hits on outbound links
