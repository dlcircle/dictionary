# _*_ coding: utf-8 _*_
"""
  Created by yuan on 2020/01/04.
"""
from sqlalchemy import Column, Integer, String, SmallInteger, ForeignKey
from sqlalchemy import or_, and_
from sqlalchemy.orm import relationship
from .base import Base, db

__author__ = 'yuan'

class Words(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True)
    hanzi = Column('hanzi', String(11))
    pinyin = Column('pinyin', String(50))
    bihua = Column('bihua', Integer)
    bushou = Column('bushou', String(50))
    jianti = Column('jianti', String(50))
    fanti = Column('fanti', String(50))
    shiyi = Column('shiyi', String(3000))
    page = Column('page', String(50))
    check = Column('check', SmallInteger)

    pinyins = relationship("PinYin", order_by="PinYin.py", backref="word")

    def keys(self):
        self.append('py1')
        return self.fields

    @property
    def py1(self):
      if len(self.pinyins) >= 1 :
        return self.pinyins[0].py
      return ''

class PinYin(Base):
    __tablename__ = 'pinyin'
    id = Column(Integer, ForeignKey('words.id'), primary_key=True)
    py = Column('py', String(50), primary_key=True)