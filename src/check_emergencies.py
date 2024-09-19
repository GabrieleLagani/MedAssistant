import sqlite3

from config import *


def check_emergencies():
	# Connect to database
	db = sqlite3.connect(DB_PATH)
	cur = db.cursor()
	
	# Prepare query
	query = """
			SELECT *
			FROM emergencies
			"""
	result = cur.execute(query)
	emergencies = result.fetchall()
	
	print("List of emergencies:")
	for e in emergencies: print('* {}'.format(e))
	
	
if __name__ == '__main__':
	check_emergencies()
