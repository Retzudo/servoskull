[![Build Status](https://travis-ci.org/Retzudo/servoskull.svg?branch=master)](https://travis-ci.org/Retzudo/servoskull)

# Servo-skull

*A custom Discord bot.*

## Running the bot
1. Build the Docker image: `docker build -t servoskull .`
2. Run a Docker container: `docker run --name servoskull --restart=always -e SERVOSKULL_TOKEN=<YOUR_TOKEN> servoskull`
3. Open `https://discordapp.com/api/oauth2/authorize?scope=bot&permissions=0&client_id=<YOUR_CLIENT_ID>`.
   You can get your client ID from your Discord dev dashboard.

If you want to change the default command prefix `!` to something else, add another parameters
`-e SERVOSKULL_PREFIX=<PREFIX>` e. g. `-e SERVOSKULL_PREFIX=#`


## Extending the command list
Create a new class in `commands.py` that inherits from `Command` or `SoundCommand` depending on what you need and
implement the `execute` method. Finally, add your new class to the `commands` dictionary. The class properties
`help_text` and `required_arguments` are optional it's highly recommended you add them.