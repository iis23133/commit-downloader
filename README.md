# GitHub Commit Downloader

A simple Python GUI to download added and modified files from a specific GitHub commit.

## Features

- Downloads only files marked as *added* or *modified*
- Requires only a commit URL and a local folder
- Lightweight, no external GUI dependencies

## Requirements

- Python 3.x
- `requests`

## Setup

```bash
git clone https://github.com/iis23133/commit-downloader.git
cd commit-downloader
pip install requests
python main.py
