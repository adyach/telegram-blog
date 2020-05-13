# What is it? 
Simple web page with the text is made out of your public Telegram channel posts.

# Why do I need it?
I have not seen any available free solution on the internet, but there are paid versions, 
which in my opinion cost more tha they should.

# How to run
## Get api id and api hash
[How to register Telegram App](https://core.telegram.org/api/obtaining_api_id#obtaining-api-id)

from the link above:
```$xslt
In order to obtain an API id and develop your own application using the Telegram API you need to do the following:

Sign up for Telegram using any application.
Log in to your Telegram core: https://my.telegram.org.
Go to 'API development tools' and fill out the form.
You will get basic addresses as well as the api_id and api_hash parameters required for user authorization.
For the moment each number can only have one api_id connected to it.
```
## Get bot token
[How to create Telegram Bot](https://core.telegram.org/bots#6-botfather)

from the link above:
```
Use the /newbot command to create a new bot. The BotFather will ask you for a name and username, then generate an authorization token for your new bot.
The name of your bot is displayed in contact details and elsewhere.
The Username is a short name, to be used in mentions and t.me links. Usernames are 5-32 characters long and are case insensitive, but may only include Latin characters, numbers, and underscores. Your bot's username must end in ‘bot’, e.g. ‘tetris_bot’ or ‘TetrisBot’.
The token is a string along the lines of 110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw that is required to authorize the bot and send requests to the Bot API. Keep your token secure and store it safely, it can be used by anyone to control your bot.
```

## Create from existing channel
This command requires Telegram API user access, which requires you to login(will ask you for 
telephone number and will wait for confirmation code)
```shell script
export WEBSITE_NAME=https://example.com
export TELEGRAM_CHANNEL_NAME=your-awesome-channel
export TELEGRAM_API_ID=id
export TELEGRAM_API_HASH=hash
export TELEGRAM_BOT_TOKEN=token
export BLOG_EXPOSE_WAY=http

python3 bot.py build-from-scratch 
```
the output of command will be `index.html` in the current folder, which can be opened via browser.
In order to run http server use [listen-events](#Listen on new channel messages)

## Listen on new channel messages
```shell script
export WEBSITE_NAME=https://example.com
export TELEGRAM_CHANNEL_NAME=your-awesome-channel
export TELEGRAM_API_ID=id
export TELEGRAM_API_HASH=hash
export TELEGRAM_BOT_TOKEN=token
export BLOG_EXPOSE_WAY=http

python3 bot.py listen-events
```
Resulted `index.html` will be accessible at [http://localhost:8080](http://localhost:8080)

## Docker
```shell script
docker run docker.pkg.github.com/adyach/telegram-blog/telegablogbot:latest \
-e WEBSITE_NAME=your_web_blog \
-e TELEGRAM_CHANNEL_NAME=channel_name \
-e TELEGRAM_API_ID=api_id \
-e TELEGRAM_API_HASH=api_hash \
-e TELEGRAM_BOT_TOKEN=bot_token \
-e BLOG_EXPOSE_WAY=http
```

## Credits
[Pure Python 3 MTProto API Telegram client library](https://github.com/LonamiWebs/Telethon)