from datetime import datetime

def init_models(db):
    class CrowdReport(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        latitude = db.Column(db.Float, nullable=False)
        longitude = db.Column(db.Float, nullable=False)
        density = db.Column(db.Integer, nullable=False)
        timestamp = db.Column(db.DateTime, default=datetime.utcnow)

        def __init__(self, latitude, longitude, density):
            self.latitude = latitude
            self.longitude = longitude
            self.density = density

    class FavoriteSpot(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.String, nullable=False)
        latitude = db.Column(db.Float, nullable=False)
        longitude = db.Column(db.Float, nullable=False)
        name = db.Column(db.String(100), nullable=False)

        def __init__(self, user_id, latitude, longitude, name):
            self.user_id = user_id
            self.latitude = latitude
            self.longitude = longitude
            self.name = name

        def to_dict(self):
            return {
                'id': self.id,
                'latitude': self.latitude,
                'longitude': self.longitude,
                'name': self.name
            }

    class ParkingSpot(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        latitude = db.Column(db.Float, nullable=False)
        longitude = db.Column(db.Float, nullable=False)
        available = db.Column(db.Boolean, nullable=False)
        timestamp = db.Column(db.DateTime, default=datetime.utcnow)

        def __init__(self, latitude, longitude, available):
            self.latitude = latitude
            self.longitude = longitude
            self.available = available

    return CrowdReport, FavoriteSpot, ParkingSpot
