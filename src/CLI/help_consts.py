class HelpDocs:
    telegram_creds_file:str = "A path for a file containing the credentials for the telegram app"
    telegram_group: str = "Telegram group to crawl out from. Can be specified multiple times"
    telegram_groups_file: str = "Path for a file containing a JSON list of groups to crawl out from"
    history_period: str = "Number of days to search in groups history for other group's references"
    crawling_depth: str = """The maximum level of iteration. First iteration is the given groups, second iteration is 
                           the referenced in the given groups and so on.."""
    concurrency_limit: str = "Positive number specifying the number of groups that can be handled at the same time."
    output_file_path: str = "Path for an output file contains a JSON list of all found groups"
