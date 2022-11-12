
/*!50003 DROP PROCEDURE IF EXISTS `get_last_custom_error` */;

DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`root`@`localhost`*/ /*!50003 PROCEDURE `get_last_custom_error`()
BEGIN
  SELECT @error_method, @error_message;
END */;;
DELIMITER ;


/*!50003 DROP PROCEDURE IF EXISTS `raise_application_error` */;

DELIMITER ;;
/*!50003 CREATE*/ /*!50020 DEFINER=`root`@`localhost`*/ /*!50003 PROCEDURE `raise_application_error`(IN METHOD VARCHAR(255), IN MESSAGE VARCHAR(255))
BEGIN
  SELECT METHOD, MESSAGE INTO @error_method, @error_message;

  CREATE TEMPORARY TABLE IF NOT EXISTS RAISE_ERROR(`Erreur de trigger. Appelez la fonction get_last_custom_error()` INT NOT NULL);
  INSERT INTO RAISE_ERROR VALUES(NULL);
END */;;
DELIMITER ;


DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER birds_before_insert BEFORE INSERT ON birds
FOR EACH ROW BEGIN
	IF (@DISABLE_TRIGGERS IS NULL) THEN
		IF ( NEW.rfid NOT REGEXP '^(R|W) [0-9]{4} [0-9]{16}$'
			AND NEW.rfid NOT REGEXP '^A [0-9]{5} [0-9] [0-9]{3} [0-9]{12}$' ) THEN
			CALL raise_application_error('birds_before_insert','Invalid PIT-tag number, check the format (including whitespaces)');
		END IF;
		IF (NEW.rfid_date IS NOT NULL AND NEW.rfid_date > NOW() ) THEN
			CALL raise_application_error('birds_before_insert','PIT tagging date cannot be set in the future');
		END IF;
		IF (NEW.ft_date IS NOT NULL AND NEW.ft_date > NOW() ) THEN
			CALL raise_application_error('birds_before_insert','Fish-tagging date cannot be set in the future');
		END IF;
        IF(NEW.ft_date IS NOT NULL and NEW.rfid_date IS NOT NULL and NEW.ft_date > NEW.rfid_date) THEN
			CALL raise_application_error('birds_before_insert', 'Fish-tagging cannot occur after PIT-tagging');
		END IF;
END IF;
END */;;
DELIMITER ;

DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER birds_before_update BEFORE UPDATE ON birds
FOR EACH ROW BEGIN
	DECLARE date_first_detection DATETIME;
	IF (@DISABLE_TRIGGERS IS NULL) THEN
		IF ( OLD.id != NEW.id ) THEN
			CALL raise_application_error('birds_before_update','Penguin ID cannot be modified');
		END IF;

		IF ( OLD.rfid != NEW.rfid ) THEN
			IF ( NEW.rfid NOT REGEXP '^(R|W) [0-9]{4} [0-9]{16}$'
				AND NEW.rfid NOT REGEXP '^A [0-9]{5} [0-9] [0-9]{3} [0-9]{12}$' ) THEN
				CALL raise_application_error('birds_before_update','Invalid PIT-tag number, check the format (including whitespaces)');
			END IF;
		END IF;

		IF ( OLD.rfid_date != NEW.rfid_date ) THEN

			IF (NEW.rfid_date IS NOT NULL AND NEW.rfid_date > NOW() ) THEN
				CALL raise_application_error('birds_before_update','PIT tagging date cannot be set in the future');
			END IF;

			SELECT MIN(dtime) FROM detections WHERE rfid = NEW.id INTO date_first_detection;
			IF (date_first_detection IS NOT NULL AND NEW.rfid_date > date_first_detection) THEN
				CALL raise_application_error('birds_before_update','This penguin was first detected before the proposed new PIT-tagging date');
			END IF;

		END IF;

		IF ( OLD.ft_date != NEW.ft_date ) THEN
			IF (NEW.ft_date IS NOT NULL AND NEW.ft_date > NOW() ) THEN
				CALL raise_application_error('birds_before_update','Fish-tagging date cannot be set in the future');
			END IF;
		END IF;

		IF(NEW.ft_date IS NOT NULL and NEW.rfid_date IS NOT NULL and NEW.ft_date > NEW.rfid_date) THEN
			CALL raise_application_error('birds_before_update', 'Fish-tagging cannot occur after PIT-tagging');
		END IF;

		IF ( OLD.last_detection != NEW.last_detection ) THEN
			IF (NEW.last_detection IS NOT NULL AND NEW.last_detection > NOW() ) THEN
				CALL raise_application_error('birds_before_update', 'Last seen date cannot be set in the future');
			END IF;
		END IF;
	END IF;
END */;;
DELIMITER ;

DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER detections_after_insert AFTER INSERT ON detections
 FOR EACH ROW BEGIN
	DECLARE date_last_detection DATETIME;
    DECLARE last_location VARCHAR(64);
	IF (@DISABLE_TRIGGERS IS NULL) THEN
		SELECT birds.last_detection FROM birds WHERE rfid = NEW.rfid INTO date_last_detection;
        SELECT IF(LEFT(NEW.antenna_id, 1) & 1, 'SEA', 'BDM') INTO last_location;
		IF (date_last_detection IS NULL OR NEW.dtime > date_last_detection ) THEN
			UPDATE birds SET last_detection = NEW.dtime, current_loc = last_location WHERE birds.rfid = NEW.rfid;
		END IF;
	END IF;
END */;;
DELIMITER ;

DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `detections_after_update` AFTER UPDATE ON `detections`
 FOR EACH ROW BEGIN
	DECLARE date_last_detection DATETIME;
    DECLARE last_location VARCHAR(64);
	IF (@DISABLE_TRIGGERS IS NULL) THEN
		IF (NEW.dtime != OLD.dtime) OR (NEW.antenna_id != OLD.antenna_id) THEN
			SELECT birds.last_detection FROM birds WHERE rfid = NEW.rfid INTO date_last_detection;
			SELECT IF(LEFT(NEW.antenna_id, 1) & 1, 'SEA', 'BDM') INTO last_location;
			IF (date_last_detection IS NULL OR NEW.dtime > date_last_detection ) THEN 
				UPDATE birds SET last_detection = NEW.dtime, current_loc = last_location WHERE birds.rfid = NEW.rfid;
			END IF;
		END IF;
	END IF;
END */;;
DELIMITER ;

DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER detections_before_update BEFORE UPDATE ON detections
FOR EACH ROW BEGIN
	IF (@DISABLE_TRIGGERS IS NULL) THEN
		IF ( OLD.id != NEW.id ) THEN
			CALL raise_application_error('detections_before_update','You cannot modify row id !');
		END IF;
		
		IF ( OLD.rfid != NEW.rfid ) THEN
			CALL raise_application_error('detections_after_update','Impossible to change the associated RFID - you need to delete and re-insert the detection.');
		END IF;
		
	END IF;
END */;;
DELIMITER ;
