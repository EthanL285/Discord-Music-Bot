# Discord Music Bot

I created this music bot to provide a reliable solution for playing songs and playlists from YouTube in Discord. Unlike many existing bots that don't work or are restricted by copyright laws, this bot lets you enjoy music without hassle.

## Features
- Play songs and playlists from YouTube URLs
- Pause, resume, and skip songs
- View, clear, and shuffle the queue

## Commands

| Command       | Description                                    |
|--------------|--------------------------------|
| `!play <url>` | Plays a song or playlist from a URL |
| `!pause`      | Pauses the current song |
| `!resume`     | Resumes the paused song or queue |
| `!skip`       | Skips the current song and plays the next |
| `!queue`      | Shows the current queue |
| `!clear`      | Clears the queue |
| `!shuffle`    | Shuffles the queue |
| `!join`       | Joins the voice channel |
| `!leave`      | Leaves the voice channel |
| `!help`       | Displays available commands |

## Language
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

## Installation

### 1. Clone Repository
To get started, clone this repository to your local machine:
```bash
git clone https://github.com/EthanL285/Discord-Music-Bot.git
```
### 2. Install Dependencies
Install all required dependencies using pip:
```bash
pip install -r requirements.txt
```
### 3. Install FFmpeg
   
FFmpeg is required for audio streaming. You can install it as follows:

**Windows:**  
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract the files and add the bin folder to your system PATH

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 4. Configure Your Bot Token
Create a `.env` file in the root directory of your project and add your Discord bot token:
```bash
DISCORD_TOKEN=your_bot_token_here
```

### 5. Run the Bot
Once everything is set up, you can run the bot using the following command:
```bash
python bot.py
```

## Important Notes

- **Permissions:** Ensure the bot has permissions to connect and speak in voice channels
- **Playlist URL:** For playlists, ensure you're using the playlist URL *(not a single song URL from the playlist).* The bot will fail to fetch videos if the playlist URL is incorrect
- **Video Restrictions:** If a playlist contains a geo-restricted, age-restricted, or unavailable video, the bot will fail to download the playlist.






