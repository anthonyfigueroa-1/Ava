import argparse

def parse_args():
    args = argparse.ArgumentParser()

    args.add_argument("--id", type=int, help="Ticket #ID of ticket you would like to run TC test on")

    return args.parse_args()
