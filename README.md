# dump

Effortlessly send files to your Dropbox from the command line.

## What is this thing?

Mostly, it was a one-day project to get some stuff done for work.
But for you, it shows off three things:

1. The [Dropbox Python API](https://www.dropbox.com/developers/documentation/python#overview): see `dump/dump.py`.
1. A simple [Click](https://click.palletsprojects.com/en/7.x/) CLI: see `dump/cli.py`.
1. A `pip`-installable package that provides a CLI command: see `setup.py`.

## How do I make my own Dropbox app?

As of the time of writing...

1. Go to the [Dropbox Developer's website](https://www.dropbox.com/developers).
1. Go the App console (top right).
1. Create an app.
1. Choose "Dropbox API" (**not** "Dropbox Business API").
1. Choose "App folder" access (**not** "Full Dropbox").
1. Give your app a name.
1. Scroll down to "Generated access token", generate a token, and keep it around.

The token is what lets you talk to the Dropbox API for your own account.

Head over to the [Dropbox Python API](https://www.dropbox.com/developers/documentation/python#overview)
to see what you can do with it!
