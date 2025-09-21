# Discord Music Bot 🎵

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Discord.py](https://img.shields.io/badge/Discord.py-Latest-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A feature-rich Discord bot for playing and managing music in voice channels. This bot provides advanced navigation through song history, lyrics fetching, and intuitive queue management - all with a simple command structure.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Commands](#commands)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Features

- 🎵 Play music from YouTube
- 📋 Queue system for multiple songs
- 🔄 Navigation through song history (previous/next)
- 🔁 Loop mode for repeating songs
- 🔊 Volume control
- 📝 Lyrics fetching
- 📊 Queue display
- 🎧 Now playing command
- ⏯️ Pause and resume functionality

## Requirements

- Python 3.8+
- Discord.py
- yt-dlp
- FFmpeg
- Discord Bot Token
- Internet connection for YouTube access

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/kikepy/discord-bot.git
   cd discord-bot
    ```
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Install FFmpeg:
   - Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html) and add to PATH.
   - macOS: Use Homebrew `brew install ffmpeg`.
   - Linux: Use package manager, e.g., `sudo apt install ffmpeg`.

4. Create a Discord bot:
    - Go to the [Discord Developer Portal](https://discord.com/developers/applications).
    - Create a new application and set up a bot.
    - Enable necessary intents (e.g., Message Content Intent is required).
    - Copy the bot token.
    - Invite the bot to your server with appropriate permissions.

## Usage
Start the bot:
   ```
   python main.py
   ```
   Once the bot is running, you'll see a "Bot [your-bot-name] is ready!" message in the console.

### Example Usage

User: !play despacito Bot: Searching... despacito Bot: Now playing: 
Despacito - Luis Fonsi ft. Daddy Yankee  

User: !queue Bot: Current queue:  

    1. Shape of You - Ed Sheeran
    2. Dance Monkey - Tones and I


## Implementation Details

- **Song History**: The bot uses a custom SongHistory class that maintains a navigable history of up to 50 songs with prev/next functionality
- **Queue Management**: Songs are added to a queue when a track is already playing
- **Command Handling**: Built with discord.py's Cog system for modular command organization

## Configuration

Create a `config.json` file in the `config` directory with the following structure:
```json
{
  "token": "YOUR_DISCORD_BOT_TOKEN_HERE"
}
```
   
## Commands

### Music Controls
| Command        | Description                                              | Example           |
|----------------|----------------------------------------------------------|-------------------|
| `!join`        | Join your voice channel                                  | `!join`           |
| `!play <song>` | Search and play a song or add to queue if one is playing | `!play despacito` |
| `!pause`       | Pause the current song                                   | `!pause`          |
| `!next`        | Skip to the next song                                    | `!next`           |
| `!previous`    | Go back to the previous song                             | `!previous`       |
| `!leave`       | Disconnect from voice channel                            | `!leave`          |

### Queue Management
| Command           | Description                           | Example      |
|-------------------|---------------------------------------|--------------|
| `!queue`          | Display the current queue             | `!queue`     |
| `!loop`           | Toggle loop mode for the current song | `!loop`      |
| `!volume <0-100>` | Set the volume                        | `!volume 75` |

### Song Information
| Command          | Description                                 | Example                          |
|------------------|---------------------------------------------|----------------------------------|
| `!nowplaying`    | Display title of the currently playing song | `!nowplaying`                    |
| `!np`            | Alias for nowplaying                        | `!np`                            |
| `!current`       | Alias for nowplaying                        | `!current`                       |
| `!currentsong`   | Alias for nowplaying                        | `!currentsong`                   |
| `!lyrics [song]` | Get lyrics for current or specified song    | `!lyrics` or `!lyrics despacito` |

## Project Structure

```
discord-bot/
├── commands/
│   ├── music_commands.py    # Music player functionality
│   ├── song_history.py      # Track song history for navigation
│   └── utility_commands.py  # Utility commands
├── config/
│   ├── config.json          # Bot configuration
│   └── json_reader.py       # Configuration loader
├── main.py                  # Bot entry point
└── README.md                # Documentation
```

## Contributing

I welcome contributions to improve this Discord Music Bot! Here's how you can contribute:  

1. Fork the repository

2. Create your feature branch: 
    ```bash
    git checkout -b feature/amazing-feature
    ```
3. Implement your changes
4. Add tests if applicable

5. Commit your changes:
    ```bash
    git commit -m 'Add some amazing feature'
    ```
6. Push to the branch:
    ```bash
    git push origin feature/amazing-feature
    ```

7. Open a Pull Request

### Contribution Guidelines
- Follow PEP 8 style guidelines for Python code
- Write meaningful commit messages
- Update documentation for any new features
- Add comments to complex code sections
- Test your changes before submitting

## Troubleshooting

- **Bot not connecting to voice channel?**
  - Ensure you have the proper permissions in your Discord server
  - Check if your bot token is valid in config.json

- **No sound playing?**
  - Verify FFmpeg is correctly installed and in your PATH
  - Check your internet connection

- **Song history navigation not working?**
  - Make sure you've played multiple songs first
  - Check the console for any errors
  
- **Rate limiting issues?**
  - The bot implements exponential backoff for YouTube requests
  - If you see "Rate limited" messages, wait a few minutes before trying again

- **Lyrics not appearing?**
  - The lyrics API might be down or the song title might not match exactly
  - Try using `!lyrics` with the exact artist and song name


## License
This project is licensed under the MIT License - see the LICENSE file for details.  


--- 
Made with ❤️ by [kikepy](https://github.com/kikepy)
