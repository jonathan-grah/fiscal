import requests
import json
import math

import db.tables

countries = []


def add(country):
    # TODO: If tables don't exist, don't crash application
    row = db.tables.country.insert().values(country)
    db.tables.engine.execute(row)

    if country["knoemaKey"]:
        countries.append(country["knoemaKey"])


def grabCountryData():
    # knoemaKey refers to the subject key used by the API desc is used as a quick reference for devs to understand
    # which key equals which indicator (this should be moved somewhere else)

    indicators = [
        {
            "knoemaKey": 1000430,
            "desc": "unemploymentRate"
        },
        {
            "knoemaKey": 1000230,
            "desc": "inflationPercentChange"
        },
        {
            "knoemaKey": 1000340,
            "desc": "exportsVolumePercentChange"
        }
    ]

    if countries:
        commaDividedCountries = ",".join(map(str, countries))
        commaDividedIndicators = ",".join(map(str, indicators))

        # request = requests.get(f"http://knoema.com/api/1.0/data/IMFWEO2019Oct?Subject=1000430,1000230,1000340&Country={commaDividedCountries}&Time=2019")
        #
        # if request.status_code == 403:
        #     return print("Rate limiting has caused this request to fail")
        #     # should alert the user via gui alert?
        #     # this could maybe be a modular system that links in with reminder kind of system?
        #     # - would however be different to a modal type system that would be more like a completely separate interface
        #
        # data = request.json()

        # I am temporarily using a test json file, which is a mock response from the server (the server has rate
        # limiting so this is easier for dev)

        with open("test_data.json") as json_file:
            data = json.load(json_file)
            # TODO: need to add error checking for opening json file

            countryMembers = data["keys"]["stub"][0]["members"]
            indicatorMembers = data["keys"]["stub"][1]["members"]

            # the API will return each subject in order for each country in order
            # e.g. country1-subject1 country1-subject2, country2-subject1 country2-subject2

            # for each country requested, go through each subject
            for country in range(1, len(countryMembers) + 1):

                overallIndex = (country * len(indicatorMembers)) - len(indicatorMembers)

                for indicator in range(0, len(indicatorMembers)):
                    row = db.tables.indicator.insert().values({
                        "countryRegionId": data["data"][overallIndex]["RegionId"],
                        "value": data["data"][overallIndex]["Value"],
                        "indicatorTypeId": indicators[indicator]["knoemaKey"]
                    })

                    db.tables.engine.execute(row)

                    overallIndex += 1