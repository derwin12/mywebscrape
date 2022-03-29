from datetime import datetime

from app import Sequence, Vendor, db


def insert_sequence(store, url, name):
    vendor = Vendor.query.filter(Vendor.name == store).first()
    sequence = Sequence(name=name, link=url, vendor_id=vendor.id, last_updated=datetime.now())
    print("Adding %s" % sequence.name)
    seq = Sequence.query.filter(Sequence.link == url and Sequence.vendor_id == vendor.id).first()
    Sequence.query.filter(Sequence.link == url and Sequence.vendor_id == vendor.id).delete()
    if seq and seq.first_seen:
        sequence.first_seen = seq.first_seen
    else:
        sequence.first_seen = datetime.now()
    db.session.add(sequence)
    db.session.commit()
