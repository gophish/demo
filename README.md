# Gophish Demo

This project uses the [Gophish Python API client](https://github.com/gophish/api-client-python) to load demo data into a local Gophish instance. This is a great way to explore Gophish without having to launch real campaigns.

## Installation

To install the dependencies, run:

```
pip install -r requirements.txt
```

This demo assumes you have a local installation of [Gophish](https://getgophish.com) downloaded and started.

## Usage

The only required flag is `--api-key`. Otherwise, the values should work for a standard installation of Gophish on your local machine.

```
$ python create_demo.py -h
usage: create_demo.py [-h] --api-key API_KEY [--api-url API_URL]
                      [--phish-url PHISH_URL] [--num-groups NUM_GROUPS]
                      [--num-members NUM_MEMBERS]
                      [--percent-opened PERCENT_OPENED]
                      [--percent-clicked PERCENT_CLICKED]
                      [--percent-submitted PERCENT_SUBMITTED]
                      [--percent-reported PERCENT_REPORTED]

Loads demo data into a Gophish instance

optional arguments:
  -h, --help            show this help message and exit
  --api-key API_KEY     The Gophish API key (default: None)
  --api-url API_URL     The URL pointing to the Gophish admin server (default:
                        https://localhost:3333)
  --phish-url PHISH_URL
                        The URL pointing to the Gophish phishing server
                        (default: http://localhost)
  --num-groups NUM_GROUPS
                        The number of groups to create (default: 10)
  --num-members NUM_MEMBERS
                        The number of recipients in each group (default: 100)
  --percent-opened PERCENT_OPENED
                        Percent of users to open the emails in the campaign
                        (default: 50)
  --percent-clicked PERCENT_CLICKED
                        Percent of users to click the links in the campaign
                        (default: 20)
  --percent-submitted PERCENT_SUBMITTED
                        Percent of users to submit data in the campaign
                        (default: 5)
  --percent-reported PERCENT_REPORTED
                        Percent of users to report the emails in the campaign
                        (default: 5)
```
