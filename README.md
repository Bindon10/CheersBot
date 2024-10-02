# Cheers Bot - A Homies House Discord Bot

Cheers Bot is a custom Discord bot originally designed for Homies House, featuring sound playback, automatic voice channel joining, Easter eggs, and a logging system for bot actions.

## Features

- **Play Sounds:** The bot joins voice channels and plays a sound at specific times (like every hour at :15). It can also be triggered to join and play on demand.
- **Easter Eggs:** Trigger hidden sound effects at specific times based on user-defined time zones.
- **Modes**: Choose between single sound, randomize, or percent-based sound playback modes.
- **Automatic Channel Join**: The bot automatically joins the most populated voice channel every x:15 minute of every hour, waits 5 minutes, then plays a sound.
- **Logging**: Log the bot's actions in a specific channel, including when it joins, plays a sound, and leaves a voice channel.
- **Slash Commands**: Simple-to-use slash commands for controlling bot behavior.
- **Permissions**: Role-based access control for general staff and bot admin commands.

## Requirements

1. **FFmpeg**: 
   - You need to add the `ffmpeg` binaries to the `FFMPEG` folder inside the bot's directory.
   - For **Windows**, download `ffmpeg.exe` and place it in the `FFMPEG` folder.
   - For **Linux**, download or install `ffmpeg` (without the `.exe` extension) and place it in the `FFMPEG` folder.
   - The bot automatically detects the operating system and sets the correct path for `ffmpeg`.

2. **Python 3.8+**: Required for running the bot.
   - 

## Setup
1a. **Windows: Download the files as a .Zip**
   - Although you can download the files as a .Zip within the big green code button, I'll also link it [here](https://github.com/Wubbity/CheersBot/archive/refs/heads/main.zip).

1b. **Linux: Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/cheers-bot.git
   cd cheers-bot
   ```

2. **Install FFmpeg:**

   - **Windows:**
     - Download `ffmpeg.exe` from [here](https://ffmpeg.org/download.html).
     - Place `ffmpeg.exe` in a folder named `FFMPEG` folder inside the bot directory.
       - Example: `/CheersBot/FFMPEG/ffmpeg.exe`

   - **Linux:**
     - Install `ffmpeg` via your package manager.
     - if installed correctly, you won't need to move the binary (The default is /usr/bin/)
     - To use the system installed version of FFMPEG, you will need to follow the instructions in the cheersbot.py file

   - **Linux Manual:**
     - If you manually downloaded FFMPEG you won't need to change the cheersbot.py file
      - Create a folder named FFMPEG (Case Sensitive)
      - Ensure the `ffmpeg` binary is in the `FFMPEG` folder inside the bot directory.
      - Example: `/CheersBot/FFMPEG/ffmpeg`


4. **Create a `.env` file:**

   In the root directory, create a `.env` file to store your bot's token.

   ```bash
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   ```

5. **Install the required dependencies:**

   Make sure you have Python 3.8+ installed.

   Install the dependencies listed in the `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

7. **Run the bot:**

   After configuring the bot, run it:

   ```bash
   python cheersbot.py
   ```

## Slash Commands

Here’s a list of all available slash commands:

### General Commands

- **/join <channel>**: Joins the specified voice channel without playing any sound.
- **/leave**: Makes the bot leave the current voice channel.
- **/cheers <channel>**: Joins a specified voice channel, plays the current sound, and leaves the channel.
- **/sounds**: Lists all available sounds in the sound folder.
- **/testsound <sound_name> <channel>**: Plays the specified sound in the chosen voice channel. You can specify whether the bot should leave after playing the sound.

### Mode Commands

- **/mode [single/randomize/percent] [sound_name]**: Changes the sound mode.
  - `single`: Plays a single sound file.
  - `randomize`: Plays a random sound from the sound folder.
  - `percent`: Plays sounds based on percentage values in the config.

### Easter Egg Commands

- **/easteregg [name] [enable/disable]**: List, enable, or disable Easter Eggs.
- **/add_easter_egg <name> <sound> <join_time> <play_delay> <timezone>**: Add a new Easter Egg with specific details.
- **/delete_easter_egg <name>**: Deletes the specified Easter Egg.

### Admin Commands

- **/reload**: Reloads the bot’s configuration and syncs slash commands.
- **/setlog <channel>**: Set the log channel for bot actions.

## Configuration

The bot uses a `config.json` file to store settings, such as the list of available sounds, the current mode, and logging settings. You can edit the `config.json` manually or update the settings through slash commands.

Example `config.json`:

```json
{
    "sounds": {
        "Cheers_Bitch": 100,
        "Cheers by King": 0.001,
        "FWYTB": 0.001,
        "Its 420 Somewhere - Smoke up": 0.001,
        "Mount-Cheers": 0.001
    },
    "default_sound": "Cheers_Bitch",
    "mode": "randomize",
    "log_channel_id": 000000000000000000,
    "log_settings": {
        "embed_title": "HH Cheers Bot Log",
        "footer_text": "EST. 1/1/2024",
        "thumbnail_url": "https://i.imgur.com/SKICBLv.png",
        "footer_icon_url": "https://i.imgur.com/SKICBLv.png"
    }
}
```

## Easter Egg Structure

Easter eggs are sound triggers that happen at specific times and can be set with different time zones and play delays.

- **Name**: The unique name of the Easter egg.
- **Sound**: The sound file associated with the Easter egg.
- **Join Time**: The time (in AM/PM format) when the bot should join a channel.
- **Play Delay**: Delay (in minutes) before playing the sound.
- **Timezone**: The timezone for the Easter egg trigger.

Example Easter egg entry in `easter_eggs.json`:

```json
[
    {
        "name": "420 Celebration",
        "sound": "Its 420!!!",
        "join_time": "4:15 PM",
        "play_delay": 5,
        "timezone": "America/New_York",
        "enabled": true,
        "last_triggered": null
    }
]
```

## Logging

The bot logs its actions (joining, playing sounds, leaving) in a specified log channel. You can configure this via the `/setlog` command or manually in `config.json`.

The log embed includes:

- Joined and left times
- Mode of the bot
- Sound played
- Easter egg trigger (if applicable)

## Credits
- Wubbity (Main Bot Code)
- Bindon (General and Logic Fixes)
- KitCtrl (Original Idea for CheersBot)
