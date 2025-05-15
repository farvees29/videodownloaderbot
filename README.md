# Telegram Video Downloader Bot

## Setup

1. Create a Telegram bot and get its token from @BotFather.

2. On Railway, create a new project and deploy this repo.

3. Add environment variable:
   - `TELEGRAM_BOT_TOKEN` = your bot token

4. Railway runs `bot.py` and your bot will be live.

## Usage

Send your bot a video URL from supported sites.

The bot downloads the video using yt-dlp + ffmpeg and sends it back.

Limitations:
- Max Telegram file size ~2GB
- Large videos might fail to upload
