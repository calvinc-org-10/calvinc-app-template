from typing import List, Dict, Any, Callable, Tuple

import decimal
from datetime import datetime, date

# from django.db import models
# from django.db.models import Q, F, Value

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex

from cMenu.utils import QDjangoTableModel

# standard sizes for decimal fields
HunThouMoney2Dec = {'max_digits':  8, 'decimal_places': 2}
HunThouMoney4Dec = {'max_digits': 10, 'decimal_places': 4}
HunMillMoney2Dec = {'max_digits': 11, 'decimal_places': 2}
HunMillMoney4Dec = {'max_digits': 13, 'decimal_places': 4}

# TODO: move to utils
def moneystr(value):
    return f"${value:,.2f}"
def str_to_dec(value):
    return decimal.Decimal(value.replace("$", "").replace(",", ""))

def datestrYMD(value):
    return value.strftime('%Y-%m-%d')
def strYMD_to_date(value):
    return datetime.strptime(value, '%Y-%m-%d').date()

# for converting Django models to Qt models


# I'm quite happy with automaintained pk fields, so I don't specify any (in most cases)


##########################################################
##########################################################


##########################################################
##########################################################