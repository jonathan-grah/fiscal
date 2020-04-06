import requests
import db.tables


def createIndicatorTypes():
    print("Creating indicator types")

    request = requests.get(f"http://knoema.com/api/1.0/meta/dataset/IMFWEO2019Oct/dimension/subject")

    if request.status_code == 403:
        return print("Rate limiting has caused this request to fail")
        # should alert the user via gui alert?
        # this could maybe be a modular system that links in with reminder kind of system?
        # - would however be different to a modal type system that would be more like a completely separate interface

    data = request.json()

    for indicatorType in data["items"]:
        row = db.tables.indicatorType.insert().values({
            "knoemaKey": indicatorType["key"],
            "name": indicatorType["fields"]["subject-descriptor"],
            "description": indicatorType["fields"]["subject-notes"]
        })

        db.tables.engine.execute(row)
