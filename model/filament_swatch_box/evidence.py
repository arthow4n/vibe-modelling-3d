"""Object-owned naming wrapper for shared compact evidence retention."""
import argparse
from pathlib import Path
from physical_analysis.evidence import retain_run

ROOT = Path(__file__).resolve().parent


def retain(run, label):
    if not label.replace('_', '').isalnum():
        raise ValueError('Label must be a short identifier')
    return retain_run(run, ROOT/'notes'/'analysis'/label)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    parser.add_argument('label')
    args = parser.parse_args()
    print(retain(args.run, args.label))
