from _mysql_connect import *
from _create_tables import *
from _tools import *
from _transfer_data import *
import time, datetime

#----------------------------------------------------------------------------------------------------------------------#
host = "127.0.0.1"
port = 3306
usr = "root"
pwd = ""
source = "antavia_cro"
target = "antavia_cro_v2"
#----------------------------------------------------------------------------------------------------------------------#


start_time = time.time()

# Instantiate a connection to the source db
db_source = MysqlConnect(host=host, usr=usr, pwd=pwd, db=source, port=port)

# Delete the new database if it already exists, and create it:
print(f"{time.asctime()} | Initializing the database...", end="")
db_source.execute(f"DROP DATABASE IF EXISTS {target};")
db_source.execute(f"CREATE DATABASE IF NOT EXISTS {target};")
print("done.")

# Instantiate a connection to the target db
db_target = MysqlConnect(host=host, usr=usr, pwd=pwd, db=target, port=port)

#----------------------------------------------------------------------------------------------------------------------#
# Create tables in the target database
print(f"{time.asctime()} | Creating empty tables...", end="")
db_target.execute(create_colonies)
db_target.execute(create_antennas)
db_target.execute(create_locations)
db_target.execute(create_handlers)
db_target.execute(create_manip_classes)
db_target.execute(create_manips)
db_target.execute(create_stages)
db_target.execute(create_rfid_packing)
db_target.execute(create_alarms)
db_target.execute(create_birds)
db_target.execute(create_bird_manips)
db_target.execute(create_event_classes)
db_target.execute(create_event_types)
db_target.execute(create_events)
db_target.execute(create_measure_classes)
db_target.execute(create_measure_types)
db_target.execute(create_measures)
db_target.execute(create_phenology_types)
db_target.execute(create_phenology)
db_target.execute(create_breeding)
db_target.execute(create_cycling)
db_target.execute(create_computed_cycling)
# db_target.execute(create_detections)
db_target.execute(create_computed_detections)
db_target.execute(create_comments)
print("done.")

#----------------------------------------------------------------------------------------------------------------------#
# Transfer the minor tables
transfer_colonies(db_target)
transfer_antennas(db_target)
transfer_locations(db_source, db_target)
transfer_handlers(db_source, db_target)
transfer_manip_classes(db_target)
transfer_manip(db_target)
transfer_stage(db_source, db_target)
transfer_alarms(db_target)
transfer_event_classes(db_target)
transfer_event_types(db_target)
transfer_measure_types(db_source, db_target)
transfer_birds(db_source, db_target)
transfer_measures(db_source, db_target)
transfer_comments(db_source, db_target)
transfer_bird_manips(db_source, db_target)
transfer_cycling_types(db_target)
transfer_cycling(db_source, db_target)
transfer_creation_detection(db_source, db_target, source)

db_source.disconnect()
db_target.disconnect()

print(f"{time.asctime()} | Migration complete..!")
print("-----------------------------------------------")
print(f"Migration completed in {datetime.timedelta(seconds=time.time() - start_time)}")