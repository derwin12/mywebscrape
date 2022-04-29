## Database Migrations
Edit the classes in app/__init__.py for the database schema
```$ flask db migrate -m "Some comment"```
```$ flask db upgrade ```

    flask db migrate -m "Adding vendor count"
    INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
    INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
    INFO  [alembic.autogenerate.compare] Detected added column 'vendor.sequence_count'
    Generating migrations/versions/f38b854cb661_adding_vendor_count.py ...  done
    flask db upgrade
    INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
    INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
    INFO  [alembic.runtime.migration] Running upgrade 77fdfbc43629 -> f38b854cb661, Adding vendor count

>>> x = db.session.query(Vendor.name, db.func.count(Sequence.vendor_id)).outerjoin(Sequence, Vendor.id == Sequence.vendor_id).group_by(Vendor.name).all()
>>> [print(y) for y in x]
('Animated Illumination', 9)
('BlinkySequences', 3)
('BostikFamilyLightshow', 30)
('CFOLights', 22)
('Custom Light Creations', 107)
('East Ridge Lights', 5)
('Fairy Pixel Dust', 32)
('FcLightsDisplay', 6)
('GoogleDrive', 543)
('Holiday Sequences', 139)
('HolidayCoro', 290)
('Inspire Lightshows', 8)
('JL Pixel Sequences', 4)
('Jolly Jingle Sequences', 27)
('LED Warehouse', 15)
('Laredo Lights', 6)
('Led Warehouse', 0)
('LightEm Up Sequences', 100)
('Lights of the Night', 19)
('Livermore Lights', 8)
('Magical Light Shows', 56)
('Music with Motion', 36)
('OG Sequences', 38)
('Pixel Pro Displays', 303)
('PixelPerfectSequences', 25)
('PixelSequencePros', 26)
('RGBSequences', 57)
('Sequence Depot', 4)
('Sequence Outlet', 13)
('Sequence Solutions', 32)
('Show Sequences', 3)
('ShowStoppers', 151)
('Showtime Bumpers', 7)
('Spectacle of Light Sequences', 4)
('Syracuse Lights', 10)
('The Sequence Armory', 25)
('UXSG', 829)
('VisionaryLightShow', 41)
('Vivid Sequences', 2)
('Whimsical Light Shows', 12)
('xLightsSequences', 71)
('xTreme Sequences', 117)