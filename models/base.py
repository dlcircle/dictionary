# _*_ coding: utf-8 _*_
"""
  Created by yuan on 2020/01/04.
"""

from contextlib import contextmanager
from datetime import datetime
from flask import current_app, json
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, Pagination as _Pagination, BaseQuery
from sqlalchemy import Column, SmallInteger, Integer, orm, inspect

from time import localtime, strftime, mktime, strptime

__author__ = 'yuan'


class SQLAlchemy(_SQLAlchemy):
	@contextmanager
	def auto_commit(self):
		try:
			yield
			self.session.commit()  # 事务
		except Exception as e:
			self.session.rollback()  # 回滚
			raise e


class Pagination(_Pagination):
	def hide(self, *keys):
		for item in self.items:
			item.hide(*keys)
		return self


class Query(BaseQuery):
	def filter_by(self, **kwargs):
		return super(Query, self).filter_by(**kwargs)

	def paginate(self, page=None, per_page=None, error_out=True, max_per_page=None):
		# 使用paginator记的加上filter_by，用于默认添加status=1
		paginator = BaseQuery.paginate(self, page=page, per_page=per_page, error_out=error_out,
									   max_per_page=max_per_page)
		return Pagination(self,
						  paginator.page,
						  paginator.per_page,
						  paginator.total,
						  paginator.items
						  )


db = SQLAlchemy(query_class=Query)


class Base(db.Model):
	__abstract__ = True

	@orm.reconstructor
	def init_on_load(self):
		# 被隐藏的属性则无法用append方法添加，下面包括都字段表示隐藏
		# self.exclude = ['id', 'status']
		self.exclude = ['status']
		all_columns = inspect(self.__class__).columns.keys()
		self.fields = list(set(all_columns) - set(self.exclude))

	def __getitem__(self, item):
		attr = getattr(self, item)
		# 将字符串转为JSON
		if isinstance(attr, str):
			try:
				attr = json.loads(attr)
			except ValueError:
				pass
		# 处理时间(时间戳转化)
		if item in ['create_time', 'update_time', 'delete_time']:
			attr = strftime('%Y-%m-%d %H:%M:%S', localtime(attr))
		return attr

	@property
	def create_datetime(self):
		if self.create_time:
			return datetime.fromtimestamp(self.create_time)
		else:
			return None

	def get_url(self, url):
		if (self._from == 1):
			return current_app.config['IMG_PREFIX'] + url
		else:
			return url

	def set_attrs(self, **kwargs):
		# 快速赋值
		# 用法: set_attrs(form.data)
		for key, value in kwargs.items():
			if hasattr(self, key) and key != 'id':
				setattr(self, key, value)

	def delete(self):
		self.status = 0

	def keys(self):
		# 在 app/app.py中的 JSONEncoder中的 dict(o)使用
		# 在此处，整合要输出的属性：self.fields
		return self.fields

	def hide(self, *keys):
		for key in keys:
			self.exclude.append(key)
			if key in self.fields:
				self.fields.remove(key)
		return self

	def append(self, *keys):
		for key in keys:
			# self.fields 暂未有key
			# and
			# 在 Model层和 Service层等任意的操作中，已经隐藏的属性无法再添加
			if key not in self.fields and key not in self.exclude:
				self.fields.append(key)
		return self
