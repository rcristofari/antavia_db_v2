#----------------------------------------------------------------------------------------------------------------------#
#  PLACES

create_colonies = "CREATE TABLE IF NOT EXISTS colonies (" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "name varchar(64) NOT NULL UNIQUE," \
            "archipelago enum('Crozet', 'Kerguelen', 'Marion_PrinceEdward', 'Heard_McDonald','Macquarie', 'Patagonia', 'South_Georgia', 'Scotia', 'At sea', 'Ukn') DEFAULT 'Ukn'," \
            "lat double," \
            "lon double," \
            "description varchar(255)" \
            ") ENGINE = InnoDB DEFAULT CHARSET=utf8;"

create_antennas = "CREATE TABLE IF NOT EXISTS antennas (" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "name varchar(64) NOT NULL UNIQUE," \
            "description varchar(255)," \
            "colony varchar(64) NOT NULL," \
            "side enum('Terre','Mer','Both') NOT NULL," \
            "CONSTRAINT FK_antenna_locations_REF_colonies " \
            "FOREIGN KEY (colony) " \
            "REFERENCES colonies(name) ON UPDATE CASCADE" \
            ") ENGINE = InnoDB DEFAULT CHARSET=utf8;"

create_locations = "CREATE TABLE IF NOT EXISTS locations (" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "colony varchar(64) NOT NULL," \
            "name varchar(64) NOT NULL UNIQUE," \
            "description varchar(255)," \
            "CONSTRAINT FK_locations_REF_colonies " \
            "FOREIGN KEY (colony) " \
            "REFERENCES colonies(name) ON UPDATE CASCADE" \
            ") ENGINE = InnoDB DEFAULT CHARSET=utf8;"

#----------------------------------------------------------------------------------------------------------------------#
# HANDLERS

create_handlers = "CREATE TABLE IF NOT EXISTS handlers (" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "name varchar(64) NOT NULL UNIQUE," \
            "description varchar(64) NOT NULL" \
            ") ENGINE = InnoDB DEFAULT CHARSET=utf8;"

#----------------------------------------------------------------------------------------------------------------------#
# MANIPS

create_manip_classes = "CREATE TABLE IF NOT EXISTS manip_classes (" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "class varchar(64) NOT NULL UNIQUE," \
            "description varchar(255)," \
            "KEY K_manip_classes_class (class)" \
            ") ENGINE = InnoDB DEFAULT CHARSET=utf8;"

create_manips = "CREATE TABLE IF NOT EXISTS manips (" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "class varchar(64) NOT NULL," \
            "name varchar(64) NOT NULL UNIQUE," \
            "year int(4) NOT NULL," \
            "description varchar(255)," \
            "CONSTRAINT FK_manips_REF_manip_classes " \
            "FOREIGN KEY (class) " \
            "REFERENCES manip_classes(class) ON UPDATE CASCADE" \
            ") ENGINE = InnoDB DEFAULT CHARSET=utf8;"

create_stages = "CREATE TABLE IF NOT EXISTS stages (" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "class enum('Adult','Juvenile','Chick','Ukn') NOT NULL DEFAULT 'Ukn'," \
            "name varchar(64) NOT NULL UNIQUE," \
            "description varchar(255)" \
            ") ENGINE = InnoDB DEFAULT CHARSET=utf8;"

create_bird_manips = "CREATE TABLE IF NOT EXISTS bird_manips(" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "rfid varchar(64) NOT NULL," \
            "manip varchar(64) NOT NULL," \
            "comment varchar(512)," \
            "CONSTRAINT FK_bird_manips_REF_birds " \
            "FOREIGN KEY (rfid) REFERENCES birds(rfid) ON DELETE CASCADE ON UPDATE CASCADE," \
            "CONSTRAINT FK_bird_manips_REF_manips " \
            "FOREIGN KEY (manip) REFERENCES manips(name) ON DELETE CASCADE ON UPDATE CASCADE, " \
            "CONSTRAINT un_rfid_manip UNIQUE (rfid, manip)" \
            ") ENGINE = InnoDB DEFAULT CHARSET=utf8;"

#----------------------------------------------------------------------------------------------------------------------#
# EVENTS

create_event_classes = "CREATE TABLE IF NOT EXISTS event_classes (" \
           "id int(10) PRIMARY KEY AUTO_INCREMENT," \
           "class varchar(64) NOT NULL UNIQUE," \
           "description varchar(255)," \
           "KEY K_event_classes_class (class)" \
           ") ENGINE = InnoDB DEFAULT CHARSET=utf8;"

create_event_types = "CREATE TABLE IF NOT EXISTS event_types (" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "class varchar(64) NOT NULL," \
            "name varchar(64) NOT NULL UNIQUE," \
            "description varchar(255)," \
            "CONSTRAINT FK_event_types_REF_event_classes " \
            "FOREIGN KEY (class) " \
            "REFERENCES event_classes(class) ON UPDATE CASCADE" \
            ") ENGINE = InnoDB DEFAULT CHARSET=utf8;"

create_events = "CREATE TABLE IF NOT EXISTS events(" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "rfid varchar(64) NOT NULL," \
            "event_date datetime NOT NULL, " \
            "event_type varchar(64) NOT NULL," \
            "stage varchar(64) NOT NULL DEFAULT 'Ukn'," \
            "location varchar(64)," \
            "handler varchar(64) NOT NULL," \
            "comment varchar(512)," \
            "KEY KEY_date (event_date)," \
            "CONSTRAINT FK_event_REF_birds " \
            "FOREIGN KEY (rfid) REFERENCES birds(rfid) ON DELETE CASCADE ON UPDATE CASCADE," \
            "CONSTRAINT FK_event_REF_event_types " \
            "FOREIGN KEY (event_type) REFERENCES event_types(name) ON UPDATE CASCADE," \
            "CONSTRAINT FK_events_REF_stages " \
            "FOREIGN KEY (stage) REFERENCES stages(name) ON UPDATE CASCADE," \
            "CONSTRAINT FK_event_REF_locations " \
            "FOREIGN KEY (location) REFERENCES locations(name) ON UPDATE CASCADE," \
            "CONSTRAINT FK_event_REF_handlers " \
            "FOREIGN KEY (handler) REFERENCES handlers(name) ON UPDATE CASCADE" \
            ")ENGINE=InnoDB DEFAULT CHARSET=utf8;"

#----------------------------------------------------------------------------------------------------------------------#
# MEASURES

create_measure_classes = "CREATE TABLE IF NOT EXISTS measure_classes (" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "class varchar(64) NOT NULL UNIQUE," \
            "description varchar(255)," \
            "KEY K_measure_classes_class (class)" \
            ") ENGINE = InnoDB DEFAULT CHARSET=utf8;"

create_measure_types = "CREATE TABLE IF NOT EXISTS measure_types (" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "class varchar(64) NOT NULL," \
            "name varchar (64) NOT NULL UNIQUE," \
            "unit varchar(10)," \
            "description varchar(255)" \
            ") ENGINE = InnoDB DEFAULT CHARSET=utf8;"

create_measures = "CREATE TABLE IF NOT EXISTS measures(" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "event_id int(10) NOT NULL," \
            "name varchar(64) NOT NULL," \
            "value varchar(64) NOT NULL," \
            "raw_value varchar(64),"\
            "comment varchar(512)," \
            "CONSTRAINT FK_measures_REF_events " \
            "FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE," \
            "CONSTRAINT FK_measures_REF_measure_types " \
            "FOREIGN KEY (name) REFERENCES measure_types(name) ON UPDATE CASCADE" \
            ")ENGINE=InnoDB DEFAULT CHARSET=utf8;"

#----------------------------------------------------------------------------------------------------------------------#
# PHENOLOGY

create_phenology_types = "CREATE TABLE IF NOT EXISTS phenology_types (" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "name varchar(64) NOT NULL UNIQUE," \
            "description varchar(255)" \
            ") ENGINE = InnoDB DEFAULT CHARSET=utf8;"

create_phenology = "CREATE TABLE IF NOT EXISTS phenology(" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "rfid varchar(64) NOT NULL," \
            "name varchar(64) NOT NULL," \
            "type enum('obs','cycle') NOT NULL," \
            "date datetime NOT NULL," \
            "comment varchar(512)," \
            "CONSTRAINT FK_phenology_REF_birds " \
            "FOREIGN KEY (rfid) REFERENCES birds(rfid) ON DELETE CASCADE ON UPDATE CASCADE," \
            "CONSTRAINT FK_phenology_REF_phenology_types " \
            "FOREIGN KEY (name) REFERENCES phenology_types(name) ON UPDATE CASCADE" \
            ")ENGINE=InnoDB DEFAULT CHARSET=utf8 ;"

#----------------------------------------------------------------------------------------------------------------------#
# COMMENTS

create_comments = "CREATE TABLE IF NOT EXISTS comments(" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "rfid varchar(64) NOT NULL," \
            "comment TEXT NOT NULL," \
            "handler varchar(64) NOT NULL," \
            "date datetime," \
            "CONSTRAINT FK_comments_REF_birds " \
            "FOREIGN KEY (rfid) REFERENCES birds(rfid) ON DELETE CASCADE," \
            "CONSTRAINT FK_comments_REF_handlers " \
            "FOREIGN KEY (handler) REFERENCES handlers(name) ON UPDATE CASCADE" \
            ") ENGINE = InnoDB DEFAULT CHARSET=utf8;"

#----------------------------------------------------------------------------------------------------------------------#
# PACKING
create_rfid_packing = "CREATE TABLE IF NOT EXISTS rfid_packing_types (" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "name varchar(64) NOT NULL UNIQUE," \
            "description varchar(255)" \
            ") ENGINE = InnoDB DEFAULT CHARSET=utf8;"

#----------------------------------------------------------------------------------------------------------------------#
# ALARMS

create_alarms = "CREATE TABLE IF NOT EXISTS alarms (" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "class varchar(64) NOT NULL UNIQUE," \
            "description text" \
            ") ENGINE = InnoDB DEFAULT CHARSET=utf8;"

#----------------------------------------------------------------------------------------------------------------------#
# BIRDS

create_birds = "CREATE TABLE IF NOT EXISTS birds (" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "rfid varchar(64) NOT NULL UNIQUE," \
            "name varchar(64) NOT NULL UNIQUE," \
            "sex ENUM('M','Mobs','F','Fobs') DEFAULT NULL," \
            "birth_year INT(4) UNSIGNED DEFAULT NULL,"\
            "birth_year_type ENUM('obs', 'infer', 'methyl') DEFAULT NULL,"\
            "rfid_date DATE," \
            "ft_date DATE," \
            "current_loc VARCHAR(64)," \
            "last_detection datetime," \
            "alarm varchar(64)," \
            "death_date DATE," \
            "dead tinyint(1) UNSIGNED NOT NULL DEFAULT 0," \
            "ring_number varchar(64)," \
            "rfid_stage varchar(64)," \
            "KEY KEY_dead (dead)," \
            "KEY KEY_rfid_date (rfid_date)," \
            "KEY KEY_rfid_stage (rfid_stage)," \
            "KEY KEY_last_detection (last_detection)," \
            "CONSTRAINT FK_birds_REF_locations " \
            "FOREIGN KEY (current_loc) " \
            "REFERENCES colonies(name)," \
            "CONSTRAINT FK_birds_REF_alarms " \
            "FOREIGN KEY (alarm) " \
            "REFERENCES alarms(class) ON UPDATE CASCADE ON DELETE SET NULL," \
            "CONSTRAINT FK_birds_REF_rfid_stages " \
            "FOREIGN KEY (rfid_stage) " \
            "REFERENCES stages(name) ON UPDATE CASCADE" \
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"

#----------------------------------------------------------------------------------------------------------------------#
# CYCLES

create_breeding = "CREATE TABLE breeding("\
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
           "season int(4) NOT NULL," \
           "female_id varchar(64) DEFAULT NULL," \
           "male_id varchar(64) DEFAULT NULL," \
           "offspring_id varchar(64) DEFAULT NULL," \
           "outcome enum('success','failure','nonbreeding') DEFAULT NULL," \
           "pair_type enum('observed','feeding','cycle') DEFAULT NULL," \
           "offspring_type enum('observed','feeding') DEFAULT NULL," \
           "KEY female_id (female_id), " \
           "KEY male_id (male_id), " \
           "KEY offspring_id (offspring_id), " \
           "CONSTRAINT FK_breeding_REF_female_id " \
           "FOREIGN KEY (female_id) " \
           "REFERENCES birds (rfid) ON DELETE CASCADE ON UPDATE CASCADE," \
           "CONSTRAINT FK_breeding_REF_male_id " \
           "FOREIGN KEY (male_id) " \
           "REFERENCES birds (rfid) ON DELETE CASCADE ON UPDATE CASCADE," \
           "CONSTRAINT FK_breeding_REF_offspring_id " \
           "FOREIGN KEY (offspring_id) " \
           "REFERENCES birds (rfid) ON DELETE CASCADE ON UPDATE CASCADE" \
           ") ENGINE= InnoDB DEFAULT CHARSET=utf8;"

create_cycling = "CREATE TABLE cycling (" \
            "id INT(10) PRIMARY KEY AUTO_INCREMENT," \
            "rfid varchar(64) NOT NULL," \
            "season SMALLINT(4) NOT NULL," \
            "value VARCHAR(3)," \
            "behavioral_sex VARCHAR(2)," \
            "start_dtime DATETIME NOT NULL," \
            "end_dtime DATETIME," \
            "comment VARCHAR(256)," \
            "CONSTRAINT FK_cycling_REF_birds " \
            "FOREIGN KEY (rfid) REFERENCES birds(rfid) ON DELETE CASCADE ON UPDATE CASCADE" \
            ")ENGINE=InnoDB DEFAULT CHARSET=utf8;"

create_computed_cycling = "CREATE TABLE computed_cycling (" \
            "id INT(10) PRIMARY KEY AUTO_INCREMENT," \
            "rfid varchar(64) NOT NULL," \
            "season SMALLINT(4) NOT NULL," \
            "value VARCHAR(3)," \
            "behavioral_sex ENUM('Mobs','Fobs')," \
            "start_dtime DATETIME NOT NULL," \
            "end_dtime DATETIME," \
            "comment VARCHAR(256)," \
            "CONSTRAINT FK_computed_cycling_REF_birds " \
            "FOREIGN KEY (rfid) REFERENCES birds(rfid) ON DELETE CASCADE ON UPDATE CASCADE" \
            ")ENGINE=InnoDB DEFAULT CHARSET=utf8;"

#----------------------------------------------------------------------------------------------------------------------#
# DETECTIONS

create_detections = "CREATE TABLE IF NOT EXISTS detections(" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "rfid varchar(64) NOT NULL," \
            "antenna_id int(10) NOT NULL," \
            "dtime datetime," \
            "type enum('fix','mob','man')," \
            "CONSTRAINT FK_detections_antennas " \
            "FOREIGN KEY (antenna_id) REFERENCES antennas(id)," \
            "CONSTRAINT FK_detections_birds " \
            "FOREIGN KEY (rfid) REFERENCES birds(rfid) ON DELETE CASCADE ON UPDATE CASCADE," \
            "INDEX rfid_dtime (rfid, dtime)" \
            ") ENGINE= InnoDB DEFAULT CHARSET=utf8;"


create_computed_detections = "CREATE TABLE IF NOT EXISTS computed_detections(" \
            "id int(10) PRIMARY KEY AUTO_INCREMENT," \
            "rfid varchar(64) NOT NULL," \
            "antenna_id int(10) NOT NULL," \
            "dtime datetime," \
            "type enum('logical','probabilistic')," \
            "CONSTRAINT FK_computed_detections_antennas " \
            "FOREIGN KEY (antenna_id) REFERENCES antennas(id)," \
            "CONSTRAINT FK_computed_detections_rfid " \
            "FOREIGN KEY (rfid) REFERENCES birds(rfid) ON DELETE CASCADE ON UPDATE CASCADE," \
            "INDEX rfid_dtime_computed (rfid, dtime)" \
            ") ENGINE= InnoDB DEFAULT CHARSET=utf8;"