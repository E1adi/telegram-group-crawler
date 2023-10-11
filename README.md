# telegram-group-crawler

This Crawler, built for telegram, starts at a given list of groups and crawl out from there to any other group/channel that were referenced whether by a direct link or by a message that was forward from other groups/channels.
You can also specify how far it will look for in each group/channel in term of a datetime object.

You need to change the telegram credentials on main.py file in order to get started. In order to create telegram credentials, go to [my.telegram.org](https://my.telegram.org/).

The results are written to a file as a json list composed of links to join the groups that the crawler have found.
