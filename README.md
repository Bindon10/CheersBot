# Cheers Bot - A Homies House Discord Bot

Welcome to **Cheers Bot**, a custom bot for the **Homies House** Discord server! This bot plays sounds in voice channels, manages Easter Eggs, and logs its actions to a designated channel.

## Features

- **Play Sounds:** The bot joins voice channels and plays a sound at specific times (like every hour at :15). It can also be triggered to join and play on demand.
- **Easter Eggs:** Special events (Easter Eggs) that can trigger specific sounds based on time zones and join times.
- **Logging:** The bot logs all its actions (joining, playing a sound, leaving) in a specified log channel with a custom embed.
- **Modes:** Three sound-playing modes are available:
  - **Single:** Plays a single sound.
  - **Randomize:** Plays a random sound from the sound folder.
  - **Percent:** Plays sounds based on configured percentage chances.
- **Slash Commands:** Multiple slash commands are available for controlling the bot.

## Setup

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/cheers-bot.git
cd cheers-bot
```

2. Create a .env file:

In the root directory, create a .env file to store your bot's token.
```bash
DISCORD_BOT_TOKEN=your_discord_bot_token_here
```

3. Install the required dependencies:

Make sure you have Python 3.8+ installed. Install the dependencies listed in the requirements.txt file:

```bash
pip install -r requirements.txt
```
## Config File:

A config.json file will be automatically generated if it doesn't exist, but you can create or edit it to manage sounds and logging. Example config:

```json
{
    "sounds": {
        "SoundName1": 100,
        "SoundName2": 0.001
    },
    "default_sound": "SoundName1",
    "mode": "randomize",
    "log_channel_id": "123456789012345678",
    "log_settings": {
        "embed_title": "HH Cheers Bot Log",
        "footer_text": "EST. 1/1/2024",
        "thumbnail_url": "https://i.imgur.com/SKICBLv.png",
        "footer_icon_url": "https://i.imgur.com/SKICBLv.png"
    }
}
```
Run the bot:

After configuring the bot, run it:

```bash
python cheersbot.py
```
Available Slash Commands<br/><br/>
**/join** [channel]: Joins the specified voice channel without playing any sound. <br/>
**/leave:** Makes the bot leave the current voice channel.<br/>
**/cheers** [channel]: Joins a voice channel, plays the current sound, and leaves.<br/>
**/mode** [single/randomize/percent]: Shows or changes the bot's sound-playing mode.<br/>
**/sounds:** Lists all available sounds in the sound folder.<br/>
**/testsound** [sound] [channel]: Plays a specific sound in a voice channel for testing purposes.<br/>
**/easteregg:** Lists all available Easter Eggs and allows enabling/disabling them.<br/>
**/add_easter_egg** [name] [sound] [join_time] [play_delay] [timezone]: Adds a new Easter Egg.<br/>
**/delete_easter_egg** [name]: Deletes an existing Easter Egg.<br/>
**/reload:** Reloads the bot's configuration and syncs slash commands.<br/>
**/setlog** [channel]: Sets the log channel for the bot's actions.<br/>

## Easter Eggs
Easter Eggs are special events that trigger sounds based on pre-configured times and time zones. You can manage Easter Eggs using the 
```
/easteregg
/add_easter_egg
/delete_easter_egg
```
commands.

## Logging
All bot actions (such as joining and leaving channels, playing sounds, triggering Easter Eggs) are logged in a specific Discord channel. The log message is customizable via the config.json file, which allows you to set the embed title, footer text, thumbnail, and footer icon.

## Contribution
Feel free to open issues or submit pull requests to improve this bot!
