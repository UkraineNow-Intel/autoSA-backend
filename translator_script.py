import shapefile
from OSMPythonTools.api import Api

from maptools.translator import Translator, get_file_with_extensions

translator = Translator()

# file_name = "./Data/motorway_gis_osm_roads.shp"
file_name = get_file_with_extensions()

api = Api()

sf = shapefile.Reader(file_name)
records = sf.records()

w = shapefile.Writer("./Export/tests")
w.fields = list(sf.fields)
w.field("translate", "C", "200")
i = 0

for shaperec in sf.iterShapeRecords():
    # for record in records:
    record = shaperec.record
    print(record["osm_id"])

    way = api.query("way/" + record["osm_id"])
    # if record does not have a name -> get from OSM

    if way.tag("name:uk") or way.tag("name:ru"):
        print(way.tag("name"))
        print(way.tag("name:en"))
        print(way.tag("name:ru"))
        print(way.tag("name:uk"))

        # if record has a name in uk or ru -> translate to en
        translation = ""
        if way.tag("name:uk"):
            translation = translator.translate(way.tag("name:uk"), "uk")
        elif way.tag("name:ru"):
            translation = translator.translate(way.tag("name:ru"), "ru")
        print("Translation", translation)

        # copy to output file
        w.record(*shaperec.record, translation)
        w.shape(shaperec.shape)
    else:  # if entry does not have a name, still copy to output file
        w.record(*shaperec.record)
        w.shape(shaperec.shape)
    print("-------")

w.close()

translator.save_translation_cache()
