#!/usr/bin/env python3

import pdb

import datetime
from bs4 import BeautifulSoup


def mysql_quote(x):
    """Quote the string x using MySQL quoting rules. If x is the empty string,
    return "NULL". Probably not safe against maliciously formed strings, but
    our input is fixed and from a basically trustable source."""
    if not x:
        return "NULL"
    x = x.replace("\\", "\\\\")
    x = x.replace("'", "''")
    x = x.replace("\n", "\\n")
    return "'{}'".format(x)


def main():
    print("""insert into donations (donor, donee, amount, donation_date,
    donation_date_precision, donation_date_basis, cause_area, url,
    donor_cause_area_url, notes, affected_countries, affected_states,
    affected_cities, affected_regions) values""")

    first = True

    with open("grants-2000-to-2007.html", "r") as f:
        soup = BeautifulSoup(f, "lxml")
        for td in soup.find_all("td"):
            if td == "\n" or not td.text:
                continue
            if td.text.startswith("FOCUS AREA: "):
                focus_area = td.text[len("FOCUS AREA: "):]
            date = ""
            grantee = ""
            program = ""
            amount = ""
            website = ""
            purpose = ""

            # The goal is that each time we go around this loop, we set exactly
            # one of the unset variables from above (date, grantee, program, etc.).
            # The tricky thing about the source table is that each cell can
            # contain a variable number of lines, so we can't just say "the
            # first thing is a date, the next thing is a program, and so on".
            # In other words, we have to inspect the content of each line to
            # see which variable should be set.
            for i in map(str.strip, filter(bool, td.text.split("\n"))):
                print("DEBUG:", i)
                try:
                    test_date = datetime.datetime.strptime(i, "%B %Y").strftime("%Y-%m-%d")
                    assert not date, (date, i)
                    date = test_date
                    continue
                except ValueError:
                    pass
                if i.startswith("www.") or i in ["usi.uchicago.edu", "cns.utexas.edu"]:
                    assert website in ["www.insureakid.org", "www.secondharvest.org"] or not website, (website, i)
                    website = i
                elif i.startswith("To ") or i.startswith("A gift to ") or i.startswith("In support of ") or i.startswith("Funds provided to "):
                    assert not purpose
                    purpose = i
                elif i.startswith("$"):
                    assert not amount
                    amount = i
                    amount = amount.replace("$", "").replace(",", "")
                    assert int(amount)
                    print("DEBUG2:", i)
                # In the HTML, the program is listed first, then the grantee
                # (for grants that list both a program and grantee), so set the
                # grantee only if program is already set.
                elif program:
                    assert not grantee, (grantee, i)
                    grantee = i
                else:
                    assert not program, (program, i)
                    program = i
            print(("    " if first else "    ,") + "(" + ",".join([
                mysql_quote("Michael & Susan Dell Foundation"),  # donor
                mysql_quote(grantee),  # donee
                amount,  # amount
                mysql_quote(date),  # donation_date
                mysql_quote("month"),  # donation_date_precision
                mysql_quote("donation log"),  # donation_date_basis
                mysql_quote(focus_area),  # cause_area
                mysql_quote(website),  # url
                mysql_quote("FIXME"),  # donor_cause_area_url
                mysql_quote(program + "###" + purpose),  # notes
                mysql_quote(""),  # affected_countries
                mysql_quote(""),  # affected_states
                mysql_quote(""),  # affected_cities
                mysql_quote(""),  # affected_regions
            ]) + ")")
            first = False
        print(";")


if __name__ == "__main__":
    main()
