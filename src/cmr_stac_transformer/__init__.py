""" cmr_stac_transformer """

__version__ = "0.0.1"

from typing import Optional
from pydantic import BaseModel
import pystac
from datetime import datetime

class RelatedUrls(BaseModel):
    Description: Optional[str]
    URLContentType: str
    Type: str
    Subtype: Optional[str]
    URL: str

class SpatialExtent(BaseModel):
    HorizontalSpatialDomain: Optional[dict]
    SpatialCoverageType: Optional[str]
    ResolutionAndCoordinateSystem: Optional[dict]
    GranuleSpatialRepresentation: Optional[str]

    def bounding_rectangles(self):
        bounding_rectangles = self.HorizontalSpatialDomain['Geometry']['BoundingRectangles'][0]
        return [[
            bounding_rectangles['WestBoundingCoordinate'],
            bounding_rectangles['SouthBoundingCoordinate'],
            bounding_rectangles['EastBoundingCoordinate'],
            bounding_rectangles['NorthBoundingCoordinate']
        ]]

class CmrDateRange(BaseModel):
    BeginningDateTime: datetime
    EndingDateTime: Optional[datetime]

class TemporalExtents(BaseModel):
    RangeDateTimes: list[CmrDateRange]

class CmrUmmJsonCollection(BaseModel):
    ShortName: str
    EntryTitle: str
    Abstract: str
    RelatedUrls: list[RelatedUrls]
    SpatialExtent: SpatialExtent
    TemporalExtents: list[TemporalExtents]

def transform(collection: CmrUmmJsonCollection, stac_root = ''):
    temporal_interval = [
        collection.TemporalExtents[0].RangeDateTimes[0].BeginningDateTime,
        collection.TemporalExtents[0].RangeDateTimes[0].EndingDateTime
    ]
    extent = pystac.Extent(
        spatial = pystac.SpatialExtent(bboxes = collection.SpatialExtent.bounding_rectangles()),
        temporal = pystac.TemporalExtent(intervals = temporal_interval)
    )
    stac_collection = pystac.Collection(
        id = collection.ShortName,
        title = collection.EntryTitle,
        description = collection.Abstract,
        extent = extent,
        href = f'{stac_root}/stac/collections/{collection.ShortName}'
    )
    for cmr_link in [collection.RelatedUrls[0]]:
        print(cmr_link)
        stac_collection.add_link(
            pystac.Link(
                target = cmr_link.URL,
                rel = cmr_link.URLContentType
            )
        )
    return stac_collection
