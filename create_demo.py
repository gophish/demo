from faker import Faker
from aiosmtpd.handlers import Sink
from aiosmtpd.controller import Controller
from os import sys

from gophish import Gophish
from gophish.models import *

import random
import requests
import urllib3
import time
import argparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

faker = Faker()

DEFAULT_USER_AGENT = 'Gophish Test Data Generator'

DEFAULT_TEMPLATE_HTML = '''<html>
    <head></head>
    <body>
        <p>{{.FirstName}},</p>
        <p>Please click <a href="{{.URL}}">this link</a> to reset your
        password.</p>
        {{.Tracker}}
    </body>
</html>
'''

DEFAULT_TEMPLATE_TEXT = 'Default template text'
DEFAULT_LANDING_PAGE_HTML = '''<html>
    <head></head>
    <body>
    Please sign in below
    <form action="" method="POST">
        <input name="username" type="text" placeholder="username"/>
        <input name="password" type="password"/>
    </form>
    </body>
</html>
'''


def generate_groups(api, num_groups=10, num_members=100):
    """Generates groups with randomly created targets using the Gophish API

    Each target has a randomly generated first and last name. The email address
    for the target is in first.last@example.com format.

    This returns the names of the created groups, *not* the full Group objects
    to save memory.

    Arguments:
        api {gophish.API} -- The authenticated Gophish API client

    Keyword Arguments:
        num_groups {int} -- [description] (default: {10})
        num_members {int} -- [description] (default: {100})
    """
    group_names = []
    for group_idx in range(0, num_groups):
        targets = []
        for target_idx in range(0, num_members):
            first_name = faker.first_name()
            last_name = faker.last_name()
            email = '{}.{}@example.com'.format(first_name, last_name)
            targets.append(
                User(first_name=first_name, last_name=last_name, email=email))
        group = Group(name='Test Group {}'.format(group_idx), targets=targets)
        try:
            group = api.groups.post(group)
        except Exception as e:
            print('Unable to post group: {}'.format(e))
            break
        group_names.append(group.name)
    return group_names


def generate_sending_profile(api, host):
    """Generates a new sending profile

    Arguments:
        api {gophish.API} -- The authenticated Gophish API client
        host {str} -- The host:port for the SMTP server

    Returns:
        gophish.models.SMTP -- The created sending profile
    """
    sending_profile = SMTP(
        name='Test Sending Profile',
        host=host,
        from_address='Example Sender <foo@example.com>')
    try:
        sending_profile = api.smtp.post(sending_profile)
    except Exception as e:
        print('Unable to create sending profile: {}'.format(e))
    return sending_profile


def generate_template(api,
                      text=DEFAULT_TEMPLATE_TEXT,
                      html=DEFAULT_TEMPLATE_HTML):
    """Creates a new email template

    Arguments:
        api {gophish.API} -- The authenticated Gophish API client

    Keyword Arguments:
        text {str} -- The email template text (default: {DEFAULT_TEMPLATE_TEXT})
        html {str} -- The email template HTML (default: {DEFAULT_TEMPLATE_HTML})

    Returns:
        gophish.models.Template -- The created template
    """
    template = Template(name='Example Template', text=text, html=html)
    try:
        template = api.templates.post(template)
    except Exception as e:
        print('Unable to create template: {}'.format(e))
    return template


def generate_landing_page(api, html=DEFAULT_LANDING_PAGE_HTML):
    """Generates a new landing page.

    Arguments:
        api {gophish.API} -- The authenticated Gophish API client

    Keyword Arguments:
        html {str} -- The landing page HTML (default: {DEFAULT_LANDING_PAGE_HTML})

    Returns:
        gophish.models.Page -- The created landing page
    """
    landing_page = Page(name='Example Landing Page', html=html)
    try:
        landing_page = api.pages.post(landing_page)
    except Exception as e:
        print('Unable to create landing page: {}'.format(e))
    return landing_page


def generate_results(api,
                     campaign,
                     percent_opened=50,
                     percent_clicked=20,
                     percent_submitted=5,
                     percent_reported=20):
    """Generates campaign events

    Arguments:
        api {gophish.API} -- The authenticated Gophish API client
        campaign {gophish.models.Campaign} -- The created campaign

    Keyword Arguments:
        percent_opened {int} -- The percent of emails to open (default: {50})
        percent_clicked {int} -- The percent of links to click (default: {20})
        percent_submitted {int} -- The percent of form submissions (default: {5})
        percent_reported {int} -- The percent of emails to report (default: {20})
    """
    for result in campaign.results:
        # Create a "device" for this user
        user_agent = faker.user_agent()
        # Handle the email open events
        should_open = random.randint(0, 100)
        if should_open <= percent_opened:
            open_email(campaign, result, user_agent=user_agent)
            # Handle the link clicked events
            should_click = random.randint(0, 100)
            if should_click <= percent_clicked:
                click_link(campaign, result, user_agent=user_agent)
                # Handle the submissions events
                should_submit = random.randint(0, 100)
                if should_submit <= percent_submitted:
                    submit_data(campaign, result, user_agent=user_agent)
        # Handle the reported events
        should_report = random.randint(0, 100)
        if should_report <= percent_reported:
            report_email(campaign, result, user_agent=user_agent)


def open_email(campaign, result, user_agent=DEFAULT_USER_AGENT):
    """Generates an email opened event

    Arguments:
        campaign {gophish.models.Campaign} -- The campaign to generate the 
            event for
        result {gophish.models.Result} -- The result to generate the event for 

    Keyword Arguments:
        user_agent {str} -- The user agent used to generate the event 
            (default: {DEFAULT_USER_AGENT})

    Returns:
        requests.Response -- The response object for the HTTP request used to
            create the event
    """
    print('Opening email for {}'.format(result.email))
    sys.stdout.flush()
    return requests.get(
        '{}/track'.format(campaign.url),
        params={'rid': result.id},
        headers={'User-Agent': user_agent})


def click_link(campaign, result, user_agent=DEFAULT_USER_AGENT):
    """Generates a clicked link event

    Arguments:
        campaign {gophish.models.Campaign} -- The campaign to generate the 
            event for
        result {gophish.models.Result} -- The result to generate the event for 

    Keyword Arguments:
        user_agent {str} -- The user agent used to generate the event 
            (default: {DEFAULT_USER_AGENT})

    Returns:
        requests.Response -- The response object for the HTTP request used to
            create the event
    """
    print('Clicking link for {}'.format(result.email))
    sys.stdout.flush()
    return requests.get(
        campaign.url,
        params={'rid': result.id},
        headers={'User-Agent': user_agent})


def submit_data(campaign, result, user_agent=DEFAULT_USER_AGENT):
    """Generates a data submission event

    Arguments:
        campaign {gophish.models.Campaign} -- The campaign to generate the 
            event for
        result {gophish.models.Result} -- The result to generate the event for 

    Keyword Arguments:
        user_agent {str} -- The user agent used to generate the event 
            (default: {DEFAULT_USER_AGENT})

    Returns:
        requests.Response -- The response object for the HTTP request used to
            create the event
    """
    print('Submitting data for {}'.format(result.email))
    sys.stdout.flush()
    return requests.post(
        campaign.url,
        params={'rid': result.id},
        data={
            'email': result.email,
            'password': faker.password()
        },
        headers={'User-Agent': user_agent})


def report_email(campaign, result, user_agent=DEFAULT_USER_AGENT):
    """Generates an email report event

    Arguments:
        campaign {gophish.models.Campaign} -- The campaign to generate the 
            event for
        result {gophish.models.Result} -- The result to generate the event for 

    Keyword Arguments:
        user_agent {str} -- The user agent used to generate the event 
            (default: {DEFAULT_USER_AGENT})

    Returns:
        requests.Response -- The response object for the HTTP request used to
            create the event
    """
    print('Reporting email for {}'.format(result.email))
    sys.stdout.flush()
    return requests.get(
        '{}/report'.format(campaign.url),
        params={'rid': result.id},
        headers={'User-Agent': user_agent})


def main():
    parser = argparse.ArgumentParser(
        description='Loads demo data into a Gophish instance',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--api-key', type=str, required=True, help='The Gophish API key')
    parser.add_argument(
        '--api-url',
        type=str,
        default='https://localhost:3333',
        help='The URL pointing to the Gophish admin server')
    parser.add_argument(
        '--phish-url',
        type=str,
        default='http://localhost',
        help='The URL pointing to the Gophish phishing server')
    parser.add_argument(
        '--num-groups',
        type=int,
        default=10,
        help='The number of groups to create')
    parser.add_argument(
        '--num-members',
        type=int,
        default=100,
        help='The number of recipients in each group')
    parser.add_argument(
        '--percent-opened',
        type=int,
        default=50,
        help='Percent of users to open the emails in the campaign')
    parser.add_argument(
        '--percent-clicked',
        type=int,
        default=20,
        help='Percent of users to click the links in the campaign')
    parser.add_argument(
        '--percent-submitted',
        type=int,
        default=5,
        help='Percent of users to submit data in the campaign')
    parser.add_argument(
        '--percent-reported',
        type=int,
        default=5,
        help='Percent of users to report the emails in the campaign')
    args = parser.parse_args()

    # Start our null SMTP server
    smtp = Controller(Sink(), hostname='127.0.0.1')
    smtp.start()
    api = Gophish(api_key=args.api_key, host=args.api_url, verify=False)

    # Generate our groups
    print('Generating Groups...')
    sys.stdout.flush()
    group_names = generate_groups(
        api, num_groups=args.num_groups, num_members=args.num_members)
    groups = [Group(name=group) for group in group_names]

    print('Generating SMTP')
    sys.stdout.flush()
    smtp = generate_sending_profile(api, '{}:{}'.format(
        smtp.hostname, smtp.port))

    print('Generating Template')
    sys.stdout.flush()
    template = generate_template(api)

    print('Generating Landing Page')
    sys.stdout.flush()
    landing_page = generate_landing_page(api)

    print('Generating Campaigns')
    sys.stdout.flush()
    campaign = Campaign(
        name='Demo Campaign',
        groups=groups,
        page=landing_page,
        template=template,
        smtp=smtp,
        url=args.phish_url)

    campaign = api.campaigns.post(campaign)
    # Wait for the emails to be received
    while True:
        summary = api.campaigns.summary(campaign_id=campaign.id)
        if summary.stats.sent < len(campaign.results):
            if summary.stats.error:
                print(
                    'Encountered an error... Check the Gophish logs for details.'
                )
                print('Exiting...')
                sys.exit(1)
            print(
                'Waiting for mock emails to finish sending (this takes a few seconds)...'
            )
            sys.stdout.flush()
            time.sleep(1)
            continue
        break

    generate_results(
        api,
        campaign,
        percent_opened=args.percent_opened,
        percent_clicked=args.percent_clicked,
        percent_submitted=args.percent_submitted,
        percent_reported=args.percent_reported)

    print(
        '\n\nAll set! You can now browse to {} to view the Gophish dashboard'.
        format(args.api_url))
    print('The credentials are admin:gophish')
    print('Enjoy!')


if __name__ == '__main__':
    main()
