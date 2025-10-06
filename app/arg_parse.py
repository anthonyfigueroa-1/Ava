import argparse

def parse_args():
    args = argparse.ArgumentParser()

    args.add_argument("--id")

    return args.parse_args()
