from datetime import datetime
from typing import Annotated, Literal
from pydantic import BaseModel, Field, field_validator, model_validator

class Concept(BaseModel):
    id: str = Field(min_length=1, max_length=100)
    label: str = Field(min_length=1, max_length=100)
    kind: Literal["thing", "time"]
    synonyms: list[str] = Field(default_factory=list, max_length=50)
    year: int | None = Field(default=None, ge=1900, le=2099)
    month: int | None = Field(default=None, ge=1, le=12)

class TimeFilter(BaseModel):
    facet: Literal["when"]
    level: Literal["year", "month", "day"]
    label: str
    start: str
    end: str

    @model_validator(mode="after")
    def valid_range(self):
        start, end = datetime.fromisoformat(self.start), datetime.fromisoformat(self.end)
        if start.tzinfo or end.tzinfo or start >= end:
            raise ValueError("Use a valid timezone-free date range")
        return self

class ValueFilter(BaseModel):
    facet: Literal["who", "also"]
    value: str
    label: str

Filter = Annotated[TimeFilter | ValueFilter, Field(discriminator="facet")]

class SearchRequest(BaseModel):
    query: str = Field(default="", max_length=300)
    removed_concept_ids: list[str] = Field(default_factory=list, max_length=50)
    concept_overrides: list[Concept] = Field(default_factory=list, max_length=50)
    filters: list[Filter] = Field(default_factory=list, max_length=50)
    hints_on: bool = True
    want_drop: bool = False

class PhotoCard(BaseModel):
    id: str
    thumb_url: str
    taken_at: str | None
    tag_status: Literal["tagged"] = "tagged"

class PhotoDetail(PhotoCard):
    full_url: str
    date_source: Literal["manual"] = "manual"
    city: str
    setting: str
    caption: str
    people_names: list[str]

class HintValue(BaseModel):
    label: str
    count: int
    thumb_url: str
    filter: Filter

class HintRow(BaseModel):
    facet: Literal["when", "who", "also"]
    label: str
    values: list[HintValue]

class RemoveConcept(BaseModel):
    type: Literal["remove_concept"]
    concept_id: str

class RemoveFilter(BaseModel):
    type: Literal["remove_filter"]
    index: int

class ReplaceConcept(BaseModel):
    type: Literal["replace_concept"]
    concept_id: str
    with_: Concept = Field(alias="with")

class DropOption(BaseModel):
    kind: Literal["drop", "nearest"]
    label: str
    count: int
    action: Annotated[RemoveConcept | RemoveFilter | ReplaceConcept, Field(discriminator="type")]

class SearchResponse(BaseModel):
    concepts: list[Concept]
    n_results: int
    results: list[PhotoCard]
    hints: list[HintRow]
    drop: list[DropOption]
    untagged_count: int = 0
    message: str | None = None
