# _*_ coding: utf-8 _*_
"""
  Created by yuan on 2020/01/04.
"""
from sqlalchemy import Column, Integer, String, SmallInteger, ForeignKey
from sqlalchemy import or_, and_
from sqlalchemy.orm import relationship
from .base import Base, db

__author__ = 'yuan'

class Keys(Base):
    __tablename__ = 'keys'
    page = Column('page', String(4), primary_key=True)
    keyword = Column('key', String(50))
    pagetitle = Column('keys', String(50))