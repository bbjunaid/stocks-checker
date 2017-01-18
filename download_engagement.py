#!/usr/bin/env python

import gmail

from auth import GMAIL_USER, GMAIL_PASS
from const import ENGAGEMENT_FILE_PATH, CACHE_KEY_TREND, CACHE_EXPIRY_TIME
from stocks import r

def main():
    g = gmail.login(GMAIL_USER, GMAIL_PASS)
    engagement_emails = g.inbox().mail(sender='fitzstock2004@gmail.com')

    if len(engagement_emails) == 0:
        print "No engagement email"
        return

    latest = engagement_emails[-1]
    latest.fetch()

    trend = "NOTREND"
    if "*UPTREND*" in latest.body:
        trend = "UPTREND"
    if "*DOWNTREND*" in latest.body:
        trend = "DOWNTREND"

    r.set(CACHE_KEY_TREND, trend, CACHE_EXPIRY_TIME)

    for attachment in latest.attachments:
        if attachment.name == "engagement.xls":
            print "Saving {name}".format(name=attachment.name)
            attachment.save(ENGAGEMENT_FILE_PATH)
            return

    print "Could not find engagement.xls attachment"


if __name__ == "__main__":
    main()
