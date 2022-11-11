def missing_data(data):
    if data is None or any(x == str(data).upper() for x in ("I", "", "N/A", "NA", "NONE", "NEANT", "NÉANT", "(INCONNU)", "0", "")):
        return True
    else:
        return False

def birth_year_determination(rfid_date,rfid_stage):
    if rfid_stage[1] == "P":
        if rfid_stage == "'P-Brooding'":
            birth_year = int(rfid_date.year)
        else:
            if rfid_date.month > 9:
                birth_year = int(rfid_date.year)
            else:
                birth_year = int(rfid_date.year) - 1
        birth_year_type = "'obs'"
    else:
        birth_year = 'NULL'
        birth_year_type = 'NULL'
    return birth_year, birth_year_type

def determine_year(date):
    if date.month > 9:
        year = int(date.year) + 1
    else:
        year = int(date.year)
    return year

def get_rfidate(rfid, date):
    rfidate = rfid.replace(" ", "")
    if str(date)=="0000-00-00":
        year = "1970"
        month = "01"
        day = "01"
        rfidate += "_" + year + "_" + month + "_" + day
    else:
        year = str(date.year)
        month = str(date.month)
        day = str(date.day)
        rfidate += "_" + year + "_" + month + "_" + day
    return rfidate
