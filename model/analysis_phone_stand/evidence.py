"""Object-owned naming wrapper for shared compact evidence retention."""
import argparse
from pathlib import Path
from physical_analysis.evidence import retain_run

ROOT=Path(__file__).resolve().parent

def retain(run,label):
    if not label.replace('_','').isalnum():
        raise ValueError('Label must be a short identifier')
    return retain_run(run, ROOT/'notes'/'analysis'/label)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);p.add_argument('label')
    a=p.parse_args()
    print(retain(a.run,a.label))
