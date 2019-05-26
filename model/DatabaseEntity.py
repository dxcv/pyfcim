

import numpy as np
from sqlalchemy import *
# from sqlclchemy.orm import *


class QBDDB_history_reg():
    def __int__(self, id, bondCode,createDateTime,bid,ofr,
                bid_cleanprice,ofr_cleanprice,last_bid,
                last_ofr,last_bid_cleanprice,last_ofr_cleanprice):
        self.id = bondCode
        self.bondCode = bondCode
        self.createDateTime = createDateTime
        self.bid = bid
        self.ofr = ofr
        self.bid_cleanprice = bid_cleanprice
        self.ofr_cleanprice = ofr_cleanprice
        self.last_bid = last_bid
        self.last_ofr = last_ofr
        self.last_bid_cleanprice = last_bid_cleanprice
        self.last_ofr_cleanprice = last_ofr_cleanprice


# users = Table('QBDDB_history_reg', metadata,Column('user_id', Integer, primary_key=True),
#                Column('name', String(40)),
#                Column('age', Integer),
#                Column('password', String),)