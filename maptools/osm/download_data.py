import os
import shapefile
from OSMPythonTools.api import Api
from OSMPythonTools.overpass import Overpass
from input import osmIDs

# Ukraine: Україна

osmIDs = osmIDs[:3000]
overpass = Overpass()
#result = overpass.query('area[name = "Україна"];way(area)["highway"~"^(motorway|trunk|primary|secondary)$"]; out;', timeout=10000)
result = overpass.query('area[name = "Україна"];(way(area)["highway"~"^(motorway|trunk|primary|secondary)$"]; >;);', timeout=10000)

for element in result.elements():
    print(element.tag('name'))

exit()


query = "way(id:"
i = 0
for way_id in osmIDs:
    query += f"{way_id}, "
    i += 1
    if i % 1000 == 0 or i == len(osmIDs):
        query = query[:-2]
        query += "); out tags;"
        result = overpass.query(query)
        for element in result.elements():
            print(element.tag('name'))
        query = "way(id:"


exit()
from input import (
    osmIDs,
)  # input.py file in the same folder that just contains "osmIDs = [111111, 22223232, ...] "


# sorted list as given
# interesting_columns = ["osm_id", "smoothness", "highway", "bridge", "maxspeed", "maxheight", "maxaxleload", "lanes", "layer", "surface", "bicycle", "oneway", "name", "name:en", "name:uk", "name:ru", "lit", "destinatio", "destinatio_1", "destinatio_2", "destinatio_3", "destinatio_4", "destinatio_5", "turn:lanes", "highway:cl", "old_ref", "ref", "int_ref", "nat_ref", "hgv", "source:max", "highway:ca", "source:max_1", "placement", "embankment", "changeset", "timestamp", "user", "uid"]

# list with no tags
# interesting_columns = ["osm_id", "changeset", "timestamp", "user", "uid"]

# list of all currently interesting tags
interesting_columns = [
    "osm_id",
    "smoothness",
    "highway",
    "bridge",
    "maxspeed",
    "maxheight",
    "maxaxleload",
    "lanes",
    "layer",
    "surface",
    "bicycle",
    "oneway",
    "name",
    "name:en",
    "name:uk",
    "name:ru",
    "lit",
    "destination",
    "destination:en",
    "destination:symbol",
    "destination:int_ref",
    "destination:ref",
    "destination:lang:en",
    "turn:lanes",
    "highway:class:pl",
    "highway:category:pl",
    "old_ref",
    "int_ref",
    "source:maxspeed",
    "placement",
    "hgv",
    "source:maxaxleload",
    "nat_ref",
    "ref",
    "embankment",
    "changeset",
    "timestamp",
    "user",
    "uid",
]

# as shapefiles only support 10 character column names, replace some tag names accordingly
REPLACEMENTS = {
    ":": "_",
    "destination": "dst",
    "maxaxleload": "axlld",
    "maxspeed": "maxv",
    "class": "cls",
    "highway": "hw",
    "category": "cat",
    "source": "src",
    "_ref": "_rf",
    "_lang": "lng",
}


class Progress:
    """simple class to display current progress downloading data"""

    def __init__(self, totalIDs):
        self.i = 0
        self.totalIDs = totalIDs
        self.stepsToDisplayCount = max(min(500, int(totalIDs / 20)), 1)

    def update(self):
        self.i += 1
        if self.i % self.stepsToDisplayCount == 0:
            print(f"{self.i} / {self.totalIDs} IDs downloaded")


api = Api()

unable_to_download = set()  # here, all IDs that could not be downloaded will be stored


def query_osm(way_id):
    """returns way object or None if not found"""
    global unable_to_download
    try:
        way = api.query(f"way/{way_id}")
        return way
    except:
        unable_to_download.add(way_id)
        return None


def get_all_fields(ids):
    """returns a list of all fields (that are present in at least one of the given IDs)"""
    all_tag_fiels = set()

    prgs = Progress(len(ids))
    for current_id in ids:
        prgs.update()
        way = query_osm(current_id)
        if way is None:
            continue

        # print(way.tag('name'))
        all_tags = way.tags()
        for tag_name in all_tags:
            all_tag_fiels.add(tag_name)

    all_fields = ["osm_id"]
    all_fields.extend(list(all_tag_fiels))
    all_fields.extend(["changeset", "timestamp", "user", "uid"])
    return all_fields


def append_fields_not_in_sorted_list():
    """promps user if tags not in interesting_columns list should be appended to output as well"""
    all_fields = get_all_fields(osmIDs)

    fields_not_in_sorted_list = [
        field for field in all_fields if field not in interesting_columns
    ]
    if len(fields_not_in_sorted_list) == 0:
        return all_fields
    print("------------------")
    print(
        "These fields were not in the previous sorted list (interesting_columns), should they be appended?"
    )
    print(fields_not_in_sorted_list)
    append_fields = "Y" # input("Append new fields (Y/n)?")
    append_fields = append_fields == "" or append_fields == "Y" or append_fields == "y"

    if append_fields:
        all_fields = interesting_columns[:-4]
        all_fields.extend(list(fields_not_in_sorted_list))
        all_fields.extend(["changeset", "timestamp", "user", "uid"])
    else:
        all_fields = interesting_columns
    return all_fields


# all_fields = [osm_id, *[tags fields], "changeset", "timestamp", "user", "uid"]
all_fields = append_fields_not_in_sorted_list()

# sort all tag fields:
# all_fields = [osm_id, *[tags sorted alphabetically], "changeset", "timestamp", "user", "uid"]
all_tag_fields = all_fields[1:-4]
all_tag_fields.sort()
all_fields = ["osm_id"] + all_tag_fields + ["changeset", "timestamp", "user", "uid"]


def get_column_name(field_name):
    """returns 10 character names (limit of shp files) for fields"""
    for replacement in REPLACEMENTS:
        field_name = field_name.replace(replacement, REPLACEMENTS[replacement])
    if len(field_name) > 10:
        print(f"WARNING: Field name too long: {field_name}")
    return field_name


w = shapefile.Writer("./infos")
w.fields = []
new_field_names = [get_column_name(field) for field in all_fields]
for field_name in new_field_names:
    w.field(field_name, "C", "200")  # replace all : by _


# give user some feedback on where we are in the list
i = 0
stepsToDisplayCount = max(min(500, int(len(osmIDs) / 20)), 1)
prgs = Progress(len(osmIDs))
for current_id in osmIDs:
    prgs.update()

    way = query_osm(current_id)
    if way is None:
        continue

    # print(way.tag('name'))
    all_tags = way.tags()
    # print(all_tags["maxaxleload"])

    polyline_coords = []
    for node in way.nodes():
        coordinates = node.geometry()["coordinates"]
        polyline_coords.append(coordinates)

    w.line([polyline_coords])
    all_records = [current_id]
    all_records.extend(
        [
            all_tags[tagName] if tagName in all_tags else None
            for tagName in all_tag_fields
        ]
    )
    all_records.extend(
        [str(way.changeset()), str(way.timestamp()), str(way.user()), str(way.uid())]
    )
    w.record(*all_records)

print()
print("-----------------------------------------")
print("--------------- Summary -----------------")
print("-----------------------------------------")
print(f"Successfully downloaded data of {len(osmIDs) - len(unable_to_download)} IDs")
if len(unable_to_download) == 0:
    print("Was able to download all IDs!")
else:
    print(f"Was not able to download {unable_to_download}")
print("Done!")
w.close()
