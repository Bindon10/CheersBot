'''
   ____ _                        ____        _           _   ___  
  / ___| |__   ___  ___ _ __ ___| __ )  ___ | |_  __   _/ | / _ \ 
 | |   | '_ \ / _ \/ _ \ '__/ __|  _ \ / _ \| __| \ \ / / || | | |
 | |___| | | |  __/  __/ |  \__ \ |_) | (_) | |_   \ V /| || |_| |
  \____|_| |_|\___|\___|_|  |___/____/ \___/ \__|   \_/ |_(_)___/ 
                                                                
  ____         __        __     _     _     _ _         
 | __ ) _   _  \ \      / /   _| |__ | |__ (_) |_ _   _ 
 |  _ \| | | |  \ \ /\ / / | | | '_ \| '_ \| | __| | | |
 | |_) | |_| |   \ V  V /| |_| | |_) | |_) | | |_| |_| |
 |____/ \__, |    \_/\_/  \__,_|_.__/|_.__/|_|\__|\__, |
        |___/                                     |___/ 

##############################################################################################################
#   For Configuration:                                                                                       #
#       - Channel Logging ID and RoleIDs are now Handled in the config.json                                  #
#                                                                                                            #
#                                                                                                            #
#   For FFMPEG:                                                                                              #
#       - Normally on Linux FFMPEG will install in /usr/bin/, if in your setup you have manually             #
#         downloaded the binary you won't have to do anything, if you want to use your systems version of    #
#         FFMPEG; uncomment lines 61-62 and comment lines 63-64                                              #
#                                                                                                            #
#                                                                                                            #
##############################################################################################################
'''

import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta
import os
import random
import pytz
import json
from discord import app_commands
from discord.app_commands import CheckFailure
from dotenv import load_dotenv
import subprocess
from discord.ui import Button, View
import platform

intents = discord.Intents.default()
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

#####################################################################################################################################
# Use the os module to dynamically get the current working directory and join it with the sound folder path                         #
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current file                                      #
SOUND_FOLDER = os.path.join(BASE_DIR, "cheers_sounds")  # Join the base directory with the sound folder                             #
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")  # Path to config.json                                                          #
                                                                                                                                    #
# Detect the current operating system                                                                                               #
current_os = platform.system()                                                                                                      #
                                                                                                                                    #
# Update ffmpeg path for Windows and Linux dynamically based on the detected OS                                                     #
if current_os == "Windows":                                                                                                         #
    ffmpeg_path = os.path.join(BASE_DIR, "FFMPEG", "ffmpeg.exe")  # Windows executable                                              #
#elif current_os == "Linux":                                                                                                         #
#   ffmpeg_path = os.path.join("/usr/bin/", "ffmpeg")  # Linux executable, by Default this is usually in /usr/bin                    #
elif current_os == "Linux":                                                                                                         #
    ffmpeg_path = os.path.join(BASE_DIR, "FFMPEG", "ffmpeg")  # Linux; Comment the previous value for an "in folder" install        #
else:                                                                                                                               #
    raise OSError(f"Unsupported operating system: {current_os}")                                                                    #
                                                                                                                                    #
print(f"Sound folder path: {SOUND_FOLDER}")                                                                                         #
print(f"FFmpeg path: {ffmpeg_path}")                                                                                                #
#####################################################################################################################################

# Get available sound files in the sound folder
def get_available_sounds():
    return [f[:-4] for f in os.listdir(SOUND_FOLDER) if f.endswith('.mp3')]

# Save the config to the file, sorting sounds by percentage (highest first)
def save_config(config):
    # Sort the sounds by percentage in descending order (highest first)
    config["sounds"] = dict(sorted(config["sounds"].items(), key=lambda item: item[1], reverse=True))

    # Write the sorted config to the file
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# Update config to match the sounds in the sound folder and manage sound_status
def update_config_sounds(config):
    available_sounds = get_available_sounds()

    # Add missing sounds to config (with default percentage and enabled status)
    for sound in available_sounds:
        if sound not in config["sounds"]:
            config["sounds"][sound] = 0.001  # Default percentage for new sounds
        if "sound_status" not in config:
            config["sound_status"] = {}  # Ensure sound_status exists
        if sound not in config["sound_status"]:
            config["sound_status"][sound] = True  # Default status for new sounds is enabled

    # Remove sounds from config that no longer exist in the folder
    for sound in list(config["sounds"].keys()):
        if sound not in available_sounds:
            del config["sounds"][sound]
            if sound in config["sound_status"]:
                del config["sound_status"][sound]

    if config["default_sound"] not in available_sounds:
        config["default_sound"] = random.choice(available_sounds)
        config["sounds"][config["default_sound"]] = 100

    save_config(config)

# Load or create the config file for sounds and mode
def load_or_create_config():
    if not os.path.exists(CONFIG_FILE):
        config = {
            "sounds": {},
            "default_sound": None,
            "mode": "single",
            "log_settings": {
                "embed_title": "HH Cheers Bot Log",
                "footer_text": "EST. 1/1/2024",
                "thumbnail_url": "https://i.imgur.com/SKICBLv.png",
                "footer_icon_url": "https://i.imgur.com/SKICBLv.png"
            }
        }
        sounds_in_folder = get_available_sounds()
        if sounds_in_folder:
            default_sound = random.choice(sounds_in_folder)
            config["default_sound"] = default_sound
            for sound in sounds_in_folder:
                config["sounds"][sound] = 0.001 if sound != default_sound else 100
        save_config(config)
    else:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        # Ensure new log settings exist
        if "log_settings" not in config:
            config["log_settings"] = {
                "embed_title": "HH Cheers Bot Log",
                "footer_text": "EST. 1/1/2024",
                "thumbnail_url": "https://i.imgur.com/SKICBLv.png",
                "footer_icon_url": "https://i.imgur.com/SKICBLv.png"
            }
        update_config_sounds(config)

    return config

# Pull the values from the config.json file
config = load_or_create_config()
STARTUP_CHANNEL_ID = config["startup_and_roles"].get("startup_channel_id")
ROLE_NEEDED_FOR_GENERAL_COMMAND = config["startup_and_roles"].get("role_needed_for_general_command")
ROLE_NEEDED_FOR_RELOAD_COMMAND = config["startup_and_roles"].get("role_needed_for_reload_command")

# Default sound from config
DEFAULT_SOUND_FILE = os.path.join(SOUND_FOLDER, f"{config.get('default_sound_file', 'cheers_bitch')}.mp3")
selected_sound = DEFAULT_SOUND_FILE

# Easter Egg List
easter_eggs = []

# Path to the Easter Egg JSON file
EASTER_EGG_FILE = "easter_eggs.json"



# Backup old config and create a new one
def backup_and_create_new_config(config):
    os.rename(CONFIG_FILE, CONFIG_FILE + ".backup")
    save_config(config)



'''
  _____          _              _____                  _                   _                    
 | ____|__ _ ___| |_ ___ _ __  | ____|__ _  __ _   ___| |_ _ __ _   _  ___| |_ _   _ _ __ ___ _ 
 |  _| / _` / __| __/ _ \ '__| |  _| / _` |/ _` | / __| __| '__| | | |/ __| __| | | | '__/ _ (_)
 | |__| (_| \__ \ ||  __/ |    | |__| (_| | (_| | \__ \ |_| |  | |_| | (__| |_| |_| | | |  __/_ 
 |_____\__,_|___/\__\___|_|    |_____\__, |\__, | |___/\__|_|   \__,_|\___|\__|\__,_|_|  \___(_)
                                     |___/ |___/                                                
'''
class EasterEgg:
    def __init__(self, name, sound, join_time, play_delay, timezone, enabled=True, last_triggered=None):
        self.name = name
        self.sound = sound
        self.join_time = join_time
        self.play_delay = play_delay
        self.timezone = timezone
        self.enabled = enabled
        self.last_triggered = last_triggered  # Keep it None if it hasn't been triggered

    def get_converted_time(self):
        tz_name = self.timezone
        abbreviation_mapping = build_timezone_mapping()

        # Map abbreviation to full timezone name if necessary
        if tz_name in abbreviation_mapping:
            tz_name = abbreviation_mapping[tz_name]

        try:
            tz = pytz.timezone(tz_name)
            join_time = datetime.strptime(self.join_time, "%I:%M %p")  # Parse join_time as naive
            now = datetime.now(tz)
            # Combine today's date with the provided time
            join_time = join_time.replace(year=now.year, month=now.month, day=now.day)
            join_time_aware = tz.localize(join_time)
            return join_time_aware.astimezone(pytz.utc)  # Return join time in UTC
        except pytz.UnknownTimeZoneError:
            print(f"Error: Invalid timezone '{self.timezone}'")
            return None

    def can_trigger(self):
        """Checks if the Easter Egg can be triggered based on last trigger and current time."""
        now_utc = datetime.now(pytz.utc)  # Get current time in UTC
        join_time_utc = self.get_converted_time()  # Convert join_time to UTC

        if join_time_utc is None:
            print(f"Error: Cannot check trigger for Easter Egg '{self.name}' due to invalid timezone.")
            return False

    # If never triggered, check if the current UTC time has passed the join_time
        if self.last_triggered is None:
            if now_utc >= join_time_utc:
                self.mark_triggered()  # Mark it as triggered
                return True

        # Check if it hasn't been triggered today and the join_time has passed
        last_triggered_date = self.last_triggered.date() if self.last_triggered else None
        now_date = now_utc.date()

        if last_triggered_date is None:  # Handle case when last_triggered is None
            return False

        if now_date != last_triggered_date:
            if now_utc >= join_time_utc:
                self.mark_triggered()  # Update last_triggered to now
                return True

    def mark_triggered(self):
        """Marks the Easter Egg as triggered by setting the current UTC time."""
        self.last_triggered = datetime.now(pytz.utc)

# Save Easter Eggs to JSON
def save_easter_eggs():
    with open(EASTER_EGG_FILE, 'w') as f:
        # Convert datetime objects to ISO format strings for serialization
        data = [
            {
                **egg.__dict__,
                "last_triggered": egg.last_triggered.isoformat() if egg.last_triggered else None
            }
            for egg in easter_eggs
        ]
        json.dump(data, f, indent=4)

'''
  _____ _                _____                  _                _        
 |_   _(_)_ __ ___   ___|__  /___  _ __   ___  | |    ___   __ _(_) ___ _ 
   | | | | '_ ` _ \ / _ \ / // _ \| '_ \ / _ \ | |   / _ \ / _` | |/ __(_)
   | | | | | | | | |  __// /| (_) | | | |  __/ | |__| (_) | (_| | | (__ _ 
   |_| |_|_| |_| |_|\___/____\___/|_| |_|\___| |_____\___/ \__, |_|\___(_)
                                                           |___/          
'''
def build_timezone_mapping():
    try:
        timezones = pytz.all_timezones
        abbreviation_to_timezone = {}
        for timezone in timezones:
            tz = pytz.timezone(timezone)
            for time_info in [datetime.now(), datetime.now() - timedelta(days=180)]:
                try:
                    abbreviation = tz.tzname(time_info)
                    if abbreviation and abbreviation not in abbreviation_to_timezone:
                        abbreviation_to_timezone[abbreviation] = timezone
                except:
                    continue
        
        # Your known timezone abbreviations
        abbreviation_to_timezone.update({
            "ACST": "Australia/Adelaide",  # Australian Central Standard Time
            "EST": "America/New_York",     # Eastern Standard Time (US)
            "PST": "America/Los_Angeles",  # Pacific Standard Time (US)
            "GMT": "Europe/London",        # Greenwich Mean Time
            "CST": "America/Chicago",      # Central Standard Time (US)
            "MST": "America/Denver",       # Mountain Standard Time (US)
            "AEST": "Australia/Sydney",    # Australian Eastern Standard Time
            "BST": "Europe/London",        # British Summer Time (maps to GMT as they share DST rules)
            "AWST": "Australia/Perth",     # Australian Western Standard Time
            "JST": "Asia/Tokyo",           # Japan Standard Time
            "UTC": "UTC"                   # Coordinated Universal Time
        })

        return abbreviation_to_timezone
    
    except Exception as e:
        print(f"Error fetching timezones: {e}")
        return {}

# Global variable to enable/disable auto-join
auto_join_enabled = True

# Auto-join task that runs every second
@tasks.loop(seconds=5)
async def auto_join_task():
    global auto_join_enabled

    # Auto-join task logic for every x:15
    if auto_join_enabled:
        now = datetime.now(pytz.utc)
        if now.minute == 15 and now.second == 0:
            for guild in bot.guilds:
                voice_channel = get_most_populated_voice_channel(guild)
                if voice_channel:
                    try:
                        join_time = datetime.now()  # Capture join time
                        vc = await voice_channel.connect(reconnect=True)
                        print(f"Automatically joined {voice_channel.name}")
                        # Add a small delay before playing the sound to ensure the connection stabilizes
                        await asyncio.sleep(2)  # Wait for 2 seconds before proceeding

                        next_time = (now + timedelta(minutes=5)).replace(second=0, microsecond=0)
                        sleep_duration = (next_time - now).total_seconds()
                        await asyncio.sleep(sleep_duration)
                        sound_to_play = choose_sound()

                        # Define the after function to disconnect after the sound is done
                        def after_playing(error):
                            coro = vc.disconnect()
                            fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
                            try:
                                fut.result()  # Ensure any exceptions are handled
                            except Exception as e:
                                print(f"Error disconnecting: {e}")

                        vc.play(
                            discord.FFmpegOpusAudio(sound_to_play, executable=ffmpeg_path),
                            after=after_playing  # Pass the after function
                        )

                        leave_time = datetime.now()  # Capture leave time

                        # Log the action after the bot leaves the voice channel
                        await log_action(
                            voice_channel=voice_channel,
                            sound_name=os.path.basename(sound_to_play),
                            is_easter_egg=False,
                            mode=load_or_create_config()["mode"],
                            join_time=join_time,
                            leave_time=leave_time
                        )
                    except Exception as e:
                        print(f"Error occurred during auto join/play: {e}")

# New task to check for Easter Egg triggers independently
@tasks.loop(seconds=5)
async def easter_egg_task():
    try:
        now = datetime.now(pytz.utc)

        # Easter Egg triggers
        for easter_egg in easter_eggs:
            if easter_egg.enabled and easter_egg.can_trigger():
                join_time_utc = easter_egg.get_converted_time()
                if join_time_utc and now.strftime("%H:%M") == join_time_utc.strftime("%H:%M"):
                    for guild in bot.guilds:
                        voice_channel = get_most_populated_voice_channel(guild)
                        if voice_channel:
                            print(f"Triggering Easter Egg '{easter_egg.name}' in {voice_channel.name}")
                            await handle_easter_egg_trigger(easter_egg, voice_channel, guild)
                            easter_egg.mark_triggered()
                            save_easter_eggs()
    except Exception as e:
        print(f"Error in easter_egg_task: {e}")

# Handle Easter Egg Trigger
async def handle_easter_egg_trigger(easter_egg, voice_channel, guild):
    try:
        join_time = datetime.now()  # Capture join time when the bot joins

        # Check if already connected to a voice channel
        if guild.voice_client is None:
            print(f"Bot is not connected. Joining {voice_channel.name}...")
            vc = await voice_channel.connect()
            print(f"Joined {voice_channel.name}.")
        else:
            vc = guild.voice_client
            print(f"Bot is already connected to {vc.channel.name}.")

        # Apply delay if configured
        if easter_egg.play_delay > 0:
            print(f"Delaying sound for {easter_egg.play_delay} minutes...")
            await asyncio.sleep(easter_egg.play_delay * 60)

        sound_to_play = os.path.join(SOUND_FOLDER, f"{easter_egg.sound}.mp3")
        print(f"Playing sound: {sound_to_play}")

        # Function to disconnect after sound is done
        async def after_playing(vc):
            if vc.is_connected():
                await vc.disconnect()

        # Start playing the sound
        vc.play(
            discord.FFmpegPCMAudio(sound_to_play, executable=ffmpeg_path),
            after=lambda e: asyncio.create_task(after_playing(vc))
        )
        # Capture the leave time after playing
        leave_time = datetime.now()

    except Exception as e:
        print(f"Error in handle_easter_egg_trigger: {e}")
        leave_time = datetime.now()  # Ensure leave_time is initialized even on error

        # Log the Easter egg action after the bot leaves the voice channel
        await log_action(
            voice_channel=voice_channel,
            sound_name=easter_egg.sound,  # Use the Easter egg's sound name
            is_easter_egg=True,  # Indicate that it was an Easter egg
            mode=load_or_create_config()["mode"],  # Pass the current mode
            join_time=join_time,
            leave_time=leave_time,
            easter_egg_details={"name": easter_egg.name, "timezone": easter_egg.timezone},  # Optional details
            user=None  # Since this is automated, no user involved
        )
    except Exception as e:
        print(f"Error occurred during Easter Egg activation: {e}")

# Global variables to store Easter eggs and last modified timestamp
easter_eggs = []
last_modified_time = None

# Function to load Easter Eggs from a JSON file
def load_easter_eggs():
    global easter_eggs, last_modified_time

    # Check if file exists
    if not os.path.exists(EASTER_EGG_FILE):
        print(f"File {EASTER_EGG_FILE} does not exist. Initializing an empty list.")
        easter_eggs = []
        return

    try:
        # Get the last modified time of the file
        current_modified_time = os.path.getmtime(EASTER_EGG_FILE)

        # Only reload if the file has changed since the last check
        if last_modified_time is None or current_modified_time > last_modified_time:
            with open(EASTER_EGG_FILE, 'r') as f:
                easter_eggs_data = json.load(f)
                easter_eggs = []

                for egg_data in easter_eggs_data:
                    last_triggered = egg_data.get('last_triggered')
                    if isinstance(last_triggered, str):
                        try:
                            egg_data['last_triggered'] = datetime.fromisoformat(last_triggered)
                        except ValueError:
                            print(f"Error: Invalid date format for Easter egg {egg_data.get('name')}, setting 'last_triggered' to None.")
                            egg_data['last_triggered'] = None

                    try:
                        easter_eggs.append(EasterEgg(**egg_data))
                    except TypeError as e:
                        print(f"Error: Missing or invalid fields for Easter egg: {e}. Skipping entry.")

            # Update the last modified time
            last_modified_time = current_modified_time
            print(f"Reloaded {len(easter_eggs)} Easter Eggs from file.")

        else:
            print(f"No changes detected in {EASTER_EGG_FILE}, skipping reload.")

    except json.JSONDecodeError:
        print(f"Error: {EASTER_EGG_FILE} contains invalid JSON. Initializing an empty list.")
        easter_eggs = []
    except Exception as e:
        print(f"Unexpected error while loading Easter eggs: {e}")

# Function to check and reload the Easter Egg list if the file has changed
def check_and_reload_easter_eggs():
    load_easter_eggs()  # Simply call the load function to handle checking and reloading

# Function to get the most populated voice channel
def get_most_populated_voice_channel(guild: discord.Guild):
    voice_channels = [vc for vc in guild.voice_channels if len(vc.members) > 0]
    return max(voice_channels, key=lambda vc: len(vc.members)) if voice_channels else None

# Choose the sound based on the mode
def choose_sound():
    config = load_or_create_config()
    if config["mode"] == "randomize":
        return os.path.join(SOUND_FOLDER, random.choice(get_available_sounds()) + ".mp3")
    elif config["mode"] == "percent":
        return weighted_random_choice(config["sounds"])
    else:
        return os.path.join(SOUND_FOLDER, config["default_sound"] + ".mp3")

# Weighted random choice based on percentage values
def weighted_random_choice(sounds):
    total_weight = sum(sounds.values())
    random_num = random.uniform(0, total_weight)
    current_sum = 0
    for sound, weight in sounds.items():
        current_sum += weight
        if random_num <= current_sum:
            return os.path.join(SOUND_FOLDER, sound + ".mp3")

# Role restriction check functions
def has_general_role():
    async def predicate(interaction: discord.Interaction):
        role_ids = [role.id for role in interaction.user.roles]
        if ROLE_NEEDED_FOR_GENERAL_COMMAND in role_ids:
            return True
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return False
    return app_commands.check(predicate)

def has_reload_role():
    async def predicate(interaction: discord.Interaction):
        role_ids = [role.id for role in interaction.user.roles]
        if ROLE_NEEDED_FOR_RELOAD_COMMAND in role_ids:
            return True
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return False
    return app_commands.check(predicate)

'''
  ____  _           _        ____                                          _       
 / ___|| | __ _ ___| |__    / ___|___  _ __ ___  _ __ ___   __ _ _ __   __| |___ _ 
 \___ \| |/ _` / __| '_ \  | |   / _ \| '_ ` _ \| '_ ` _ \ / _` | '_ \ / _` / __(_)
  ___) | | (_| \__ \ | | | | |__| (_) | | | | | | | | | | | (_| | | | | (_| \__ \_ 
 |____/|_|\__,_|___/_| |_|  \____\___/|_| |_| |_|_| |_| |_|\__,_|_| |_|\__,_|___(_)
                                                                                   
'''
@bot.tree.command(name="mode", description="Show or change the sound mode (randomize/single/percent).")
@app_commands.describe(mode_type="The sound mode to choose: 'single', 'randomize', or 'percent'.")
@app_commands.describe(sound_name="Specify a sound if choosing single or percent mode.")
@has_general_role()
async def mode(interaction: discord.Interaction, mode_type: str = None, sound_name: str = None):
    config = load_or_create_config()

    if mode_type is None:
        # If no mode_type is provided, output the current mode
        current_mode = config.get("mode", "unknown")
        response = f"Current mode: `{current_mode}`"

        if current_mode == "single":
            current_sound = config.get("default_sound", "None")
            response += f"\nCurrent single mode sound: `{current_sound}`"
        elif current_mode == "randomize":
            response += "\nMode is set to randomize. The bot will randomly play sounds from the sound folder."
        elif current_mode == "percent":
            sound_list = "\n".join([f"{sound}: {percent}%" for sound, percent in config["sounds"].items()])
            response += f"\nPercent mode sounds:\n{sound_list}"

        await interaction.response.send_message(response)
        return

    available_sounds = get_available_sounds()
    available_sounds_lower = [s.lower() for s in available_sounds]

    if mode_type == "single":
        if sound_name:
            # Convert the provided sound name to lowercase for comparison
            sound_name_lower = sound_name.lower()
            
            if sound_name_lower not in available_sounds_lower:
                await interaction.response.send_message(
                    f"Invalid sound name. Available sounds: {', '.join(available_sounds)}",
                    ephemeral=True
                )
                return

            # Find the correct case for the sound name
            matched_sound = available_sounds[available_sounds_lower.index(sound_name_lower)]
            config["mode"] = "single"
            config["default_sound"] = matched_sound
            save_config(config)
            await interaction.response.send_message(f"Mode set to 'single' with default sound '{matched_sound}'.")
        else:
            # Set to single mode with a random sound from percent mode
            config["mode"] = "single"
            if not config.get("sounds"):
                backup_and_create_new_config(config)
            config["default_sound"] = random.choice([s for s, p in config["sounds"].items() if p == 100])
            save_config(config)
            await interaction.response.send_message(f"Mode set to 'single' with randomly chosen sound '{config['default_sound']}'.")
    
    elif mode_type == "randomize":
        # Set to randomize mode
        config["mode"] = "randomize"
        save_config(config)
        await interaction.response.send_message("Mode set to 'randomize'. The bot will play a random sound from the folder.")

    elif mode_type == "percent":
        if sound_name:
            sound_name_lower = sound_name.lower()

            if sound_name_lower not in available_sounds_lower:
                await interaction.response.send_message(
                    f"Invalid sound name. Available sounds: {', '.join(available_sounds)}",
                    ephemeral=True
                )
                return

            matched_sound = available_sounds[available_sounds_lower.index(sound_name_lower)]
            set_percent_mode(config, matched_sound)
            await interaction.response.send_message(f"Mode set to 'percent' with default sound '{matched_sound}'.")

        else:
            # Set to percent mode with a random sound if no sound_name provided
            if not config.get("sounds"):
                backup_and_create_new_config(config)
            random_sound = random.choice(available_sounds)
            set_percent_mode(config, random_sound)
            await interaction.response.send_message(f"Mode set to 'percent' with random default sound '{random_sound}'.")

    else:
        await interaction.response.send_message("Invalid mode. Choose between 'single', 'randomize', or 'percent'.", ephemeral=True)

# Function to set the config for percent mode
def set_percent_mode(config, sound_name):
    if sound_name not in get_available_sounds():
        raise ValueError(f"Invalid sound name. Available sounds: {', '.join(get_available_sounds())}")
    config["mode"] = "percent"
    config["sounds"] = {sound: (100 if sound == sound_name else 0.001) for sound in get_available_sounds()}
    config["default_sound"] = sound_name
    save_config(config)

# View for confirmation of overwriting percent config
class ConfirmOverwriteView(View):
    def __init__(self, sound_name, interaction):
        super().__init__()
        self.sound_name = sound_name
        self.interaction = interaction

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        config = load_or_create_config()
        set_percent_mode(config, self.sound_name)
        await self.interaction.followup.send(f"Percent mode overwritten with default sound '{self.sound_name}'.")

    @discord.ui.button(label="No", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await self.interaction.followup.send("Command canceled. The current percent configuration remains unchanged.", ephemeral=True)

# command to check the state of auto-join
@bot.tree.command(name="autojoin_status", description="Check the current state of auto-join.")
@has_general_role()
async def autojoin_status(interaction: discord.Interaction):
    # Check the state of auto_join_enabled
    status = "enabled" if auto_join_enabled else "disabled"
    await interaction.response.send_message(f"Auto-join is currently **{status}**.", ephemeral=True)

@bot.tree.command(name="sounds", description="List all available sounds or enable/disable a sound.")
@app_commands.describe(sound_name="The name of the sound to enable/disable.", action="Either 'enable' or 'disable'.")
@has_general_role()
async def sounds(interaction: discord.Interaction, sound_name: str = None, action: str = None):
    config = load_or_create_config()
    
    available_sounds = get_available_sounds()

    if sound_name and action:
        # Enable or disable the sound
        sound_name_lower = sound_name.lower()

        if sound_name_lower not in [s.lower() for s in available_sounds]:
            await interaction.response.send_message(f"Invalid sound name. Available sounds: {', '.join(available_sounds)}", ephemeral=True)
            return

        if action.lower() not in ["enable", "disable"]:
            await interaction.response.send_message("Invalid action. Use 'enable' or 'disable'.", ephemeral=True)
            return

        # Ensure that the config contains the enable/disable flag for each sound
        if "sound_status" not in config:
            config["sound_status"] = {sound: True for sound in available_sounds}

        # Update the enabled/disabled status for the sound
        config["sound_status"][sound_name] = (action.lower() == "enable")
        save_config(config)

        status = "enabled" if config["sound_status"][sound_name] else "disabled"
        await interaction.response.send_message(f"Sound '{sound_name}' is now {status}.", ephemeral=True)
        return

    # If no sound_name or action is provided, list all sounds and their status
    sound_status = config.get("sound_status", {sound: True for sound in available_sounds})

    if config["mode"] == "percent":
        # Show sounds with their percentages in percent mode
        sound_list = "\n".join([f"{sound} `{('Enabled' if sound_status.get(sound, True) else 'Disabled')}`: {percent}%" for sound, percent in config["sounds"].items()])
        await interaction.response.send_message(f"Available sounds and their percentages:\n{sound_list}")
    else:
        # Just list sounds in single or randomize mode, with their enabled/disabled status
        sound_list = "\n".join([f"{sound} `{('Enabled' if sound_status.get(sound, True) else 'Disabled')}`" for sound in available_sounds])
        await interaction.response.send_message(f"Available sounds:\n{sound_list}")

# Function to choose a sound for auto-join, excluding disabled sounds
def choose_sound():
    config = load_or_create_config()
    available_sounds = get_available_sounds()
    
    # Get the sound status (enabled/disabled)
    sound_status = config.get("sound_status", {sound: True for sound in available_sounds})
    
    # Filter sounds to only include enabled ones
    enabled_sounds = [sound for sound in available_sounds if sound_status.get(sound, True)]

    if config["mode"] == "randomize":
        return os.path.join(SOUND_FOLDER, random.choice(enabled_sounds) + ".mp3")
    elif config["mode"] == "percent":
        # Filter percent sounds to only include enabled ones
        enabled_percent_sounds = {sound: percent for sound, percent in config["sounds"].items() if sound in enabled_sounds}
        return weighted_random_choice(enabled_percent_sounds)
    else:
        return os.path.join(SOUND_FOLDER, config["default_sound"] + ".mp3")

# Function to handle Easter Egg triggers
async def handle_easter_egg_trigger(easter_egg, voice_channel, guild):
    try:
        join_time = datetime.now()  # Capture join time when the bot joins

        # Check if already connected to a voice channel
        if guild.voice_client is None:
            print(f"Bot is not connected. Joining {voice_channel.name}...")
            vc = await voice_channel.connect()
            print(f"Joined {voice_channel.name}.")
        else:
            vc = guild.voice_client
            print(f"Bot is already connected to {vc.channel.name}.")

        # Apply delay if configured
        if easter_egg.play_delay > 0:
            print(f"Delaying sound for {easter_egg.play_delay} minutes...")
            await asyncio.sleep(easter_egg.play_delay * 60)

        # Easter eggs ignore the enabled/disabled status of sounds
        sound_to_play = os.path.join(SOUND_FOLDER, f"{easter_egg.sound}.mp3")
        print(f"Playing sound: {sound_to_play}")

        # Function to disconnect after sound is done
        async def after_playing(vc):
            if vc.is_connected():
                await vc.disconnect()

        # Start playing the sound
        vc.play(
            discord.FFmpegPCMAudio(sound_to_play, executable=ffmpeg_path),
            after=lambda e: asyncio.create_task(after_playing(vc))
        )
        # Capture the leave time after playing
        leave_time = datetime.now()

    except Exception as e:
        print(f"Error in handle_easter_egg_trigger: {e}")
        
# Command to toggle auto-join task
@bot.tree.command(name="toggle_auto_join", description="Toggle the auto-join task.")
@has_general_role()
async def toggle_auto_join(interaction: discord.Interaction):
    global auto_join_enabled

    # Toggle the auto_join_enabled flag
    auto_join_enabled = not auto_join_enabled
    state = "enabled" if auto_join_enabled else "disabled"
    
    await interaction.response.send_message(f"Auto-join task {state}.")

@bot.tree.command(name="testsound", description="Test a specific sound in a voice channel.")
@has_general_role()
async def testsound(interaction: discord.Interaction, sound_name: str, channel: discord.VoiceChannel, leave_after: bool = True):
    available_sounds = get_available_sounds()
    
    # Defer the response to give more time
    await interaction.response.defer()
    
    if sound_name not in available_sounds:
        await interaction.followup.send(f"Sound not found. Available sounds are: {', '.join(available_sounds)}", ephemeral=True)
        return
    
    # Check if bot is already connected to a voice channel
    vc = interaction.guild.voice_client
    
    if vc is None or vc.channel != channel:
        # If not connected or connected to a different channel, connect to the specified one
        vc = await channel.connect()
    else:
        # Already connected to the same channel
        await interaction.followup.send(f"Bot is already connected to {channel.name}. Playing the sound.")

    # Define the after function to disconnect after the sound is done, if `leave_after` is True
    def after_playing(error):
        if leave_after:
            coro = vc.disconnect()
            fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
            try:
                fut.result()  # Ensure any exceptions are handled
            except Exception as e:
                print(f"Error disconnecting: {e}")

    # Play the sound
    vc.play(
        discord.FFmpegPCMAudio(os.path.join(SOUND_FOLDER, f"{sound_name}.mp3"), executable=ffmpeg_path),
        after=after_playing  # Pass the after function
    )
    
    # Send the follow-up message while the sound is playing
    await interaction.followup.send(f"Playing '{sound_name}' in {channel.name}")

@bot.tree.command(name="cheers", description="Play a sound in a voice channel.")
@has_general_role()
async def cheers(interaction: discord.Interaction, channel: discord.VoiceChannel):
    # Defer the response to avoid the 3-second timeout
    await interaction.response.defer()

    sound_to_play = choose_sound()
    vc = await channel.connect()
    join_time = datetime.now()  # Capture join time

    # Define the after function to disconnect after the sound is done
    def after_playing(error):
        coro = vc.disconnect()
        fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
        try:
            fut.result()  # Ensure any exceptions are handled
        except Exception as e:
            print(f"Error disconnecting: {e}")

    vc.play(
        discord.FFmpegPCMAudio(sound_to_play, executable=ffmpeg_path),
        after=after_playing  # Pass the after function
    )

    # Send the follow-up message after playing sound
    await interaction.followup.send(f"Playing sound in {channel.name}")

    # Log the action after the bot leaves the voice channel
    await log_action(
        voice_channel=channel,
        sound_name=os.path.basename(sound_to_play),
        is_easter_egg=False,
        mode=load_or_create_config()["mode"],
        join_time=join_time,
        leave_time=datetime.now(),  # Log the leave time after playing sound
        user=interaction.user  # Pass the user who ran the command
    )


# Slash command to join a specific voice channel without playing a sound
@bot.tree.command(name="join", description="Make the bot join a voice channel without playing a sound.")
@has_general_role()
async def join(interaction: discord.Interaction, channel: discord.VoiceChannel):
    await interaction.response.defer()  # Avoid interaction timeout
    try:
        join_time = datetime.now()  # Capture join time
        
        # Check if the bot is already in a voice channel and leave if necessary
        if interaction.guild.voice_client:
            if interaction.guild.voice_client.channel != channel:
                await interaction.guild.voice_client.disconnect()

        # Connect with self_deaf=True to suppress microphone activation
        vc = await channel.connect(self_deaf=True)

        # Log the action when joining the voice channel
        await log_action(
            voice_channel=channel,
            sound_name="No sound played",  # No sound in /join
            is_easter_egg=False,
            mode="N/A",
            join_time=join_time,
            leave_time=None,  # No leave time as it only joins
            user=interaction.user  # Pass the user who ran the command
        )

        await interaction.followup.send(f"Joined {channel.name} without playing a sound. Microphone is suppressed.")
    except Exception as e:
        await interaction.followup.send(f"Error occurred: {e}")
        print(f"Error: {e}")


# Slash command to leave whatever channel the bot is currently in
@bot.tree.command(name="leave", description="Make the bot leave the voice channel.")
@has_general_role()
async def leave(interaction: discord.Interaction):
    try:
        leave_time = datetime.now()  # Capture leave time

        if interaction.guild.voice_client:
            voice_channel = interaction.guild.voice_client.channel  # Capture the channel it was in
            await interaction.guild.voice_client.disconnect()
            
            # Log the action when leaving the voice channel
            await log_action(
                voice_channel=voice_channel,
                sound_name="No sound played",  # No sound in /leave
                is_easter_egg=False,
                mode="N/A",
                join_time=None,  # No join time as it only leaves
                leave_time=leave_time,
                user=interaction.user  # Pass the user who ran the command
            )
            
            await interaction.response.send_message(f"Bot has left {voice_channel.name}.")
        else:
            await interaction.response.send_message("Bot is not in any voice channel.")
    except Exception as e:
        await interaction.response.send_message(f"Error occurred: {e}")
        print(f"Error: {e}")


# Slash command for reloading the bot's configuration and syncing commands
@bot.tree.command(name="reload", description="Reload the bot's configuration and sync slash commands.")
@has_reload_role()
async def reload(interaction: discord.Interaction):
    try:
        await interaction.response.send_message("Reloading slash commands and configuration...")
        await bot.tree.sync()
        await interaction.followup.send("Slash commands and configuration have been successfully reloaded.")
    except Exception as e:
        await interaction.followup.send(f"Error occurred during reload: {e}")
        print(f"Error during reload: {e}")

# Periodically check and reload Easter eggs
async def periodic_check():
    while True:
        check_and_reload_easter_eggs()
        await asyncio.sleep(60)  # Check every minute

# Slash command to list, enable, or disable Easter Eggs
@bot.tree.command(name="easteregg", description="List, enable, or disable Easter Eggs.")
@app_commands.describe(easter_egg_name="Easter Egg to enable/disable", action="Enable or disable the Easter Egg")
@has_general_role()
async def easteregg(interaction: discord.Interaction, easter_egg_name: str = None, action: str = None):
    if not easter_egg_name:
        enabled_eggs = [egg.name for egg in easter_eggs if egg.enabled]
        disabled_eggs = [egg.name for egg in easter_eggs if not egg.enabled]
        await interaction.response.send_message(
            f"**Enabled Easter Eggs:**\n- " + "\n- ".join(enabled_eggs) +
            f"\n\n**Disabled Easter Eggs:**\n- " + "\n- ".join(disabled_eggs)
        )
    else:
        easter_egg_name_lower = easter_egg_name.lower()
        matched_egg = next((egg for egg in easter_eggs if egg.name.lower() == easter_egg_name_lower), None)
        if not matched_egg:
            await interaction.response.send_message(f"Easter Egg '{easter_egg_name}' not found.", ephemeral=True)
            return

        if action.lower() == "enable":
            matched_egg.enabled = True
            await interaction.response.send_message(f"Easter Egg '{matched_egg.name}' is now enabled.")
        elif action.lower() == "disable":
            matched_egg.enabled = False
            await interaction.response.send_message(f"Easter Egg '{matched_egg.name}' is now disabled.")
        else:
            await interaction.response.send_message("Invalid action. Use 'enable' or 'disable'.")
        save_easter_eggs()

@bot.tree.command(name="delete_easter_egg", description="Delete an existing Easter Egg.")
@has_reload_role()
@app_commands.describe(easter_egg_name="The name of the Easter Egg to delete.")
async def delete_easter_egg(interaction: discord.Interaction, easter_egg_name: str):
    easter_egg_name_lower = easter_egg_name.lower()
    
    # Find the Easter Egg by case-insensitive match
    matched_egg = next((egg for egg in easter_eggs if egg.name.lower() == easter_egg_name_lower), None)

    if not matched_egg:
        await interaction.response.send_message(f"Easter Egg '{easter_egg_name}' not found.", ephemeral=True)
        return

    easter_eggs.remove(matched_egg)
    save_easter_eggs()
    await interaction.response.send_message(f"Easter Egg '{easter_egg_name}' has been deleted.")

# /Add_Easter_Egg Command - Updated so the sound is case insensitive.
@bot.tree.command(name="add_easter_egg", description="Add a new Easter Egg.")
@has_general_role()
@app_commands.describe(
    name="The name of the Easter Egg to create.",
    sound="The sound file to play (e.g., cheers_bitch).",
    join_time="The time the bot should join (e.g., 1:00 AM).",
    play_delay="How many minutes after joining to play the sound.",
    timezone="Timezone to follow (e.g., ACST, America/Chicago, Europe/London, etc.)."
)
async def add_easter_egg(interaction: discord.Interaction, name: str, sound: str, join_time: str, play_delay: int, timezone: str):
    available_sounds = get_available_sounds()

    # Convert both the input sound name and Easter Egg names to lowercase for comparison
    sound_lower = sound.lower()
    available_sounds_lower = [s.lower() for s in available_sounds]
    name_lower = name.lower()

    # Check if the sound exists (case-insensitive)
    if sound_lower not in available_sounds_lower:
        await interaction.response.send_message(f"Invalid sound. Available sounds: {', '.join(available_sounds)}")
        return

    # Check if an Easter Egg with the same name (case-insensitive) already exists
    if any(egg.name.lower() == name_lower for egg in easter_eggs):
        await interaction.response.send_message(f"An Easter Egg with the name '{name}' already exists.", ephemeral=True)
        return

    # Get the actual sound name with correct casing
    matched_sound = available_sounds[available_sounds_lower.index(sound_lower)]

    try:
        datetime.strptime(join_time, "%I:%M %p")
    except ValueError:
        await interaction.response.send_message("Invalid time format. Please use the format 'HH:MM AM/PM'.")
        return

    # Create the new Easter Egg and add it to the list
    new_easter_egg = EasterEgg(name, matched_sound, join_time, play_delay, timezone)
    easter_eggs.append(new_easter_egg)
    save_easter_eggs()
    await interaction.response.send_message(f"Easter Egg '{name}' added successfully.")

'''
  _   _      _         _____           _              _   
 | | | | ___| |_ __   | ____|_ __ ___ | |__   ___  __| |_ 
 | |_| |/ _ \ | '_ \  |  _| | '_ ` _ \| '_ \ / _ \/ _` (_)
 |  _  |  __/ | |_) | | |___| | | | | | |_) |  __/ (_| |_ 
 |_| |_|\___|_| .__/  |_____|_| |_| |_|_.__/ \___|\__,_(_)
              |_|                                         
'''
@bot.tree.command(name="help", description="Displays a help menu with all commands.")
@has_general_role()
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Commands",
        colour=0x00b0f4,
        timestamp=datetime.now()
    )

    embed.set_author(
        name="Cheers Bot Help Menu",
        icon_url="https://i.imgur.com/oYhmgBJ.png"
    )

    embed.add_field(
        name="/Join <channel>",
        value="Joins the specified voice channel without playing any sound.",
        inline=False
    )
    embed.add_field(
        name="/Leave",
        value="Makes the bot leave the current voice channel.",
        inline=False
    )
    embed.add_field(
        name="/Cheers",
        value="Joins a specified voice channel, plays the current sound, and leaves the channel.",
        inline=False
    )
    embed.add_field(
        name="/Reload",
        value="Reloads the bot's configuration and syncs slash commands. Requires the appropriate role.",
        inline=False
    )
    embed.add_field(
        name="/Mode",
        value="Changes the sound mode. Choose between:\n"
              "   - `/mode single`: Play a single sound.\n"
              "   - `/mode randomize`: Play a random sound from the folder.\n"
              "   - `/mode percent`: Play sounds based on their percent values.",
        inline=False
    )
    embed.add_field(
        name="/SoundTest <sound_name> <leave_after>",
        value="Plays the specified sound in your voice channel. Use `true` to make the bot leave after the sound.",
        inline=False
    )
    embed.add_field(
        name="/Sounds",
        value="Lists all available sounds in the sound folder along with their percentage chances.",
        inline=False
    )

    embed.set_thumbnail(url="https://i.imgur.com/oYhmgBJ.png")
    embed.set_footer(
        text="Cheers Bot - Homies House",
        icon_url="https://i.imgur.com/oYhmgBJ.png"
    )

    await interaction.response.send_message(embed=embed)

'''
  _____                       _   _                 _ _ _               
 | ____|_ __ _ __ ___  _ __  | | | | __ _ _ __   __| | (_)_ __   __ _ _ 
 |  _| | '__| '__/ _ \| '__| | |_| |/ _` | '_ \ / _` | | | '_ \ / _` (_)
 | |___| |  | | | (_) | |    |  _  | (_| | | | | (_| | | | | | | (_| |_ 
 |_____|_|  |_|  \___/|_|    |_| |_|\__,_|_| |_|\__,_|_|_|_| |_|\__, (_)
                                                                |___/   
'''
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, CheckFailure):
        if not interaction.response.is_done():
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
    else:
        if not interaction.response.is_done():
            await interaction.response.send_message("An error occurred while processing the command.", ephemeral=True)
        print(f"An error occurred: {error}")

'''
  _                      _               
 | |    ___   __ _  __ _(_)_ __   __ _ _ 
 | |   / _ \ / _` |/ _` | | '_ \ / _` (_)
 | |__| (_) | (_| | (_| | | | | | (_| |_ 
 |_____\___/ \__, |\__, |_|_| |_|\__, (_)
             |___/ |___/         |___/   
'''
async def log_action(
    voice_channel: discord.VoiceChannel, 
    sound_name: str, 
    is_easter_egg: bool, 
    mode: str, 
    join_time: datetime = None, 
    leave_time: datetime = None, 
    play_delay: int = None, 
    easter_egg_details: dict = None, 
    user: discord.User = None
):
    config = load_or_create_config()

    log_settings = config.get("log_settings", {})
    embed_title = log_settings.get("embed_title", "Bot Action Log")
    footer_text = log_settings.get("footer_text", "EST. 1/1/2024")
    thumbnail_url = log_settings.get("thumbnail_url", "")
    footer_icon_url = log_settings.get("footer_icon_url", "")

    # Check for log channel ID in the config
    log_channel_id = config.get("log_channel_id", None)
    if log_channel_id is None:
        print("No log channel set, please use `/setlog`.")
        return

    # Fetch the log channel by its ID
    log_channel = bot.get_channel(log_channel_id)
    if log_channel is None:
        print(f"Log channel with ID {log_channel_id} not found.")
        return

    # Prepare the embed for logging
    embed = discord.Embed(
        title=embed_title,
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )

    # Set the thumbnail and footer
    embed.set_thumbnail(url=thumbnail_url)
    embed.set_footer(text=footer_text, icon_url=footer_icon_url)

    # Add join and leave times
    if join_time:
        embed.add_field(name="Joined Channel", value=f"{voice_channel.name} at {join_time.strftime('%Y-%m-%d %H:%M:%S')}", inline=False)
    
    if leave_time:
        embed.add_field(name="Left Channel", value=f"{voice_channel.name} at {leave_time.strftime('%Y-%m-%d %H:%M:%S')}", inline=False)

    # Log the mode of the bot
    embed.add_field(name="Mode", value=mode, inline=False)

    # Log the sound played
    embed.add_field(name="Sound Played", value=sound_name, inline=False)

    # Easter egg-specific logging
    if is_easter_egg and easter_egg_details:
        embed.add_field(name="\u2B50 Easter Egg", value="YES", inline=False)  # Add star emoji for Easter egg
        embed.add_field(name="Easter Egg Name", value=easter_egg_details.get("name"), inline=False)
        embed.add_field(name="Easter Egg Timezone", value=easter_egg_details.get("timezone"), inline=False)

    try:
        # Send the embed to the log channel
        await log_channel.send(embed=embed)
        print(f"Logged action to channel: {log_channel.name}")
    except Exception as e:
        print(f"Failed to log action: {e}")

@bot.tree.command(name="setlog", description="Set the log channel for bot actions.")
async def setlog(interaction: discord.Interaction, channel: discord.TextChannel):
    config = load_or_create_config()
    config['log_channel_id'] = channel.id
    save_config(config)
    await interaction.response.send_message(f"Log channel set to: {channel.mention}")

'''
  ____        _                        _                              _     _                     _ _             
 | __ )  ___ | |_   _ __ ___  __ _  __| |_   _    _____   _____ _ __ | |_  | |__   __ _ _ __   __| | | ___ _ __ _ 
 |  _ \ / _ \| __| | '__/ _ \/ _` |/ _` | | | |  / _ \ \ / / _ \ '_ \| __| | '_ \ / _` | '_ \ / _` | |/ _ \ '__(_)
 | |_) | (_) | |_  | | |  __/ (_| | (_| | |_| | |  __/\ V /  __/ | | | |_  | | | | (_| | | | | (_| | |  __/ |   _ 
 |____/ \___/ \__| |_|  \___|\__,_|\__,_|\__, |  \___| \_/ \___|_| |_|\__| |_| |_|\__,_|_| |_|\__,_|_|\___|_|  (_)
                                         |___/                                                                    
'''
@bot.event
async def on_ready():
    load_easter_eggs()  # Load Easter Eggs
    load_or_create_config()  # Load configuration
    await bot.tree.sync()  # Sync slash commands
    easter_egg_task.start()  # Start the Easter egg task

    # Ensure the task is started but will respect the toggle
    if not auto_join_task.is_running():
        auto_join_task.start()

    print(f"Logged in as {bot.user} and slash commands are ready.")

# Load the environment variables from .env file
load_dotenv()

# Get the bot token from the environment and run the bot
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

if not BOT_TOKEN:
    print("Error: Bot token not found in .env file.")
else:
    bot.run(BOT_TOKEN)