# telegram-group-crawler

This Crawler, built for telegram, starts at a given list of groups and crawl out from there to any other group/channel that were referenced whether by a direct link or by a message that was forward from other groups/channels.
You can also specify how far it will look for in each group/channel in term of a datetime object.

You need to change the telegram credentials on main.py file in order to get started. In order to create telegram credentials, go to [my.telegram.org](https://my.telegram.org/).

The results are written to a file as a json list composed of links to join the groups that the crawler have found.

Usage:

`python -m tele_crawl [Options]`
* Pay attention for required options; --creds and either --group or --groups-file or both

Usage: tele_crawl.py [OPTIONS]

Options:
  -c, --creds PATH                A path for a file containing the credentials
                                  for the telegram app  [required]
  -g, --group TEXT                Telegram group to crawl out from. Can be
                                  specified multiple times
  --groups-file PATH              Path for a file containing a JSON list of
                                  groups to crawl out from
  -p, --history-period INTEGER RANGE
                                  Number of days to search in groups history
                                  for other group's references  [x>=0]
  -d, --crawling-depth INTEGER RANGE
                                  The maximum level of iteration. First
                                  iteration is the given groups, second
                                  iteration is  the referenced in the given
                                  groups and so on..  [x>=0]
  -l, --concurrency-limit INTEGER RANGE
                                  Positive number specifying the number of
                                  groups that can be handled at the same time.
                                  [x>=1]
  -o, --output PATH               Path for an output file contains a JSON list
                                  of all found groups
  --help                          Show this message and exit.

