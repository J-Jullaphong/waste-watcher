INSERT INTO waste_record (timestamp, bin_id, location, lat, lon, temp, precip, humid, capacity, level)
SELECT 
    ws.timestamp, 
    b.bin_id, 
    b.location, 
    b.lat, 
    b.lon, 
    wa.temp, 
    wa.precip, 
    wa.humid, 
    b.capacity, 
    ws.level
FROM 
    waste ws
JOIN 
    bin b ON b.bin_id = ws.bin_id
JOIN 
    weather_api wa ON wa.location = b.location AND wa.timestamp = ws.timestamp;

