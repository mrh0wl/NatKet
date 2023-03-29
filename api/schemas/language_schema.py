from typing import List, Optional
from djantic import ModelSchema
from pydantic import Field
from .media_schema import CoverSchema
from api.models import Language, LanguageSupport, LanguageTitle, AlternativeTitle, SupportType


class LanguageSchema(ModelSchema):
    class Config:
        model = Language
        exclude = ['languagesupport_set']


Languages = List[LanguageSchema]


class SupportTypeSchema(ModelSchema):
    class Config:
        model = SupportType
        exclude = ['languagesupport_set']


class AlternativeTitleSchema(ModelSchema):
    class Config:
        model = AlternativeTitle
        exclude = ['game']


class LanguageTitleSchema(ModelSchema):
    class Config:
        model = LanguageTitle
        exclude = ['languagesupport']


LanguageTitles = List[LanguageTitleSchema]


class LanguageSupportSchema(ModelSchema):
    id: int = Field(example=1)
    cover: Optional[CoverSchema]
    support_types: Optional[List[SupportTypeSchema]]
    language: Optional[LanguageSchema]
    language_titles: LanguageTitles

    class Config:
        model = LanguageSupport
        exclude = ['game']
