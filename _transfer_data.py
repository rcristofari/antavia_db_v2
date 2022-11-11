import pymysql, time
from _tools import *
import csv

def transfer_colonies(db_target):
    print(f"{time.asctime()} | Transferring colonies...", end="")
    colonies = [['SEA', 'At sea', 'Somewhere in the Southern Ocean'],
                    ['BDM', 'Crozet', 'Baie du marin'],
                    ['CDC', 'Crozet', 'Crique de la Chaloupe'],
                    ['PMC', 'Crozet', 'Petite Manchotière'],
                    ['JJP', 'Crozet', 'Jardin Japonais'],
                    ['MAE', 'Crozet', 'Mare aux Elephants'],
                    ['RAT', 'Kerguelen', 'Ratmanoff']]
    for colony in colonies:
        db_target.execute(f"INSERT INTO colonies (name, archipelago, description) VALUES ('{colony[0]}', '{colony[1]}', '{colony[2]}');")
    print("done.")

def transfer_antennas(db_target):
    print(f"{time.asctime()} | Transferring antennas...", end="")
    antennas = [['BretelleSud_Mer', 'Bretelle sud Mer', 'BDM', 'Mer'],
                ['BretelleSud_Terre', 'Bretelle sud Terre', 'BDM', 'Terre'],
                ['Autoroute_Mer', 'Autoroute Mer', 'BDM', 'Mer'],
                ['Autoroute_Terre', 'Autoroute Terre', 'BDM', 'Terre'],
                ['Manchoduc_Mer', 'Manchoduc Mer', 'BDM', 'Mer'],
                ['Manchoduc_Terre', 'Manchoduc Terre', 'BDM', 'Terre'],
                ['Prado_Mer', 'Prado Mer', 'BDM', 'Mer'],
                ['Prado_Terre', 'Prado Terre', 'BDM', 'Terre']]
    for antenna in antennas:
        db_target.execute(f"INSERT INTO antennas (name, description, colony, side) VALUES ('{antenna[0]}', '{antenna[1]}', '{antenna[2]}', '{antenna[3]}');")
    print("done.")

def transfer_locations(db_source, db_target):
    print(f"{time.asctime()} | Transferring locations...", end="")
    loc_names = [x[0] for x in db_source.fetchall("SELECT nom FROM lieux_transpondage;")]
    colony = ["RAT" if any(x == i for i in ("Guetteur", "Lac", "Ratmanoff")) else "BDM" for x in loc_names]
    locs = dict(zip(loc_names, colony))
    locs["MAE"] = "MAE"
    locs["JJP"] = "JJP"
    locs["CDC"] = "CDC"
    locs["PMC"] = "PMC"
    for l in locs:
        db_target.execute(f"INSERT INTO locations (name, colony) VALUES ('{l}', '{locs[l]}');")
    antennas = db_target.fetchall("SELECT name, colony FROM antennas;")
    for a in antennas:
        db_target.execute(f"INSERT INTO locations (name, colony) VALUES ('{a[0]}', '{a[1]}');")
    print("done.")

def transfer_handlers(db_source, db_target):
    print(f"{time.asctime()} | Transferring handlers...", end="")
    handlers = db_source.fetchall("SELECT nom, description FROM manipulateurs;")
    for h in handlers:
        db_target.execute(f"INSERT INTO handlers (name, description) VALUES ('{h[0]}', '{h[1]}');")
    print("done.")

def transfer_manip_classes(db_target):
    print(f"{time.asctime()} | Transferring manipulation classes...", end="")
    class_list = ["Puli", "EarlyLate", "FIDH", "Other", "OtherPrograms", "Tests"]
    for i in class_list:
        db_target.execute(f"INSERT INTO manip_classes (class) VALUES ('{i}');")
    print("done.")

def transfer_manip(db_target):
    print(f"{time.asctime()} | Transferring manipulations...", end="")
    csv_file = csv.reader(open("csv_files/manipulations_possibles.csv"))
    next(csv_file)
    for row in csv_file:
        db_target.execute(f"INSERT INTO manips (class, name, year) VALUES ('{row[1]}', '{row[2]}', '{row[3]}');")
    print("done.")

def transfer_stage(db_source, db_target):
    print(f"{time.asctime()} | Transferring stage...", end="")
    stages = db_source.fetchall("SELECT age, description FROM stade_transpondage;")
    for i, s in enumerate(stages):
        if s[0].startswith("A-"):
            classe = "Adult"
        elif s[0].startswith("P-"):
            classe = "Chick"
        else:
            classe = "Ukn"
        db_target.execute(f"INSERT INTO stages (class, name, description) VALUES ('{classe}', '{s[0]}', '{s[1]}');")
    db_target.execute("DELETE FROM stages WHERE name = '(Inconnu)'")
    print("done.")

def transfer_alarms(db_target):
    print(f"{time.asctime()} | Transferring alarms...", end="")
    alarms = [["CAPTURE", "Catch the bird if leaving colony"],
              ["FOLLOW", "Follow bird if entering colony"],
              ["VISUAL CONTROL", "Check body condition"]]
    for a in alarms:
        db_target.execute(f"INSERT INTO alarms(class, description) VALUES ('{a[0]}','{a[1]}');")
    print("done.")

def transfer_event_classes(db_target):
    print(f"{time.asctime()} | Transferring event classes...", end="")
    events = [['Capture', 'The bird was captured and handled'],
         ['Visual control', 'An observation without handling'],
         ['Marking', 'The bird was marked without capture']]
    for e in events:
        db_target.execute(f"INSERT INTO event_classes(class, description) VALUES ('{e[0]}','{e[1]}');")
    print("done.")

def transfer_event_types(db_target):
    print(f"{time.asctime()} | Transferring event types...", end="")
    events = [['Capture','Pit-tagging'],
              ['Capture','Fish-tagging'],
              ['Capture','Recapture'],
              ['Visual control','Random control'] ,
              ['Visual control','Localisation'],
              ['Marking','Marking']]
    for e in events:
        db_target.execute(f"INSERT INTO event_types(class, name) VALUES ('{e[0]}','{e[1]}');")
    print("done.")

def transfer_measure_types(db_source, db_target):
    print(f"{time.asctime()} | Transferring measure types...", end="")
    measures = [list(x) for x in db_source.fetchall("SELECT class, var, unit, description FROM measure_types;")]
    measures += [['marking','visual identity','cat','One or two flipper bands'],
                  ['rfid_data', 'rfid_packing', 'cat', 'Packing of pits before being implanted'],
                  ['rfid_data', 'rfid_desinfectant', 'cat', 'Desinfectant used during the pit-tagging'],
                  ['sampling', 'blood_q7', 'boolean', '1 if blood-q7 sampling has been done during the event'],
                  ['sampling', 'blood_RBC', 'boolean', '1 if blood-RBC sampling has been done during the event'],
                  ['sampling', 'blood_PL', 'boolean', '1 if blood-PL sampling has been done during the event'],
                  ['sampling', 'blood_SEC', 'boolean', '1 if blood-SEC sampling has been done during the event'],
                  ['sampling', 'feathers', 'boolean', '1 if feather sampling has been done during the event'],
                  ['sampling', 'ticks', 'boolean', '1 if tick sampling has been done during the event'],
                  ['sampling', 'guano', 'boolean', '1 if guano has been collected during the event']]
    for m in measures:
        db_target.execute(f"INSERT INTO measure_types (class, name, unit, description) VALUES ('{m[0]}','{m[1]}','{m[2]}','{m[3]}');")
    print("done.")

def transfer_birds(db_source, db_target):
    print(f"{time.asctime()} | Transferring birds:")
    birds = db_source.fetchall("SELECT * FROM animaux where supprime = 0;")
    n_birds = len(birds)
    print(f"\t- loaded data for {n_birds} individuals")
    for i, b in enumerate(birds):
        rfid = f"'{b[1]}'"
        name = f"'TEST_{b[1][-12:]}'" if b[3].startswith("TEST") else f"'{b[3]}'"
        sex = 'NULL' if missing_data(b[6]) else f"'{b[6].replace('?', 'obs')}'"
        rfid_stage = "'N/A'" if missing_data(b[14]) else f"'{b[14]}'"

        if any(x == b[2] for x in ("NULL", "0000-00-00", "1970-01-01")):
            date, ft_date, rfid_date, birth_year, birth_year_type = 'NULL', 'NULL', 'NULL', 'NULL', 'NULL'
        else:
            if b[1].startswith("A 9"):
                ft_date = f"'{b[2]}'"
                rfid_date = 'NULL'
                try:
                    birth_year = b[2].year
                    birth_year_type = "'obs'"
                    event_type = "'fish-tagging'"
                    rfid_stage = "'P-Brooding'"
                except AttributeError:
                    birth_year = 'NULL'
                    birth_year_type = 'NULL'
            else:
                rfid_date = f"'{b[2]}'"
                ft_date = 'NULL'
                birth_year, birth_year_type = birth_year_determination(b[2], rfid_stage)
                event_type = "'pit-tagging'"

        dead = b[9]
        death_date = 'NULL'
        alarm = 'NULL' if missing_data(b[7]) else "'CAPTURE'"

        # Fix ring number:
        if b[13] == '1_Bague':
            ring_number = name
        elif b[13] == '2_Bagues':
            ring_number = f"'{b[3]}+{b[10]}'"
        else:
            ring_number = 'NULL'
        last_detection = 'NULL' if missing_data(b[5]) else f"'{b[5]}'"

        # Current location:
        if b[12] == 0:
            current_loc = "'SEA'"
        elif b[12] == 1:
            current_loc = "'BDM'"
        else:
            current_loc = 'NULL'

        db_target.execute(f"INSERT INTO birds (rfid, name, sex, birth_year, birth_year_type, rfid_date, ft_date, current_loc, last_detection, alarm, death_date, dead, ring_number, rfid_stage) VALUES ({rfid},{name},{sex},{birth_year},{birth_year_type},{rfid_date},{ft_date},{current_loc},{last_detection},{alarm},{death_date},{dead},{ring_number},{rfid_stage});")

        print(f"\t- {round((i/n_birds)*100)}% completed ({i} birds)\r", end="")

        # Insert the corresponding events:
        rfid_packing = f"'{b[29]}'"
        rfid_desinfectant = f"'{b[30]}'"
        handler = "'N/A'" if missing_data(b[16]) else f"'{b[16]}'"
        rfid_loc = 'NULL' if missing_data(b[15]) else f"'{b[15]}'"

        if rfid_date != 'NULL':
            event_date = rfid_date
        elif ft_date != 'NULL':
            event_date = ft_date
        else:
            event_date = 'NULL'

        # pit / fish-tagging event:
        if event_date != "NULL":
            db_target.execute(f"INSERT INTO events (rfid, event_date, event_type, stage, location, handler) VALUES ({rfid},{event_date},{event_type},{rfid_stage},{rfid_loc},{handler});")

            #Add the pit tag conditioning values as measures
            event_id = db_target.last_id()
            if rfid_packing != "'N/A'":
                db_target.execute(f"INSERT INTO measures (event_id, name, value) VALUES ({event_id},'rfid_packing',{rfid_packing});")
            if rfid_desinfectant != "'N/A'":
                db_target.execute(f"INSERT INTO measures (event_id, name, value) VALUES ({event_id},'rfid_desinfectant',{rfid_desinfectant});")

def transfer_measures(db_source, db_target):
    print(f"{time.asctime()} | Transferring measures:")
    measures = db_source.fetchall("SELECT * FROM measures;")
    n_measures = len(measures)
    print(f"\t- loaded {n_measures} data points")
    for i, m in enumerate(measures):
        print(f"\t- {round((i / n_measures) * 100)}% completed ({i} data points)\r", end="")
        event = db_target.fetchall(f"SELECT id FROM events where rfid = '{m[1]}' and event_date = '{m[3]}';")
        if event:
            event_id = event[0][0]
            db_target.execute(f"INSERT INTO measures (event_id, name, value, raw_value) VALUES ({event_id},'{m[2]}','{m[4]}','{m[5]}');")
        else:
            try:
                # create an event
                handler = f"'{m[6]}'" if m[6] else 'NULL'
                db_target.execute(f"INSERT INTO events (rfid, event_date, event_type, stage, handler) VALUES ('{m[1]}','{m[3]}','Recapture','Ukn', {handler});")
                event_id = db_target.last_id()
                db_target.execute(f"INSERT INTO measures (event_id, name, value, raw_value) VALUES ({event_id},'{m[2]}','{m[4]}','{m[5]}');")
            except pymysql.err.IntegrityError:
                pass

def transfer_comments(db_source, db_target):
    print(f"{time.asctime()} | Transferring comments:")
    comments = db_source.fetchall("SELECT * FROM commentaire;")
    n_comments = len(comments)
    print(f"\t- loaded {n_comments} comments")
    for i, c in enumerate(comments):
        print(f"\t- {round((i / n_comments) * 100)}% completed ({i} comments)\r", end="")
        if c[2] is not None and not any(x == c[2] for x in ("test", "N/A", "")):
            comment = c[2].replace('"', "").replace("'", "")
            date = 'NULL' if missing_data(c[4]) else f"'{c[4]}'"
            try:
                # print(c)
                sql = f"INSERT INTO comments (rfid, comment, handler, date) VALUES ('{c[1]}','{comment}', 'N/A',{date});"
                # print(sql)
                db_target.execute(sql)
            except pymysql.err.IntegrityError:
                # print(f"Individual {c[1]} does not exist")
                pass

def transfer_creation_detection(db_source, db_target, source):
    print(f"{time.asctime()} | Transferring detections...", end="")
    query = "CREATE TABLE detections (" \
                    "id INT AUTO_INCREMENT PRIMARY KEY " \
                ") AS " \
                    "SELECT " \
                        "DISTNCT animaux.identifiant_transpondeur AS rfid, " \
                        "CAST(antenne_id AS SIGNED) AS antenna_id, " \
                        "date_arrivee AS dtime, " \
                        "'fixed' AS type " \
                    "FROM " + source + ".detections " \
                        "INNER JOIN " + source + ".animaux " \
                        "ON detections.animaux_id = animaux.id " \
                    "WHERE detections.supprime = 0 " \
                        "AND detections.detection_type = 'ORIGINAL' " \
                        "AND animaux.supprime = 0;"
    db_target.execute(query)
    print("done.")
    print(f"{time.asctime()} | Indexing detections...", end="")
    db_target.execute("ALTER TABLE detections ADD FOREIGN KEY (rfid) REFERENCES birds(rfid);")
    db_target.execute("ALTER TABLE detections ADD FOREIGN KEY (antenna_id) REFERENCES antennas(id);")
    db_target.execute("ALTER TABLE detections ADD INDEX dtime (rfid ASC, dtime ASC);")
    db_target.execute("UPDATE birds as targetTable, (SELECT rfid, max(dtime) as lastdetection FROM detections group by rfid) sourceTable SET targetTable.last_detection = sourceTable.lastdetection WHERE targetTable.rfid = sourceTable.rfid;")
    print("done.")

def transfer_bird_manips(db_source, db_target):
    print(f"{time.asctime()} | Transferring birds manipulations:")
    manips = db_source.fetchall("SELECT * FROM manipulations where manipulations_possibles_id != '' and animaux_id in (select identifiant_transpondeur from animaux where supprime = 0) and manipulations_possibles_id in (SELECT nom from manipulations_possibles where supprime = 0);")
    n_manips = len(manips)
    print(f"\t- loaded {n_manips} manips")
    for i, m in enumerate(manips):
        print(f"\t- {round((i / n_manips) * 100)}% completed ({i} manips)\r", end="")
        comment = 'NULL' if missing_data(m[3]) else f"'{m[3]}'"
        db_target.execute(f"INSERT INTO bird_manips (rfid, manip, comment) VALUES ('{m[1]}','{m[2]}',{comment}) ON DUPLICATE KEY UPDATE rfid = rfid;")

def transfer_cycling_types(db_target):
    print(f"{time.asctime()} | Transferring cycling types...", end="")
    cycles = [['arrival', 'Date of arrival in the colony for the first time after winter'],
             ['breeding', 'Date of the start of the breeding shift in colony'],
             ['laying', 'Date of laying'],
             ['brooding', 'Date of the start of brooding period (= hatching date)'],
             ['creching', 'Date of the start of creching period'],
             ['moult', 'Date of the start of moult shift']]
    for c in cycles:
        db_target.execute(f"INSERT INTO phenology_types (name, description) VALUES ('{c[0]}','{c[1]}');")
    print("done.")

def transfer_cycling(db_source, db_target):
    print(f"{time.asctime()} | Transferring cycles:")
    cycling = db_source.fetchall("SELECT * FROM evenements WHERE date_debut > '1970-01-01' AND date_fin > '1970-01-01' AND supprime = 0 and evenements_possibles_id = 'Breeding' and animaux_id in (select identifiant_transpondeur from animaux where supprime = 0);")
    n_cycles = len(cycling)
    print(f"\t- loaded {n_cycles} cycles")
    for i, c in enumerate(cycling):
        print(f"\t- {round((i / n_cycles) * 100)}% completed ({i} cycles)\r", end="")
        comment = f"'{c[6]}'" if not missing_data(c[6]) else 'NULL'
        value = "S" if c[3] == "Succes" else "F"
        db_target.execute(f"INSERT INTO cycling (rfid, season, value, start_dtime, end_dtime, comment) VALUES ('{c[2]}','{determine_year(c[4])}','{value}','{c[4]}','{c[5]}',{comment});")
