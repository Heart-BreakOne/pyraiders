These are the explanations to the values you can edit while setting up the account.
Pay attention to the commas.
true and false are lowercase without quotes.
Strings are in between double quotes.
Keep numbers outside quotes.

These two keys are MANDATORY as the application can not function without them:
"name" Unique account name, does not need to be your Twitch account name.
"token" Not URL encoded ACCESS_INFO token used to identify your login.

These are optional, they have default values that will allow the account to run without changing them:
"powered_on" Whether the assistant should run the account or not.
"preserve_loyalty" 0 -> Does not preserve loyalty. 1 -> Place on loyalty chests only if bronze loyalty. 2 -> Only if silver. 3 -> Only if gold. 4 -> Only if diamond.
"switch_if_no_loyalty" -> Replace a captain slot if there's no loyalty during a loyalty chest.
"switch_on_idle": -> Automatically switch a captain after a period of idleing.
"minimum_idle_time": -> Integer number without decimal points that determine the idle time in minutes.
"unlimited_campaign": -> Place more than one unit on campaign.
"unlimited_pvp": -> Place more than one unit on PvP.
"unlimited_dungeons": -> Place more than one unit on dungeons.
"any_captain": -> Select any captain available. Set to false if you plan to be selective.
"only_masterlist": -> Whether masterlist should be used or not. If enabled, fill the masterlist
"masterlist": [
      "captainZ1",
      "captainz1",
      "CAPTAINZ1"
    ] -> As many captain names as you want, casing doesn't matter, but they must match their name.
"ignore_blacklist": false -> Whether blacklist captains should be ignored. If enabled, fill the blacklist
"blacklist": [
      "captainZ1",
      "captainZ1",
      "captainZ1"
    ] -> Same rules as masterlist, but it's a blacklist for captains that should be avoided instead



DO NOT EDIT THE VALUES BELOW UNLESS YOU ARE HAVING ISSUES.
THESE VALUES WILL BE FILLED ONCE YOU SET THE "name" AND THE "token" values.
"temporary_ignore" -> DO NOT EDIT THIS VALUE, IT'S TEMPORARY DATA TO AVOID CAPTAIN SLOT SWITCH LOOPING.
"user_agent": "", LEAVE BLANK, DO NOT EDIT THIS VALUE UNLESS YOU HAVE ISSUES WITH THE USER AGENT. DUPLICATE USER AGENTS ARE NOT ALLOWED.
"proxy": "", -> LEAVE BLANK, DO NOT EDIT THIS VALUE UNLESS YOU HAVE ISSUES WITH THE PROXY. DUPLICATE PROXIES ARE NOT ALLOWED.
"userId": "", -> LEAVE BLANK, WILL BE FILLED THE  "name" AND THE "token" values.
"favoriteCaptainIds": "" -> LEAVE BLANK, WILL BE FILLED THE  "name" AND THE "token" values.
"units": "" -> LEAVE BLANK, WILL BE FILLED ONCE YOU SET THE  "name" AND THE "token" values.

Once the "units" are filled with all of your units, you can edit two values:

"priority": 0 -> Never ever place the unit. 1 -> Highest placement priority. The higher the number, the lower the priority.
"level_up": -> Whether or not unit should be leveled up.

Here's what it will look like:
    "units": [
      {
        "userId": "userId",
        "unitType": "archer",
        "level": "1",
        "skin": "skinfullarcherancient",
        "cooldownTime": null,
        "unitId": "unitId",
        "specializationUid": null,
        "soulType": null,
        "soulId": null,
        "priority": 0,
        "level_up": false
      },
      {
        "userId": "userId",
        "unitType": "tank",
        "level": "1",
        "skin": null,
        "cooldownTime": null,
        "unitId": "unitId",
        "specializationUid": null,
        "soulType": null,
        "soulId": null,
        "priority": 0,
        "level_up": false
      }
    ]