#!/usr/bin/env python3

import pdb

import datetime
from bs4 import BeautifulSoup

def main():
    with open("grants-2000-to-2007.html", "r") as f:
        soup = BeautifulSoup(f, "lxml")
        for td in soup.find_all("td"):
            if td == "\n" or not td.text:
                continue
            date = ""
            grantee = ""
            program = ""
            amount = ""
            website = ""
            purpose = ""
            l = list(map(str.strip, filter(bool, td.text.split("\n"))))
            for i in l:
                try:
                    test_date = datetime.datetime.strptime(i, "%B %Y")
                    assert not date, (date, i)
                    date = test_date
                except ValueError:
                    pass
                if date:
                    continue
                if i.startswith("www."):
                    assert not website
                    website = i
                elif i.startswith("To "):
                    assert not purpose
                    purpose = i
                elif i.startswith("$"):
                    assert not amount
                    amount = i
                elif program:
                    assert not grantee, (grantee, i)
                    grantee = i
                else:
                    assert not program, (program, i)
                    program = i


if __name__ == "__main__":
    main()
