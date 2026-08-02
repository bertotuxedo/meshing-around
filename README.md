# Mesh Bot for Network Testing and BBS Activities

Mesh Bot is a feature-rich Python bot designed to enhance your [Meshtastic](https://meshtastic.org/docs/introduction/) network experience. It provides powerful tools for network testing, messaging, games, and more! All via text-based message delivery. Whether you want to test your mesh, send messages, or play games, [mesh_bot.py](mesh_bot.py) has you covered.

* [Getting Started](#getting-started)

![Example Use](etc/pong-bot.jpg "Example Use")

#### TLDR
* [Docker Compose quick start](#getting-started) — recommended; no host Python or virtual environment
* [Native installation](INSTALL.md)
* [Configuration guide](modules/README.md)
* [Games help](modules/games/README.md)

## Key Features
![CodeQlBadge](https://github.com/SpudGunMan/meshing-around/actions/workflows/dynamic/github-code-scanning/codeql/badge.svg)

### Intelligent Keyword Responder
- **Automated Responses**: Detects keywords like "ping" and replies with "pong" in direct messages (DMs) or group channels.
- **Customizable Triggers**: Monitors group channels for specific keywords and sends custom responses.
- **Emergency Detection**: Watches for emergency-related keywords and alerts a wider audience.
- **New Node Greetings**: Automatically welcomes new nodes joining the mesh.

### Network Tools
- **Mesh Testing**: Use `ping` to test message delivery with realistic packets.
- **Hardware Testing**: The `test` command sends incrementally sized data to test radio buffer limits.
- **Network Monitoring**: Alerts for noisy nodes, tracks node locations, and suggests optimal relay placement.

- **Site Survey & Location Logging**: Use the `map` command to log your current GPS location with a custom description—ideal for site surveys, asset tracking, or mapping nodes locations. Entries are saved to a CSV file for later analysis or visualization.

### Multi-Radio/Node Support
- **Simultaneous Monitoring**: Observe up to nine networks at once.
- **Flexible Messaging**: Send mail and messages between networks.

### Advanced Messaging Capabilities
- **Mail Messaging**: Leave messages for other devices; delivered as DMs when the device is next seen. Use `bbspost @nodeNumber #message` or `bbspost @nodeShortName #message`.
- **Message Scheduler**: Automate messages such as weather updates or net reminders.
- **Store and Forward**: Retrieve missed messages with the `messages` command; optionally log messages to disk.
- **BBS Linking**: Connect multiple bots to expand BBS coverage.
- **E-Mail/SMS Integration**: Send mesh messages to email or SMS for broader reach.
- **New Node Greetings**: Automatically greet new nodes via text.

### Interactive AI and Data Lookup
- **Weather, Earthquake, River, and Tide Data**: Get local alerts and info from NOAA/USGS; uses Open-Meteo for areas outside NOAA coverage.
- **Wikipedia Search**: Retrieve summaries from Wikipedia and Kiwix
- **OpenWebUI, Ollama LLM Integration**: Query the [Ollama](https://github.com/ollama/ollama/tree/main/docs) AI for advanced responses. Supports RAG (Retrieval Augmented Generation) with Wikipedia/Kiwix context and [OpenWebUI](https://github.com/open-webui/open-webui) integration for enhanced AI capabilities. [LLM Readme](modules/llm.md)
- **Satellite Passes**: Find upcoming satellite passes for your location.
- **GeoMeasuring Tools**: Calculate distances and midpoints using collected GPS data; supports Fox & Hound direction finding.
- **RSS & News Feeds**: Receive news and data from multiple sources directly on the mesh.

### Proximity Alerts
- **Location-Based Alerts**: Get notified when members arrive at a configured latitude/longitude—ideal for campsites, geo-fences, or remote locations. Optionally, trigger scripts, send emails, or automate actions (e.g., change node config, turn on lights, or drop an `alert.txt` file to start a survey or game).
- **Customizable Triggers**: Use proximity events for creative applications like "king of the hill" or 🧭 geocache games by adjusting the alert cycle.
- **High Flying Alerts**: Receive notifications when nodes with high altitude are detected on the mesh.
- **Voice/Command Triggers**: Activate bot functions using keywords or voice commands (see [Voice Commands](modules/README.md#voice-commands-vox) for "Hey Chirpy!" support).
- **YOLOv5 alerts**: Use camera modules to detect objects or OCR

### EAS Alerts
- **FEMA iPAWS/EAS Alerts**: Receive Emergency Alerts from FEMA via API on internet-connected nodes.
- **NOAA EAS Alerts**: Get Emergency Alerts from NOAA via API.
- **USGS Volcano Alerts**: Receive volcano alerts from USGS via API.
- **Bund-Warnmeldung (Deutschland)**: Receive emergency alerts from warnung.bund.de feed for Germany.
- **Offline EAS Alerts**: Report EAS alerts over the mesh using external tools, even without internet.

### File Monitor Alerts
- **File Monitoring**: Watch a text file for changes and broadcast updates to the mesh channel.
- **News File Access**: Retrieve the contents of a news file on request; supports multiple news sources or files.
- **Shell Command Access**: Execute shell commands via DM with replay protection (admin only).

#### Radio Frequency Monitoring
- **SNR RF Activity Alerts**: Monitor radio frequencies and receive alerts when high SNR (Signal-to-Noise Ratio) activity is detected.
- **Hamlib Integration**: Use Hamlib (rigctld) to monitor the S meter on a connected radio.
- **Speech-to-Text Broadcasting**: Convert received audio to text using [Vosk](https://alphacephei.com/vosk/models) and broadcast it to the mesh.
- **WSJT-X Integration**: Monitor WSJT-X (FT8, FT4, WSPR, etc.) decode messages and forward them to the mesh network with optional callsign filtering.
- **JS8Call Integration**: Monitor JS8Call messages and forward them to the mesh network with optional callsign filtering.
- **Meshages TTS**: The bot can speak mesh messages aloud using [KittenTTS](https://github.com/KittenML/KittenTTS). Enable this feature to have important alerts and messages read out loud on your device—ideal for hands-free operation or accessibility. See [radio.md](modules/radio.md) for setup instructions.
- **Offline Tone out Decoder**: Decode fire Tone out and DTMF and action with alerts to mesh

### Asset Tracking, Check-In/Check-Out, and Inventory Management
Advanced check-in/check-out and asset tracking for people and equipment—ideal for accountability, safety monitoring, and logistics (e.g., Radio-Net, FEMA, trailhead groups). Admin approval workflows, GPS location capture, and overdue alerts. The integrated inventory and point-of-sale (POS) system enables item management, sales tracking, cart-based transactions, and daily reporting, for swaps, emergency supply management, and field operations, maker-places.

### Fun and Games
- **Built-in Games**: Play classic games like DopeWars, Lemonade Stand, BlackJack, and Video Poker directly via DM.
- **FCC ARRL QuizBot**: Practice for the ham radio exam with the integrated quiz bot.
- **Command-Based Gameplay**: Use the `games` command to view available games and start playing.
- **Telemetry Leaderboard**: Compete for fun stats like lowest battery or coldest temperature.

#### QuizMaster
- **Group Quizzes**: Admins can start and stop quiz games for groups.
- **Player Participation**: Players join with `q: join`, leave with `q: leave`, and answer questions by prefixing their answer with `q:`, e.g., `q: 42`.
- **Scoring & Leaderboards**: Check your score with `q: score` and see the top performers with `q: top`.
- **Admin Controls**: QuizMasters (from `bbs_admin_list`) can use `q: start`, `q: stop`, and `q: broadcast <message>` to manage games.

#### Survey Module
- **Custom Surveys**: Create and manage surveys by editing JSON files in `data/survey`. Multiple surveys are supported (e.g., `survey snow`).
- **User Feedback**: Users participate via DM; responses are logged for review.
- **Reporting**: Retrieve survey results with `survey report` or `survey report <surveyname>`.

### Data Reporting
- **HTML Reports**: Visualize bot traffic and data flows with a built-in HTML generator. See [data reporting](logs/README.md) for details.

### Robust Message Handling
- **Automatic Message Chunking**: Messages over 160 characters are automatically split to ensure reliable delivery across multiple hops.

- **Command Lockdown**: Admins can use `cmd stop` to lock out non-admin commands, and `cmd start` to restore normal command access. Non-admins may still use `cmd` to view help.

## Getting Started

Docker Compose is the recommended way to run Meshing Around. Python and all
dependencies stay inside the container, so the host does **not** need Python,
`pip`, or a virtual environment.

### Before you begin

You need:

- Git
- Docker Engine with the Compose plugin
- A Meshtastic node that the Docker host can reach over TCP, normally on port
  `4403`

Confirm that Compose is available:

```sh
docker compose version
```

### 1. Clone the repository

```sh
git clone https://github.com/bertotuxedo/meshing-around.git
cd meshing-around
```

### 2. Configure the Meshtastic connection

Open `config.yaml` and change the hostname to the IP address or DNS name of
your Meshtastic node:

```yaml
interface:
  type: tcp
  hostname: 192.168.1.95:4403
```

Keep the port at `4403` unless your Meshtastic TCP API uses a different port.
Use an address reachable from the Docker host; `localhost` points back to the
container and is usually incorrect.

The YAML file contains only your overrides. Settings you omit continue to
inherit from `config.template`.

Optional Compose settings such as timezone, dashboard port, and Docker log
rotation can be placed in an untracked `.env` file:

```sh
cp .env.example .env
```

Then edit `.env` as needed. If you uncomment `MESHTASTIC_HOST`,
`MESHTASTIC_PORT`, or `LOG_LEVEL`, those values override `config.yaml`.
Do not commit passwords, tokens, channel keys, or device private keys.

### 3. Validate and start the bot

```sh
docker compose config --quiet
docker compose up -d --build
```

The first build downloads the base image and installs dependencies, so it can
take a few minutes. Later starts are much faster.

### 4. Verify startup

```sh
docker compose ps
docker compose logs --tail=100 meshing-around
```

The service should move to `healthy` after startup. To follow live logs:

```sh
docker compose logs -f meshing-around
```

Press `Ctrl+C` to stop following the logs; the container continues running in
the background. Send `ping` or `cmd` to the connected Meshtastic node from
another node to confirm that the bot responds.

### Common operations

Restart the bot after a configuration change:

```sh
docker compose restart meshing-around
```

Update to the latest repository version and rebuild:

```sh
git pull
docker compose build --pull
docker compose up -d
```

Stop and remove the container while preserving data and logs:

```sh
docker compose down
```

Mutable data and application logs persist in the `meshing-data` and
`meshing-logs` named volumes. Do not use `docker compose down --volumes`
unless you intentionally want to delete them.

### Troubleshooting

- Run `docker compose logs meshing-around` to see configuration, connection,
  and startup errors.
- Confirm that the Docker host can reach the configured node on TCP port
  `4403`.
- If the service is unhealthy, inspect it with
  `docker inspect --format '{{json .State.Health}}' meshing-around`.
- Run `docker compose config` to see the fully resolved Compose configuration,
  including values loaded from `.env`.
- See the [complete Docker Compose guide](script/docker/README.md) for backups,
  environment overrides, serial devices, legacy INI files, and advanced
  troubleshooting.

### Native installation

A non-container installation remains available through [`install.sh`](INSTALL.md),
but it uses a host Python environment. Compose is the simpler option when you
want to avoid virtual environments.

## Module Help
Configuration Guide
[modules/README.md](modules/README.md)

### Game Help
Games are DM only by default

[modules/games/README.md](modules/games/README.md)

### Firmware 2.6 DM Key, and 2.7 CLIENT_BASE Favorite Nodes
Firmware 2.6 introduced [PKC](https://meshtastic.org/blog/introducing-new-public-key-cryptography-in-v2_5/), enabling secure private messaging by adding necessary keys to each node. To fully utilize this feature, you should add favorite nodes—such as BBS admins—to your node’s favorites list to ensure their keys are retained. A helper script is provided to simplify this process:
- Run the helper script from the main program directory: `python3 script/addFav.py`
- By default, this script adds nodes from `bbs_admin_list` and `bbslink_whitelist`
- If using a virtual environment, run: `launch.sh addfav`
- The API will not work-fully today to set nodes this is a WIP

Additionally, you can just DM a bot to "auto favorite." If your node is set to not be messageable, DMs won't work—be advised.

To configure favorite nodes, add their numbers to your config file:
```conf
[general]
favoriteNodeList = # list of favorite nodes numbers ex: 2813308004,4258675309 used by script/addFav.py
```

### MQTT Notes
There is no direct support for MQTT in the code, however, reports from Discord are that using [meshtasticd](https://meshtastic.org/docs/hardware/devices/linux-native-hardware/) with no radio and attaching the bot to the software node, which is MQTT-linked, allows routing. Tested working fully Firmware:2.6.11 with [mosquitto](https://meshtastic.org/docs/software/integrations/mqtt/mosquitto/).

~~There also seems to be a quicker way to enable MQTT by having your bot node with the enabled [serial](https://meshtastic.org/docs/configuration/module/serial/) module with echo enabled and MQTT uplink and downlink. These two~~ 

# Recognition

I used ideas and snippets from other responder bots and want to call them out!

### Inspiration and Code Snippets
- [MeshLink](https://github.com/Murturtle/MeshLink)
- [Meshtastic Python Examples](https://github.com/pdxlocations/meshtastic-Python-Examples)
- [Meshtastic Matrix Relay](https://github.com/geoffwhittington/meshtastic-matrix-relay)

### Games Ported From
- [Lemonade Stand](https://github.com/tigerpointe/Lemonade-Stand/)
- [Drug Wars](https://github.com/Reconfirefly/drugwars)
- [BlackJack](https://github.com/Himan10/BlackJack)
- [Video Poker Terminal Game](https://github.com/devtronvarma/Video-Poker-Terminal-Game)
- [Python Mastermind](https://github.com/pwdkramer/pythonMastermind/)
- [Golf](https://github.com/danfriedman30/pythongame)
- ARRL Question Pool Data from https://github.com/russolsen/ham_radio_question_pool

### Special Thanks
For testing and feature ideas on Discord and GitHub, if its stable its thanks to you all.
- **PiDiBi, Cisien, bitflip, nagu, Nestpebble, NomDeTom, Iris, Josh, GlockTuber, FJRPiolt, dj505, Woof, propstg, snydermesh, trs2982, F0X, Malice, mesb1, Hailo1999**
- **xdep**: For the reporting html. 📊
- **mrpatrick1991**: For OG Docker configurations. 💻
- **A-c0rN**: Assistance with iPAWS and 🚨
- **Mike O'Connell/skrrt**: For [eas_alert_parser](etc/eas_alert_parser.py) enhanced by **sheer.cold**
- **dadud**: For idea on [etc/icad_tone.py](etc/icad_tone.py)
- **WH6GXZ nurse dude**: Volcano Alerts 🌋
- **mikecarper**: hamtest, leading to quiz etc.. 📋
- **c.merphy360**: high altitude alerts. 🚀
- **G7KSE**: DX Spotting idea. 📻
- **Growing List of GitHub Contributers**
- **Meshtastic Discord Community**: For putting up with 🥔

### Tools
- **Node Backup Management**: [Node Slurper](https://github.com/SpudGunMan/node-slurper)

Meshtastic® is a registered trademark of Meshtastic LLC. Meshtastic software components are released under various licenses, see GitHub for details. No warranty is provided - use at your own risk.
