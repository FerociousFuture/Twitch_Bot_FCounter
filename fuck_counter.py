import configparser
import speech_recognition as sr
from twitchio.ext import commands
import threading
import asyncio
import os

class FuckCounterBot(commands.Bot):
    def __init__(self, config):
        self.config = config
        super().__init__(
            token=config['Twitch']['token'],
            prefix=config['Twitch']['prefix'],
            initial_channels=[config['Twitch']['channel']]
        )
        self.counter = 0

    async def event_ready(self):
        print(f"Bot connected to {self.config['Twitch']['channel']}")
        threading.Thread(target=self.listen_mic, daemon=True).start()

    def listen_mic(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            while True:
                try:
                    audio = r.listen(source, timeout=5)
                    text = r.recognize_google(audio, language='en-US').lower()
                    if 'fuck' in text:
                        self.counter += 1
                        asyncio.run_coroutine_threadsafe(
                            self.send_alert(),
                            self.loop
                        )
                except:
                    continue

    async def send_alert(self):
        channel = self.get_channel(self.config['Twitch']['channel'])
        await channel.send(
            self.config['Messages']['alert'].format(total=self.counter)
        )

    @commands.command()
    async def fuckcount(self, ctx):
        await ctx.send(f"Current count: {self.counter}")

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
    bot = FuckCounterBot(config)
    bot.run()