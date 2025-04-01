import configparser
import speech_recognition as sr
from twitchio.ext import commands
import threading
import asyncio
import os
import sys

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu(config):
    clear_screen()
    print("═"*50)
    print(f" CURRENT CONFIGURATION ".center(50, '═'))
    print("═"*50)
    print(f"1. Twitch Channel: {config['Twitch']['channel']}")
    print(f"2. OAuth Token: {'*'*20 if config['Twitch']['token'] else 'NOT CONFIGURED'}")
    print(f"3. Command Prefix: {config['Twitch']['prefix']}")
    print(f"4. Alert Message: {config['Messages']['alert']}")
    print("5. Start Bot")
    print("6. Exit")
    print("═"*50)

def edit_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    
    while True:
        show_menu(config)
        choice = input("Select an option (1-6): ")
        
        if choice == '1':
            config['Twitch']['channel'] = input("Channel name (without #): ").strip()
        elif choice == '2':
            token = input("OAuth Token (oauth:...): ").strip()
            if not token.startswith('oauth:'):
                token = 'oauth:' + token
            config['Twitch']['token'] = token
        elif choice == '3':
            config['Twitch']['prefix'] = input("Command prefix (e.g. !): ").strip()
        elif choice == '4':
            config['Messages']['alert'] = input("Alert message (use {count} and {total}): ").strip()
        elif choice == '5':
            return True  # Start bot
        elif choice == '6':
            with open(config_path, 'w') as f:
                config.write(f)
            return False  # Exit
        else:
            input("Invalid option. Press Enter to continue...")

class FuckCounterBot(commands.Bot):
    def __init__(self, config):
        self.config = config
        super().__init__(
            token=config['Twitch']['token'],
            prefix=config['Twitch']['prefix'],
            initial_channels=[config['Twitch']['channel']]
        )
        self.fuck_counter = 0
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()

    async def event_ready(self):
        print(f"\nBot connected to Twitch channel: {self.config['Twitch']['channel']}")
        print("Listening to microphone... (Press Ctrl+C to stop)")
        threading.Thread(target=self.listen_loop, daemon=True).start()

    def listen_loop(self):
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while True:
                try:
                    audio = self.recognizer.listen(source, timeout=5)
                    self.process_audio(audio)
                except Exception as e:
                    continue

    def process_audio(self, audio):
        try:
            text = self.recognizer.recognize_google(audio, language='en-US').lower()
            count = text.count('fuck')
            if count > 0:
                self.fuck_counter += count
                asyncio.run_coroutine_threadsafe(
                    self.send_alert(count),
                    self.loop
                )
                print(f"Detection! +{count} (Total: {self.fuck_counter})")
        except:
            pass

    async def send_alert(self, count):
        channel = self.get_channel(self.config['Twitch']['channel'])
        message = self.config['Messages']['alert'].format(
            count=count,
            total=self.fuck_counter
        )
        await channel.send(message)

    @commands.command()
    async def fuckcount(self, ctx):
        await ctx.send(f"Current counter: {self.fuck_counter}")

def main():
    # Initial configuration
    config = configparser.ConfigParser()
    config['Twitch'] = {
        'token': '',
        'channel': '',
        'prefix': '!'
    }
    config['Messages'] = {
        'alert': 'Fuck detected ({count}x)! Total: {total}'
    }
    
    if not os.path.exists('config.ini'):
        with open('config.ini', 'w') as f:
            config.write(f)
    
    config.read('config.ini')
    
    if not config['Twitch']['token'] or not config['Twitch']['channel']:
        print("Initial configuration required")
        if not edit_config('config.ini'):
            return
    
    try:
        bot = FuckCounterBot(config)
        bot.run()
    except KeyboardInterrupt:
        print("\nBot stopped")
    except Exception as e:
        print(f"Error: {str(e)}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()