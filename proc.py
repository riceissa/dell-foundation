#!/usr/bin/env python3

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
    locations = {'India', 'South Africa', 'United States', 'Central Texas'}

    with open("data.html", "r") as f:
        soup = BeautifulSoup(f, "lxml")

        for tr in soup.find_all("tr"):
            tds = tr.find_all("td")
            divs = tds[0].find_all("div")

            program = divs[0].text.strip()
            grant_url = "https://www.msdf.org" + divs[0].find("a").get("href").strip()
            grantee = divs[1].text.strip()

            amount = tds[1].text.strip()
            assert amount.startswith("$"), amount
            amount = amount.replace("$", "").replace(",", "")
            assert int(amount)

            location = tds[2].text.strip()
            assert location in locations
            affected_countries = ""
            affected_states = ""
            affected_regions = ""
            if location in ["United States", "India", "South Africa"]:
                affected_countries = location
            if location == "Central Texas":
                affected_countries = "United States"
                affected_states = "Texas"
                affected_regions = location

            print(("    " if first else "    ,") + "(" + ",".join([
                mysql_quote("Michael & Susan Dell Foundation"),  # donor
                mysql_quote(grantee),  # donee
                amount,  # amount
                mysql_quote(""),  # donation_date
                mysql_quote(""),  # donation_date_precision
                mysql_quote(""),  # donation_date_basis
                mysql_quote("FIXME"),  # cause_area
                mysql_quote(grant_url),  # url
                mysql_quote("FIXME"),  # donor_cause_area_url
                mysql_quote("For " + program + "."),  # notes
                mysql_quote(affected_countries),  # affected_countries
                mysql_quote(affected_states),  # affected_states
                mysql_quote(""),  # affected_cities
                mysql_quote(affected_regions),  # affected_regions
            ]) + ")")
            first = False
        print(";")


if __name__ == "__main__":
    main()
