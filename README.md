# Sheffield-Discord-Bot

![Python 3.6+ badge](https://img.shields.io/badge/python-3.6%2B-blue)
![Code quality badge](https://img.shields.io/codefactor/grade/github/FelixRandle/Sheffield-Discord-Bot/master)
![GitHub issues badge](https://img.shields.io/github/issues/FelixRandle/Sheffield-Discord-Bot)
![GitHub forks badge](https://img.shields.io/github/forks/FelixRandle/Sheffield-Discord-Bot)
![GitHub stars badge](https://img.shields.io/github/stars/FelixRandle/Sheffield-Discord-Bot)
![GPL-3.0 license badge](https://img.shields.io/github/license/FelixRandle/Sheffield-Discord-Bot)
![Discord server status badge](https://img.shields.io/discord/612377874787336212)

Discord bot created for the (unofficial) University of Sheffield Computer Science server.

Main Author:

- Felix Randle

Contributors:

- William Lee

## Requirements

**Python 3.6 or higher is required.**

A complete description of Python package requirements can be found in `requirements.txt`.

The recommended method of installing all the requirements is using pip:

```bash
pip install -r requirements.txt
```

Additionally, you have two other requirements:

- MySQL server, version 8.0 or higher. Download MySQL server from [here](https://dev.mysql.com/downloads/mysql/)
- A Discord bot token. You can create a bot application [here](https://discord.com/developers/docs/intro#bots-and-apps)

## Setup

### Configuring environment variables

You must configure your environment variables such that the program is able to connect to your database, and connect Discord. The recommended way is to write your environment variables into a file called `.env`. This file is loaded automatically by the bot.

See `.env_example` for a template of a `.env` file.

### Running the bot

Simply execute `main.py`:

```bash
python3 main.py
```

## Contributing

Pull requests are welcome.
Please make sure to test major updates before submitting a pull request.

## License

[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)
