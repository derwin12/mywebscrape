from datetime import datetime

from app import Sequence, Vendor, db


def insert_sequence(store, url, name):
    vendor = Vendor.query.filter(Vendor.name == store).first()
    sequence = Sequence(name=name, link=url, vendor_id=vendor.id, last_updated=datetime.now())
    print("Adding %s" % sequence.name)
    Sequence.query.filter(Sequence.link == url and Sequence.vendor_id == vendor.id).delete()
    db.session.add(sequence)
    db.session.commit()
