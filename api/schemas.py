from pydantic import BaseModel


class MetaResponse(BaseModel):
    total_rows: int
    total_columns: int
    columns: list[str]
    source_file: str
    source_kind: str
    integrity: str
    note: str
    kg_nodes_available: bool
    kg_edges_available: bool
    geo_lookup_available: bool

