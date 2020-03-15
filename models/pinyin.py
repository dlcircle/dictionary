# _*_ coding: utf-8 _*_
"""
  Created by yuan on 2020/01/04.
"""
from sqlalchemy import Column, Integer, String, SmallInteger, ForeignKey
from sqlalchemy import or_, and_
from sqlalchemy.orm import relationship
from .base import Base, db

__author__ = 'yuan'

class PinYin(Base):
    __tablename__ = 'pinyin'
    id = Column(Integer, primary_key=True)
    pinyin = Column('pinyin', String(50), primary_key=True)