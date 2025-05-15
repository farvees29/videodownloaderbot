import os
import asyncio
from yt_dlp import YoutubeDL
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DOWNLOAD_DIR = "./downloads"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send me a video URL and I'll download it for you using yt-dlp + ffmpeg!"
    )

def get_best_stream_url(url: str) -> str:
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        stream_url = info.get('url')
        print("Extracted stream URL:", stream_url)
        return stream_url

async def download_with_ffmpeg(stream_url: str, output_path: str) -> None:
    command = [
        'ffmpeg',
        '-y',
        '-i', stream_url,
        '-c', 'copy',
        output_path,
    ]
    print("Running ffmpeg command:", ' '.join(command))
    proc = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise Exception(f"ffmpeg error: {stderr.decode()}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    await update.message.reply_text(f"Processing your URL:\n{url}")

    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    print("Download dir exists:", os.path.exists(DOWNLOAD_DIR))

    try:
        stream_url = get_best_stream_url(url)
        if not stream_url:
            await update.message.reply_text("❌ Couldn't extract video URL.")
            return

        filename = "video.mp4"
        output_path = os.path.abspath(os.path.join(DOWNLOAD_DIR, filename))
        print("Output file path:", output_path)

        await update.message.reply_text("⏳ Downloading video, please wait...")
        await download_with_ffmpeg(stream_url, output_path)

        await update.message.reply_document(document=InputFile(output_path))
        os.remove(output_path)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
