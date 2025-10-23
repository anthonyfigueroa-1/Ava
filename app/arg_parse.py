import argparse

def parse_args():
    args = argparse.ArgumentParser()

    args.add_argument("--id", type=int, help="Ticket #ID of ticket you would like to run AIR test on")
    args.add_argument("--updateai", action="store_true", help="Prompts to verify account and connect to Tech Team SharePoint to fetch new ai instructions")

    return args.parse_args()
