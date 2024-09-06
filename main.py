from flask import Flask, render_template, request, jsonify
from config import Config, init_db, check_db_connection
from utils import calculate_crowd_density
from datetime import datetime, timedelta
import logging
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
db = init_db(app)

# Import models after db initialization
from models import init_models
CrowdReport, FavoriteSpot, ParkingSpot = init_models(db)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/report_crowd', methods=['POST'])
def report_crowd():
    try:
        data = request.json
        logger.debug(f"Received crowd report data: {data}")
        if not all(key in data for key in ['latitude', 'longitude', 'density']):
            raise ValueError("Missing required fields in the request")
        new_report = CrowdReport(
            latitude=data['latitude'],
            longitude=data['longitude'],
            density=data['density']
        )
        db.session.add(new_report)
        db.session.commit()
        logger.info("Crowd report submitted successfully")
        return jsonify({"message": "Report submitted successfully"}), 200
    except ValueError as ve:
        db.session.rollback()
        logger.error(f"Invalid data in report_crowd: {str(ve)}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in report_crowd: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/api/get_crowd_density', methods=['GET'])
def get_crowd_density():
    try:
        reports = CrowdReport.query.all()
        logger.debug(f"Retrieved {len(reports)} crowd reports")
        if not reports:
            logger.info("No crowd reports found in the database.")
            return jsonify({}), 200
        density_data = calculate_crowd_density(reports)
        logger.debug(f"Calculated density data: {density_data}")
        return jsonify(density_data), 200
    except Exception as e:
        logger.error(f"Error in get_crowd_density: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_specific_crowd_density', methods=['GET'])
def get_specific_crowd_density():
    try:
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        if not lat or not lng:
            return jsonify({"error": "Latitude and longitude are required"}), 400
        
        reports = CrowdReport.query.filter(
            CrowdReport.latitude.between(float(lat) - 0.001, float(lat) + 0.001),
            CrowdReport.longitude.between(float(lng) - 0.001, float(lng) + 0.001),
            CrowdReport.timestamp > (datetime.utcnow() - timedelta(hours=1))
        ).all()
        
        if not reports:
            return jsonify({"density": 0, "status": "Not occupied"}), 200
        
        density = sum(report.density for report in reports) / len(reports)
        status = "Highly occupied" if density > 2 else "Moderately occupied" if density > 1 else "Lightly occupied"
        return jsonify({"density": round(density, 1), "status": status}), 200
    except Exception as e:
        logger.error(f"Error in get_specific_crowd_density: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/favorite_spots', methods=['GET', 'POST'])
def favorite_spots():
    try:
        if request.method == 'POST':
            data = request.json
            logger.debug(f"Received favorite spot data: {data}")
            new_spot = FavoriteSpot(
                user_id=data['user_id'],
                latitude=data['latitude'],
                longitude=data['longitude'],
                name=data['name']
            )
            db.session.add(new_spot)
            db.session.commit()
            logger.info("Favorite spot added successfully")
            return jsonify({"message": "Favorite spot added successfully"}), 200
        else:
            user_id = request.args.get('user_id')
            spots = FavoriteSpot.query.filter_by(user_id=user_id).all()
            logger.debug(f"Retrieved {len(spots)} favorite spots for user {user_id}")
            return jsonify([spot.to_dict() for spot in spots])
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in favorite_spots: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route('/api/report_parking', methods=['POST'])
def report_parking():
    try:
        data = request.json
        new_report = ParkingSpot(
            latitude=data['latitude'],
            longitude=data['longitude'],
            available=data['available']
        )
        db.session.add(new_report)
        db.session.commit()
        return jsonify({"message": "Parking report submitted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/api/get_parking', methods=['GET'])
def get_parking():
    try:
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        spots = ParkingSpot.query.filter(ParkingSpot.timestamp > one_hour_ago).all()
        return jsonify([{
            'latitude': spot.latitude,
            'longitude': spot.longitude,
            'available': spot.available
        } for spot in spots]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/check_database')
def check_database():
    connection_status = check_db_connection(db)
    db_url = app.config['SQLALCHEMY_DATABASE_URI']
    db_url_masked = db_url.split("://")[0] + "://" + "****" + db_url.split("@")[-1] if db_url else "Not set"
    
    if connection_status:
        logger.info("Database connection successful.")
        message = "Database connection successful."
    else:
        logger.error("Database connection failed.")
        message = "Database connection failed. Please check your configuration."
    
    return jsonify({
        "status": "success" if connection_status else "error",
        "message": message,
        "database_url": db_url_masked,
        "environment_variables": {
            "PGHOST": os.environ.get("PGHOST", "Not set"),
            "PGPORT": os.environ.get("PGPORT", "Not set"),
            "PGDATABASE": os.environ.get("PGDATABASE", "Not set"),
            "PGUSER": os.environ.get("PGUSER", "Not set"),
            "PGPASSWORD": "****" if "PGPASSWORD" in os.environ else "Not set"
        }
    })

if __name__ == '__main__':
    with app.app_context():
        if not check_db_connection(db):
            logger.error("Unable to connect to the database. Please check your DATABASE_URL environment variable.")
            exit(1)
    app.run(host='0.0.0.0', port=5000)
