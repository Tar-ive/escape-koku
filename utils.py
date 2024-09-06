from datetime import datetime, timedelta

def calculate_crowd_density(reports):
    if not reports:
        return {}
    
    now = datetime.utcnow()
    recent_reports = [r for r in reports if now - r.timestamp < timedelta(hours=1)]
    
    if not recent_reports:
        return {}
    
    density_map = {}
    for report in recent_reports:
        key = f"{report.latitude:.4f},{report.longitude:.4f}"
        if key in density_map:
            density_map[key].append(report.density)
        else:
            density_map[key] = [report.density]
    
    return {k: sum(v) / len(v) for k, v in density_map.items()}
