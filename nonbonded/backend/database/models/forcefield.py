from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Query

from nonbonded.backend.database.models import Base, UniqueMixin


class Parameter(UniqueMixin, Base):

    __tablename__ = "parameters"

    id = Column(Integer, primary_key=True, index=True)

    handler_type = Column(String, nullable=False)
    smirks = Column(String, nullable=False)
    attribute_name = Column(String, nullable=False)

    @classmethod
    def unique_hash(cls, handler_type, smirks, attribute_name):
        return handler_type, smirks, attribute_name

    @classmethod
    def unique_filter(cls, query: Query, handler_type, smirks, attribute_name):
        return (
            query.filter(Parameter.handler_type == handler_type)
            .filter(Parameter.smirks == smirks)
            .filter(Parameter.attribute_name == attribute_name)
        )


class ForceField(UniqueMixin, Base):

    __tablename__ = "force_fields"

    id = Column(Integer, primary_key=True, index=True)
    inner_content = Column(String, nullable=False)

    @classmethod
    def unique_hash(cls, inner_content):
        return inner_content

    @classmethod
    def unique_filter(cls, query: Query, inner_content):
        return query.filter(ForceField.inner_content == inner_content)
