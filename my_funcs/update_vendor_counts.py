from app import Vendor, Sequence, db
from sqlalchemy import update

def main() -> None:
    print(f"Updating Vendor Sequence Counts")
    Vendors = Vendor.query.order_by(Vendor.name).all()

    for vendor in Vendors:
        SeqCount = Sequence.query.filter(Sequence.vendor_id == vendor.id).count()
        print("Vendor %s has %s sequences" % (vendor.name, SeqCount))
        stmt = update(Vendor).where(Vendor.id == vendor.id).values(sequence_count=SeqCount)
        db.session.execute(stmt)

    db.session.commit()

    Vendors = Vendor.query.order_by(Vendor.name)
    for vendor in Vendors:
        print(vendor.name, vendor.time_created, vendor.sequence_count)

if __name__ == "__main__":
    main()