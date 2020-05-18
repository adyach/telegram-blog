import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import click
from telethon import TelegramClient, events
from telethon.tl import functions
from tinydb import TinyDB, where


class Config:
    def __init__(self,
                 website_name: str,
                 channel_name: str,
                 api_id: str,
                 api_hash: str,
                 bot_token: str,
                 photo_name: str,
                 db_file: str,
                 templates_path: str,
                 website_title: str,
                 website_description: str):
        self.website_name = website_name
        self.channel_name = channel_name
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self.channel_photo_name = photo_name
        self.db_file_name = db_file
        self.templates_path = templates_path
        self.website_title = website_title
        self.website_description = website_description

    @staticmethod
    def load_from_env():
        return Config(Config._get_env_or_fail('WEBSITE_NAME'),
                      Config._get_env_or_fail('TELEGRAM_CHANNEL_NAME'),
                      Config._get_env_or_fail('TELEGRAM_API_ID'),
                      Config._get_env_or_fail('TELEGRAM_API_HASH'),
                      Config._get_env_or_fail('TELEGRAM_BOT_TOKEN'),
                      os.getenv(
                          'TELEGRAM_CHANNEL_PHOTO_NAME', 'avatar_photo.jpg'),
                      os.getenv('TELEGRAM_DB_FILE_NAME', 'posts.json'),
                      os.getenv('TEMPLATES_PATH', 'templates'),
                      os.getenv('WEBSITE_TITLE', None),
                      os.getenv('WEBSITE_DESCRIPTION', None))

    @staticmethod
    def _get_env_or_fail(varname) -> str:
        val = os.getenv(varname)
        if val is None:
            raise Exception('failed to find varname: {}, aborting'.format(varname))
        return val


class Bot:
    def __init__(self, config: Config):
        self.config = config
        self.template_post = self._read_template(
            config.templates_path + '/template_post')
        self.template_head = self._read_template(
            config.templates_path + '/template_head')
        self.template_header = self._read_template(
            config.templates_path + '/template_header')
        self.template_html = self._read_template(
            config.templates_path + '/template_html')
        self.db = TinyDB(config.db_file_name)

    def clean_and_rebuild_blog(self):
        self.db.drop_tables()

        async def _rebuild():
            messages = await client.get_messages(self.config.channel_name, None)
            for m in messages:
                if m.message is None or m.message == '':
                    continue
                self._save_to_db(m.id,
                                 m.date.strftime("%b %d, %H:%M"),
                                 m.message)
            channel_info = await self._get_channel_info(client)
            self._create_html_and_write_to_disk(channel_info)

        with TelegramClient('withuser', self.config.api_id, self.config.api_hash) as client:
            client.loop.run_until_complete(_rebuild())

    def listen_for_channel_events(self):
        client = TelegramClient('telegabot', self.config.api_id, self.config.api_hash)
        client.start(bot_token=self.config.bot_token)

        async def _process_channel_event(event):
            if event.message.message is None or event.message.message == '':
                return

            self._save_to_db(event.message.id,
                             event.message.date.strftime("%b %d, %H:%M"),
                             event.message.message)
            channel_info = await self._get_channel_info(client)
            self._create_html_and_write_to_disk(channel_info)

        client.add_event_handler(_process_channel_event,
                                 events.NewMessage(chats=self.config.channel_name))
        with client:
            client.run_until_disconnected()

    def _create_html_and_write_to_disk(self, channel_info):
        website_title = channel_info['title'] if self.config.website_title is None else self.config.website_title
        website_description = channel_info[
            'about'] if self.config.website_description is None else self.config.website_description

        header = self.template_header \
            .replace('{{channel_name}}', self.config.channel_name) \
            .replace('{{channel_title}}', website_title) \
            .replace('{{channel_members}}', channel_info['members']) \
            .replace('{{channel_date}}', channel_info['date']) \
            .replace('{{channel_description}}', website_description.replace('\n', '</br>')) \
            .replace('{{channel_avatar}}', self.config.channel_photo_name)

        head = self.template_head \
            .replace('{{url}}', self.config.website_name) \
            .replace('{{channel_name}}', self.config.channel_name) \
            .replace('{{channel_title}}', website_title) \
            .replace('{{channel_description_clean}}', website_description.replace('\n', ' ')) \
            .replace('{{channel_avatar}}', self.config.channel_photo_name)

        post = ''
        for p in reversed(sorted(self.db.all(), key=lambda k: k['id'])):
            post = post + self.template_post \
                .replace('{{channel_name}}', self.config.channel_name) \
                .replace('{{channel_title}}', channel_info['title']) \
                .replace('{{post_date}}', p.get('date')) \
                .replace('{{post_text}}', p.get('text').replace('\n', '</br>')) + '\n'

        html = self.template_html \
            .replace('{{head}}', head) \
            .replace('{{header}}', header) \
            .replace('{{posts}}', post)

        with open('index.html', 'w') as f:
            f.write(html)
            f.flush()

    def _save_to_db(self, id, date, text):
        self.db.upsert({
            'id': id,
            'date': date,
            'text': text,
        }, where('id') == id)

    async def _get_channel_info(self, client):
        channel = await client.get_entity(self.config.channel_name)
        await client.download_profile_photo(self.config.channel_name,
                                            file=self.config.channel_photo_name)
        result = await client(functions.channels.GetFullChannelRequest(
            channel=self.config.channel_name
        ))
        return {
            'about': result.full_chat.about,
            'members': str(result.full_chat.participants_count),
            'title': channel.title,
            'date': channel.date.strftime("%Y")
        }

    def _read_template(self, template_path: str) -> str:
        with open(template_path, 'r') as template_file:
            return template_file.read()


bot = Bot(Config.load_from_env())


@click.group(help='Telegram channel bot to create link blog')
def cli():
    pass


@cli.command(help='Rebuilds the whole blog from the first message')
def build_from_scratch():
    bot.clean_and_rebuild_blog()


@cli.command(help='Starts to listen to messages on the channel')
def listen_events():
    if os.getenv('BLOG_EXPOSE_WAY', 'file') == 'http':
        print('start server')

        class Handler(BaseHTTPRequestHandler):

            def do_GET(self):
                self.send_response(200)
                self.end_headers()

                print(self.path)
                if self.path == '/' + bot.config.channel_photo_name:
                    with open(bot.config.channel_photo_name, 'rb') as index:
                        self.wfile.write(index.read())
                else:
                    with open('index.html', 'r') as index:
                        self.wfile.write(index.read().encode('UTF-8'))

        http_server = HTTPServer(('', os.getenv('HTTP_SERVER_PORT', 8080)), Handler)
        thread = threading.Thread(target=http_server.serve_forever)
        thread.start()
    bot.listen_for_channel_events()


if __name__ == '__main__':
    cli()
