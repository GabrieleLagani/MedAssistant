import os
import shutil
import sqlite3

from config import *


def create_db(path):
	os.makedirs(os.path.dirname(path), exist_ok=True)
	if os.path.exists(path): shutil.move(path, path + '.old') # Save-replace old files
	db = sqlite3.connect(path)
	cur = db.cursor()
	
	tables = {  'doctors':
		          {'header':     ('name', 'specialization'),
		           'data':      [('Dr. Lyubor', 'Neurology'),
		                         ('Dr. Brazov', 'Pneumology'),
		                         ('Dr. Amicis', 'Endocrinology'),
		                         ('Dr. Mirabella', 'Gastroenterology'),
		                         ('Dr. Muller', 'Cardiology'),
		                         ('Dr. Dubois', 'Dermatology'),]
		           },
	            
	            'appointments':
		            {'header':   ('id', 'doctor', 'time_slot', 'patient'),
		             'data':    [(0,  'Dr. Lyubor', '10-01-2025 09:00:00', None),
		                         (1,  'Dr. Lyubor', '10-01-2025 10:00:00', 'Martini'),
		                         (2,  'Dr. Brazov', '11-01-2025 09:00:00', None),
		                         (3,  'Dr. Brazov', '11-01-2025 10:00:00', None),
		                         (4,  'Dr. Amicis', '12-01-2025 09:00:00', None),
		                         (5,  'Dr. Amicis', '12-01-2025 10:00:00', None),
		                         (6,  'Dr. Mirabella', '13-01-2025 09:00:00', 'Russel'),
		                         (7,  'Dr. Mirabella', '13-01-2025 10:00:00', None),
		                         (8,  'Dr. Muller', '14-01-2025 09:00:00', None),
		                         (9,  'Dr. Muller', '14-01-2025 10:00:00', None),
		                         (10, 'Dr. Dubois', '15-01-2025 09:00:00', None),
		                         (11, 'Dr. Dubois', '15-01-2025 10:00:00', None),]
		            }
	          }
	
	for t_name, t in tables.items():
		creation_query = "CREATE TABLE {}{}".format(t_name, t['header'])
		print("Creation query: {}".format(creation_query))
		cur.execute(creation_query)
		placeholders = ','.join(['?'] * len(t['header']))
		insertion_query = "INSERT INTO {} VALUES({})".format(t_name, placeholders)
		print("Insertion query: {}".format(insertion_query))
		cur.executemany(insertion_query, t['data'])
		db.commit()
	
	return db
	
	

if __name__ == '__main__':
	# Create DB
	db = create_db(DB_PATH)
	
	# Try out a query
	cur = db.cursor()
	select_query = "SELECT name FROM doctors"
	print("Select query: {}".format(select_query))
	res = cur.execute(select_query)
	print("Query results: {}".format(res.fetchall()))
	
	