from fastapi import Query
from typing import List, Union

class convertToByTypeQueryParams:
    def __init__(
        self,
        type: str = Query(..., description="type: pdfToDoc | pdfToDocx | pdfToPPT | pdfToPPTX | pdfToExcel | wordToPdf | excelToPdf | pptToPdf | imageToPdf",  example="pdfToDocx"),
    ):
        self.type = type


class pdfDeletePagesQueryParams:
    def __init__(
        self,
        pages: str = Query(..., description="Array pages deleted",
                           example="1 or 1-3 or 1,2,3,4"),
    ):
        self.pages = pages


class pdfRotateQueryParams:
    def __init__(
        self,
        angle: str = Query(..., description="Rotate angle",
                           example="0 or 90 or -90 or 180"),
    ):
        self.angle = angle


class pdfSplitQueryParams:
    def __init__(
        self,
        ranges: str = Query(..., description="Array split ranges",  example="1,2-3,4,5-6"),
    ):
        self.ranges = ranges


class pdfSortQueryParams:
    def __init__(
        self,
        sorts: str = Query(..., description="Page sort",  example="1,2,3,4"),
    ):
        self.sorts = sorts


class pdfSignatureQueryParams:
    def __init__(
        self,
        page: str = Query(..., description="page",  example="1"),
        x: str = Query(..., description="x the points to define the bounding box (inch)",  example="0"),
        y: str = Query(..., description="y the points to define the bounding box (inch)",  example="0"),
    ):
        self.page = page
        self.x = x
        self.y = y
        
class listQueryParams:
    def __init__(
        self,
        page: str = Query(..., description="page",  example="1"),
        limit: str = Query(..., description="limit",  example="10"),
        search: Union[str, None] = Query(default=None),
    ):
        self.limit = limit
        self.page = page
        self.search = search