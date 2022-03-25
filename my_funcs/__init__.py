from app import Sequence, Vendor, db


def insert_sequence(store, url, name):
    vendor = Vendor.query.filter(Vendor.name == store).first()
    sequence = Sequence(name=name, link=url, vendor_id=vendor.id)
    print("Adding %s" % sequence.name)
    Sequence.query.filter(Sequence.link == url).delete()
    db.session.add(sequence)
    db.session.commit()
