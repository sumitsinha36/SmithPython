from silo_common.logger import minimal_logger
logger = minimal_logger()

# add custom *_db() and iterfetch*() behaviors to silo_cursor
from silo_common.database import silo_cursor
silo_cursor.data_db = classmethod(data_db)
silo_cursor.reporting_db = classmethod(reporting_db)
silo_cursor.iterfetch = iterfetch
silo_cursor.iterfetch_d = iterfetch_d


def reporting_db(cls, cred_details, logger=logger):
    from silo_common.credentials import dbc_from_cred_array
    return dbc_from_cred_array(data_dbc, logger)(cred_details)

