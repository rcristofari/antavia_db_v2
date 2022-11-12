DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER animaux_before_insert BEFORE INSERT ON animaux
FOR EACH ROW BEGIN
	IF (@DISABLE_TRIGGERS IS NULL) THEN
		IF ( NEW.identifiant_transpondeur NOT REGEXP '^(R|W) [0-9]{4} [0-9]{16}$'
			AND NEW.identifiant_transpondeur NOT REGEXP '^A [0-9]{5} [0-9] [0-9]{3} [0-9]{12}$' ) THEN
			CALL raise_application_error('animaux_before_insert','Invalid PIT-tag number, check the format (including whitespaces)');
		END IF;
		IF (NEW.date_transpondage IS NOT NULL AND NEW.date_transpondage > NOW() ) THEN
			CALL raise_application_error('animaux_before_insert','PIT tagging date cannot be set in the future');
		END IF;
	END IF;
END */;;
DELIMITER ;

DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER animaux_before_update BEFORE UPDATE ON animaux
FOR EACH ROW BEGIN
	DECLARE date_premiere_detection DATETIME;
	IF (@DISABLE_TRIGGERS IS NULL) THEN
		IF ( OLD.id != NEW.id ) THEN
			CALL raise_application_error('animaux_before_update','Penguin ID cannot be modified');
		END IF;
        
		IF ( OLD.identifiant_transpondeur != NEW.identifiant_transpondeur ) THEN
			IF ( NEW.identifiant_transpondeur NOT REGEXP '^(R|W) [0-9]{4} [0-9]{16}$'
				AND NEW.identifiant_transpondeur NOT REGEXP '^A [0-9]{5} [0-9] [0-9]{3} [0-9]{12}$' ) THEN
				CALL raise_application_error('animaux_before_update','Invalid PIT-tag number, check the format (including whitespaces)');
			END IF;
		END IF;
        
		IF ( OLD.date_transpondage != NEW.date_transpondage ) THEN
			
			IF (NEW.date_transpondage IS NOT NULL AND NEW.date_transpondage > NOW() ) THEN
				CALL raise_application_error('animaux_before_update','PIT tagging date cannot be set in the future');
			END IF;
            
			SELECT MIN(date_depart) FROM detections WHERE supprime = 0 AND animaux_id = NEW.id INTO date_premiere_detection;
			IF (date_premiere_detection IS NOT NULL AND NEW.date_transpondage > date_premiere_detection) THEN
				CALL raise_application_error('animaux_before_update','This penguin was first detected before the proposed new PIT-tagging date');
			END IF;
            
		END IF;
        
		IF ( OLD.date_derniere_detection != NEW.date_derniere_detection ) THEN
			IF (NEW.date_derniere_detection IS NOT NULL AND NEW.date_derniere_detection > NOW() ) THEN
				CALL raise_application_error('animaux_before_update','Last seen date cannot be set in the future');
			END IF;
		END IF;
	END IF;
END */;;
DELIMITER ;

DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER detections_after_insert AFTER INSERT ON detections
 FOR EACH ROW BEGIN
	DECLARE tmp INT;
	DECLARE prevDet INT(10);
	DECLARE suivDet INT(10);
	DECLARE dateDerniereDetection DATETIME;
	DECLARE dateFinPrev DATETIME;
	DECLARE dateDebutSuiv DATETIME;
	DECLARE dateFinMsPrev INT;
	DECLARE dateDebutMsSuiv INT;
	IF (@DISABLE_TRIGGERS IS NULL) THEN
		SELECT animaux.date_derniere_detection FROM animaux WHERE id = NEW.animaux_id INTO dateDerniereDetection;
		IF ( dateDerniereDetection IS NULL OR NEW.date_arrivee > dateDerniereDetection ) THEN
			CALL trouveDetectionAvant(NEW.date_arrivee, NEW.date_arrivee_ms, NEW.animaux_id, NEW.id, prevDet, dateFinPrev, dateFinMsPrev);
			IF ( prevDet IS NOT NULL ) THEN
				CALL supprimeTransitionsApres(prevDet, tmp);
				CALL creeTransition(prevDet, NEW.id, NEW.animaux_id, tmp);
			END IF;
		ELSE
			CALL estRecouvertePar(NEW.date_arrivee, NEW.date_arrivee_ms, NEW.date_depart, NEW.date_depart_ms, NEW.animaux_id, 0, tmp);
			IF ( tmp IS NULL ) THEN
				CALL trouveDetectionAvant(NEW.date_arrivee, NEW.date_arrivee_ms, NEW.animaux_id, NEW.id, prevDet, dateFinPrev, dateFinMsPrev);
				CALL trouveDetectionApres(NEW.date_depart, NEW.date_depart_ms, NEW.animaux_id, NEW.id, suivDet, dateDebutSuiv, dateDebutMsSuiv);			
				IF prevDet IS NULL AND suivDet IS NULL THEN
					CALL supprimeToutesTransitions(NEW.animaux_id);
				ELSE
					CALL supprimePlusieursTransitions(prevDet, suivDet, tmp);
				END IF;	
				IF ( prevDet IS NOT NULL AND suivDet IS NOT NULL AND prevDet = suivDet ) THEN
					IF ( dateFinPrev >= NEW.date_depart AND (dateFinPrev > NEW.date_depart OR dateFinMsPrev > NEW.date_depart_ms) ) THEN
						CALL creeTransition(NEW.id, prevDet, NEW.animaux_id, tmp);
					ELSEIF ( dateDebutSuiv <= NEW.date_arrivee AND (dateDebutSuiv < NEW.date_arrivee OR dateDebutMsSuiv < NEW.date_arrivee_ms) ) THEN
						CALL creeTransition(suivDet, NEW.id, NEW.animaux_id, tmp);
					END IF;
				ELSE
					IF prevDet IS NOT NULL THEN
						CALL creeTransition(prevDet, NEW.id, NEW.animaux_id, tmp);
					END IF;
					IF suivDet IS NOT NULL THEN
						CALL creeTransition(NEW.id, suivDet, NEW.animaux_id, tmp);
					END IF;
				END IF;
			END IF;	
		END IF;	
		IF suivDet IS NULL THEN
			SELECT lieux.id FROM antennes, lieux WHERE antennes.id = NEW.antenne_id AND antennes.lieu = lieux.nom LIMIT 1 INTO tmp;
			UPDATE animaux SET date_derniere_detection = NEW.date_depart, lieu_actuel = tmp WHERE animaux.id = NEW.animaux_id;
		END IF;
	END IF;
END */;;
DELIMITER ;

DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `detections_after_update` AFTER UPDATE ON `detections`
 FOR EACH ROW BEGIN
	DECLARE tmp INT DEFAULT NULL ;
	DECLARE tmp2 INT DEFAULT NULL;
	DECLARE plop INT;
	DECLARE prevDet INT(10);
	DECLARE suivDet INT(10);
	DECLARE datedd DATETIME;
	DECLARE dateFinPrev DATETIME;
	DECLARE dateDebutSuiv DATETIME;
	DECLARE dateFinMsPrev INT;
	DECLARE dateDebutMsSuiv INT;

	DECLARE prevDetAvant INT(10);
	DECLARE suivDetAvant INT(10);
	DECLARE dateddAvant DATETIME;
	DECLARE dateFinPrevAvant DATETIME;
	DECLARE dateDebutSuivAvant DATETIME;
	DECLARE dateFinMsPrevAvant INT;
	DECLARE dateDebutMsSuivAvant INT;


	IF (@DISABLE_TRIGGERS IS NULL) THEN

		
		IF ( OLD.supprime != NEW.supprime AND NEW.supprime = 1 ) THEN
			CALL estRecouvertePar(OLD.date_arrivee, OLD.date_arrivee_ms, OLD.date_depart, OLD.date_depart_ms, OLD.animaux_id, OLD.id, tmp);
			
			IF ( tmp IS NULL ) THEN
				
				CALL trouveDetectionAvant(OLD.date_arrivee, OLD.date_arrivee_ms, OLD.animaux_id, OLD.id, prevDet, dateFinPrev, dateFinMsPrev);
				CALL trouveDetectionApres(OLD.date_depart, OLD.date_depart_ms, OLD.animaux_id, OLD.id, suivDet, dateDebutSuiv, dateDebutMsSuiv);
				IF prevDet IS NULL AND suivDet IS NULL THEN 
					SELECT id FROM detections WHERE animaux_id = OLD.animaux_id AND supprime = 0 AND id != OLD.id ORDER BY date_arrivee ASC, date_arrivee_ms ASC, date_depart ASC, date_depart_ms ASC LIMIT 1 INTO prevDet;
					SELECT id FROM detections WHERE animaux_id = OLD.animaux_id AND supprime = 0 AND id != OLD.id ORDER BY date_depart DESC, date_depart_ms DESC, date_arrivee DESC, date_arrivee_ms DESC LIMIT 1 INTO suivDet;
				END IF;
				CALL creePlusieursTransitions(prevDet, suivDet, OLD.animaux_id, tmp);


				
				IF prevDet IS NOT NULL THEN
					CALL supprimeTransition(prevDet, OLD.id, tmp);
				END IF;
				IF suivDet IS NOT NULL THEN
					CALL supprimeTransition(OLD.id, suivDet, tmp);
				ELSE
										
					SELECT detections.date_depart, lieux.id FROM detections, antennes, lieux WHERE animaux_id = OLD.animaux_id AND detections.id != OLD.id AND detections.supprime = 0 AND antennes.id = detections.antenne_id AND antennes.lieu = lieux.nom ORDER BY date_depart DESC LIMIT 1 INTO datedd, tmp;
					UPDATE animaux SET date_derniere_detection = datedd, lieu_actuel = tmp WHERE animaux.id = NEW.animaux_id;
				END IF;
			END IF;	
		END IF;



		
		IF ( OLD.supprime = 0 AND NEW.supprime = 0 AND (OLD.date_arrivee != NEW.date_arrivee OR OLD.date_arrivee_ms != NEW.date_arrivee_ms OR OLD.date_depart != NEW.date_depart OR OLD.date_depart_ms != NEW.date_depart_ms) ) THEN
			CALL trouveDetectionAvant(OLD.date_arrivee, OLD.date_arrivee_ms, OLD.animaux_id, OLD.id, prevDetAvant, dateFinPrevAvant, dateFinMsPrevAvant);
			CALL trouveDetectionApres(OLD.date_depart, OLD.date_depart_ms, OLD.animaux_id, OLD.id, suivDetAvant, dateDebutSuivAvant, dateDebutMsSuivAvant);
			
			CALL trouveDetectionAvant(NEW.date_arrivee, NEW.date_arrivee_ms, NEW.animaux_id, NEW.id, prevDet, dateFinPrev, dateFinMsPrev);
			CALL trouveDetectionApres(NEW.date_depart, NEW.date_depart_ms, NEW.animaux_id, NEW.id, suivDet, dateDebutSuiv, dateDebutMsSuiv);

			IF ( prevDet != prevDetAvant OR suivDet != suivDetAvant
			     OR (prevDet IS NULL AND prevDetAvant IS NOT NULL)
			     OR (prevDet IS NOT NULL AND prevDetAvant IS NULL)
			     OR (suivDet IS NULL AND suivDetAvant IS NOT NULL)
			     OR (suivDet IS NOT NULL AND suivDetAvant IS NULL)	
			) THEN
				CALL estRecouvertePar(OLD.date_arrivee, OLD.date_arrivee_ms, OLD.date_depart, OLD.date_depart_ms, OLD.animaux_id, OLD.id, tmp);
				CALL estRecouvertePar(NEW.date_arrivee, NEW.date_arrivee_ms, NEW.date_depart, NEW.date_depart_ms, NEW.animaux_id, OLD.id, tmp2);

				IF ( tmp IS NULL AND tmp2 IS NOT NULL ) THEN
					
					CALL supprimeTransition(prevDetAvant, OLD.id, plop);
					CALL supprimeTransition(OLD.id, suivDetAvant, plop);
					IF ( prevDetAvant != prevDet ) THEN
						CALL creePlusieursTransitions(prevDetAvant, prevDet, OLD.animaux_id, plop);
					END IF;
					IF ( suivDetAvant != suivDet ) THEN
						CALL creePlusieursTransitions(suivDet, suivDetAvant, OLD.animaux_id, plop);
					END IF;
				ELSEIF (tmp IS NOT NULL AND tmp2 IS NULL ) THEN
					
					CALL supprimePlusieursTransitions(prevDet, suivDet, plop);
					CALL creeTransition(prevDet, OLD.id, OLD.animaux_id, plop);
					CALL creeTransition(OLD.id, suivDet, OLD.animaux_id, plop);

					
				ELSEIF (tmp IS NULL AND tmp2 IS NULL) THEN

					
					IF ( (prevDet != prevDetAvant 
					     OR (prevDet IS NULL AND prevDetAvant IS NOT NULL)
					     OR (prevDet IS NOT NULL AND prevDetAvant IS NULL) )
					AND
					     (suivDet != suivDetAvant
					     OR (suivDet IS NULL AND suivDetAvant IS NOT NULL)
					     OR (suivDet IS NOT NULL AND suivDetAvant IS NULL)	)
					) THEN	
						CALL supprimeTransition(prevDetAvant, OLD.id, plop);
						CALL supprimeTransition(OLD.id, suivDetAvant, plop);
						CALL creePlusieursTransitions(prevDetAvant, suivDetAvant, OLD.animaux_id, plop);

						CALL supprimePlusieursTransitions(prevDet, suivDet, plop);
						CALL creeTransition(prevDet, OLD.id, OLD.animaux_id, plop);
						CALL creeTransition(OLD.id, suivDet, OLD.animaux_id, plop);

					ELSEIF ( (prevDet != prevDetAvant 
					     OR (prevDet IS NULL AND prevDetAvant IS NOT NULL)
					     OR (prevDet IS NOT NULL AND prevDetAvant IS NULL) )
					) THEN	
						
						IF ( NEW.date_arrivee >= OLD.date_arrivee AND (NEW.date_arrivee > OLD.date_arrivee OR NEW.date_arrivee_ms > OLD.date_arrivee_ms) ) THEN
							
							CALL supprimeTransition(prevDetAvant, OLD.id, plop);
							CALL creePlusieursTransitions(prevDetAvant, OLD.id, OLD.animaux_id, plop);
						ELSEIF ( NEW.date_arrivee <= OLD.date_arrivee AND (NEW.date_arrivee < OLD.date_arrivee OR NEW.date_arrivee_ms < OLD.date_arrivee_ms) ) THEN
							
							CALL supprimePlusieursTransitions(prevDet, OLD.id, plop);
							CALL creeTransition(prevDet, OLD.id, OLD.animaux_id, plop);
						END IF;

					ELSEIF ( (suivDet != suivDetAvant 
					     OR (suivDet IS NULL AND suivDetAvant IS NOT NULL)
					     OR (suivDet IS NOT NULL AND suivDetAvant IS NULL) )
					) THEN
						
						IF ( NEW.date_depart <= OLD.date_depart AND (NEW.date_depart < OLD.date_depart OR NEW.date_depart_ms < OLD.date_depart_ms) ) THEN
							
							CALL supprimeTransition(OLD.id, suivDetAvant, plop);
							CALL creePlusieursTransitions(OLD.id, suivDetAvant, OLD.animaux_id, plop);
						ELSEIF ( NEW.date_depart >= OLD.date_depart AND (NEW.date_depart > OLD.date_depart OR NEW.date_depart_ms > OLD.date_depart_ms) ) THEN
							
							CALL supprimePlusieursTransitions(OLD.id, suivDet, plop);
							CALL creeTransition(OLD.id, suivDet, OLD.animaux_id, plop);
						END IF;
					END IF;


					IF ( OLD.date_depart != NEW.date_depart ) THEN
						
						SELECT detections.date_depart, lieux.id FROM detections, antennes, lieux WHERE animaux_id = OLD.animaux_id AND detections.id != OLD.id AND detections.supprime = 0 AND antennes.id = detections.antenne_id AND antennes.lieu = lieux.nom ORDER BY date_depart DESC LIMIT 1 INTO datedd, tmp;
						UPDATE animaux SET date_derniere_detection = datedd, lieu_actuel = tmp WHERE animaux.id = NEW.animaux_id;
					END IF;
				END IF;
			END IF;
		END IF;
	END IF;
END */;;
DELIMITER ;

DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER detections_before_delete BEFORE DELETE ON detections
FOR EACH ROW BEGIN
	IF (@DISABLE_TRIGGERS IS NULL) THEN
		IF ( OLD.supprime != 1 ) THEN
			CALL raise_application_error('detections_before_delete','Impossible de supprimer une detection directement. Veuillez d abord mettre le champ supprime a 1, puis recommencer');
		END IF;
	END IF;
END */;;
DELIMITER ;

DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER detections_before_insert BEFORE INSERT ON detections
FOR EACH ROW BEGIN
	IF (@DISABLE_TRIGGERS IS NULL) THEN		
		IF (NEW.date_arrivee >= NEW.date_depart) THEN
			IF (NEW.date_arrivee > NEW.date_depart OR NEW.date_arrivee_ms > NEW.date_depart_ms) THEN
				CALL raise_application_error('detections_before_insert','Departure from antenna must be posterior to arrival on antenna');
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
			CALL raise_application_error('detections_before_update','Impossible de modifier l id !');
		END IF;
		
		
		IF (NEW.date_arrivee >= NEW.date_depart) THEN
			IF (NEW.date_arrivee > NEW.date_depart OR NEW.date_arrivee_ms > NEW.date_depart_ms) THEN
				CALL raise_application_error('detections_before_insert','La date de depart de l antenne doit etre posterieure a la date d arrivee sur l antenne');
			END IF;
		END IF;

		IF ( OLD.animaux_id != NEW.animaux_id ) THEN
			CALL raise_application_error('detections_after_update','Impossible de modifier l animal rattache à une detection. Veuillez supprimer et reinserer la detection');
		END IF;
		
		IF ( OLD.supprime != NEW.supprime AND NEW.supprime = 0 ) THEN
			CALL raise_application_error('detections_after_update','Impossible de rescusciter une detection pour le moment. Veuillez la supprimer et la re-inserer');
		END IF;
	END IF;
END */;;
DELIMITER ;

DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER evenement_before_insert BEFORE INSERT ON evenements FOR EACH ROW BEGIN IF NOT NEW.date_fin IS NULL AND NEW.date_debut > NEW.date_fin THEN CALL raise_application_error('evenement_int_before_insert','La date de debut doit etre anterieure a la date de fin'); END IF; END */;;
DELIMITER ;
