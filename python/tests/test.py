import database

db = database.thermoDB('thermostat.db',debug=True)
print db.getSystemStatus()