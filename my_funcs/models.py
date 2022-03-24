from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

Base = declarative_base()
metadata = MetaData()

sequence_vendor = Table(
    "sequence_vendor",
    metadata,
    Column("id", Integer, ForeignKey("sequence.id")),
    Column("vendor_id", Integer, ForeignKey("vendor.id")),
)

vendor_urls = Table(
    "vendor_urls",
    metadata,
    Column("id", Integer, ForeignKey("vendor.id")),
    Column("vendor_id", Integer, ForeignKey("vendor.id")),
)


class Vendor(Base):
    __tablename__ = "vendor"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    baseurls = Column(String)


class Urls(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True)
    url = Column(String)
    vendor_id = Column(Integer, ForeignKey("vendor.id"))


class Sequence(Base):
    __tablename__ = "sequence"
    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey("vendor.id"))
    title = Column(String)
