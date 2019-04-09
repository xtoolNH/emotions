import argparse
from webcam import realtime_emotions

"""
For Dependencies Installation using pipenv: `python -m pipenv update`
To use pipenv: `pipenv shell`
To run this code, use: `python main.py User1`
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder_name", type=str,
                        help="Please Insert Folder Name <Username_DateTime>")
    # parse the args
    args = parser.parse_args()
    print(args.folder_name)
    realtime_emotions(args.folder_name)


if __name__ == '__main__':
    print("Press Ctrl-C to exit")
    main()
