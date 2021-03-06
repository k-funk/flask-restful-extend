# -*- coding: utf-8 -*-

__all__ = ['db', 'Parent', 'Entity', 'default_value']

from sqlalchemy import Column, Integer, String, Float, Boolean, TIMESTAMP, desc, text, or_, ForeignKey
from sqlalchemy.orm import relationship
from flask.ext.sqlalchemy import SQLAlchemy
from flask_restful_extend.model_validates import complex_validates
from project import app
from model_data import sample_data


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

db = SQLAlchemy(app)


class Parent(db.Model):
    id = Column(Integer, primary_key=True)
    cstr = Column(String(50), unique=True, nullable=False)

    entities = relationship('Entity', backref='parent', lazy='dynamic')


def trans_cint_n(value):
    return dict(value=value + 1 if value != 20 else 19)


def valid_cint_n(value, arg1):
    return value % arg1 == 0


default_value = dict(cfl=1.5, cbl=1)


class Entity(db.Model):
    """
    c{column_type}[_n (nullable)]
    """
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('parent.id'), nullable=False)
    cint_n = Column(Integer)

    cstr = Column(String(5), nullable=False)
    cstr_n = Column(String(10))

    cfl = Column(Float, nullable=False, default=default_value['cfl'])
    cfl_n = Column(Float)

    cbl = Column(Boolean, nullable=False, server_default=text(str(default_value['cbl'])))
    cbl_n = Column(Boolean)

    cts = Column(TIMESTAMP, nullable=False)
    cts_n = Column(TIMESTAMP)

    validator = complex_validates({
        # 检查各个内置验证器和自定义验证器是否都能正常工作
        # 通过对 _n 字段也添加一个验证器，可检查验证器能否正确处理 null 值
        'cint_n': [('min', 10), ('max', 20),
                   trans_cint_n,                 # 单数变双数，双数变单数
                   (valid_cint_n, 2)             # 对于双数返回 true，对于单数返回 false。结合 trans_cint_n，
                                                 # 则 cint_n 原始值必须为单数才能通过检查
        ],
        'cstr': [('min_length', 1), ('max_length', 4)],
        'cstr_n': [('match', '^[a-z]+$'), 'trans_upper',
                   ('match', '^[A-Z]+$')],       # 测试 trans_upper 是否成功转换，以及两个验证器间的交接是否正常
    })


# 初始化数据
db.create_all()

for parent in sample_data['parents']:
    p = Parent(**parent)
    db.session.add(p)

for entity in sample_data['normal_entities']:
    e = Entity(**entity)
    db.session.add(e)

db.session.commit()