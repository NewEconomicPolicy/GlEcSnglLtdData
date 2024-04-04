l1 = list([1,2,3])

l2 = list([1,2,3])

l3 = [val1 + val2 for val1, val2 in zip(l1,l2)]

import shapefile as pyshp
shp_file = 'E:\\GlobalEcosseData\\World_GADM\\gadm28.shp'
shp_file = 'E:\\GlobalEcosseData\\World_borders\\world_country_boundaries.shp'
shp_file = 'E:\\GlobalEcosseData\\World_GADM\\Vault\\gadm28_adm1.shp'
shp_rdr = pyshp.Reader(shp_file)
# bbox = shp_rdr.bbox
# flds = shp_rdr.fields
shpes = shp_rdr.shapes()

recs = shp_rdr.records()
nrecs = len(recs); nshpes = len(shpes)

for ic, rec in enumerate(recs):
    if rec[3].find('nited King') >= 0:
        print('{} {}'.format(ic,rec))