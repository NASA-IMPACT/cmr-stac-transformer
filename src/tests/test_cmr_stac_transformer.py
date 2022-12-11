import json
import os
import cmr_stac_transformer
import pystac

# Opening JSON file
filename = 'C1908348134-LPDAAC_ECS.umm_json'
dir_path = os.path.dirname(os.path.realpath(__file__))
f = open(f'{dir_path}/../examples/{filename}')
  
# returns JSON object as 
# a dictionary
data = json.load(f)
f.close()
collection = data['items'][0]['umm']

collection_instance = cmr_stac_transformer.CmrUmmJsonCollection(**collection)

def test_basic_fields():
    assert(collection_instance.ShortName == 'GEDI02_A')
    assert(collection_instance.EntryTitle == 'GEDI L2A Elevation and Height Metrics Data Global Footprint Level V002')
    abstrat = 'The Global Ecosystem Dynamics Investigation (GEDI) mission aims to characterize ecosystem structure and dynamics to enable radically improved quantification and understanding of the Earth’s carbon cycle and biodiversity. The GEDI instrument produces high resolution laser ranging observations of the 3-dimensional structure of the Earth. GEDI is attached to the International Space Station (ISS) and collects data globally'
    assert(abstrat in collection_instance.Abstract)

def test_related_urls():
    assert(len(collection_instance.RelatedUrls) == 17)
    related_url = collection_instance.RelatedUrls[0]
    assert(related_url.Description == 'Earthdata Search allows users to search, discover, visualize, refine, and access NASA Earth Observation data.')
    assert(related_url.URLContentType == 'DistributionURL')
    assert(related_url.Type == 'GET DATA')
    assert(related_url.Subtype == 'Earthdata Search')
    assert(related_url.URL == 'https://search.earthdata.nasa.gov/search?q=C1908348134-LPDAAC_ECS')

stac_instance = cmr_stac_transformer.transform(collection_instance)

def test_basic_transform():
    assert(type(stac_instance) == pystac.Collection)

def test_extents():
    assert(stac_instance.extent.spatial.bboxes == [[-180, -90, 180, 90]])
    assert(stac_instance.extent.temporal.intervals[0][0].strftime('%Y-%m-%dT%H:%M:00.000Z') == "2019-03-25T00:00:00.000Z")

def test_links():
    # The first link is to self
    assert(stac_instance.links[0].target == stac_instance)
    assert(stac_instance.links[0].rel == 'root')    
    assert(stac_instance.links[1].target == '/stac/collections/GEDI02_A')
    assert(stac_instance.links[1].rel == 'self')
    assert(stac_instance.links[2].target == 'https://search.earthdata.nasa.gov/search?q=C1908348134-LPDAAC_ECS')
    assert(stac_instance.links[2].rel == 'DistributionURL')

def test_valid():
    assert(pystac.validation.validate(stac_instance))

    