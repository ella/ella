"""
This file is for aggregation records from Rating,Agg tables to Agg and TotalRate table
"""

import logging

from datetime import datetime, timedelta
from ella.ratings.models import Rating, Agg, TotalRate

logger = logging.getLogger('ella.ratings')

DELTA_TIME_YEAR = 365*24*60*60
DELTA_TIME_MONTH = 30*24*60*60
DELTA_TIME_WEEK = 7*24*60*60
DELTA_TIME_DAY = 24*60*60

TIMES_ALL = {DELTA_TIME_YEAR : '%Y', DELTA_TIME_MONTH : '%m.%Y', DELTA_TIME_WEEK : '%u.%Y', DELTA_TIME_DAY : '%d.%m.%Y'}
PERIODS = {DELTA_TIME_YEAR : "'y'", DELTA_TIME_MONTH : "'m'", DELTA_TIME_WEEK : "'w'", DELTA_TIME_DAY : "'d'"}

def transfer_agg_to_totalrate():
    """
    Transfer aggregation data from table Agg to table TotalRate
    """
    logger.info("transfer_agg_to_totalrate BEGIN")
    if TotalRate.objects.count() != 0:
        TotalRate.objects.all().delete()
    Agg.objects.agg_to_totalrate()
    logger.info("transfer_agg_to_totalrate END")


def transfer_agg_to_agg():
    """
    aggregation data from table Agg to table Agg
    """
    logger.info("transfer_agg_to_agg BEGIN")
    timenow = datetime.now()
    for t in TIMES_ALL:
        TIME_DELTA = t
        time_agg = timenow - timedelta(seconds=TIME_DELTA)
        Agg.objects.copy_agg_to_agg(time_agg, TIMES_ALL[t], PERIODS[t])
        Agg.objects.filter(time__lte=time_agg, detract=0).delete()
    Agg.objects.agg_assume()
    logger.info("transfer_agg_to_agg END")


def transfer_data():
    """
    transfer data from table Rating to table Agg
    """
    logger.info("transfer_data BEGIN")
    timenow = datetime.now()
    for t in TIMES_ALL:
        TIME_DELTA = t
        time_agg = timenow - timedelta(seconds=TIME_DELTA)
        Rating.objects.copy_rate_to_agg(time_agg, TIMES_ALL[t], PERIODS[t])
        Rating.objects.filter(time__lte=time_agg).delete()
    transfer_agg_to_agg()
    transfer_agg_to_totalrate()
    logger.info("transfer_data END")
    return True



if __name__ == "__main__":
    transfer_data()


