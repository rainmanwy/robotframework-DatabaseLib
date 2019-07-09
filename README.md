Robot Framework Database Library
==================================

## Introduction
This Library is developed based on [sqlalchemy](https://www.sqlalchemy.org/), it support below features:
* Support sql operations
* Query results could be accessed with column name(Supported by sqlalchemy ResultProxy)
* Support multi database connections
* Support session and ORM(Need be extended by user)  
## Keyword Documentation
[Keyword Documentation](http://rainmanwy.github.io/robotframework-DatabaseLibrary/doc/DatabaseLib.html)
## Installation
```commandline
pip install robotframework-databaselib
```
## How To Extend DatabaseLib
```python
model.py:
from sqlalchemy import BIGINT, INTEGER, STRING
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Student(Base):
    __tablename__ = 'student'

    id = Column(BIGINT, primary_key=True)
    name = Column(STRING(20), nullable=False)
    age = Column(INTEGER, nullable=False)
    

ExtendLib.py:
class StudentKeyword:
    def __init__(self, db):
        self.db = db
    
    @property
    def session(self):
        return self.db.session
    
    @keyword
    def get_student_by_id(self, id):
        student = self.session.query(Student).filter(Student.id==id).one()
        return student


class ExtendLib(DatabaseLib):
    def __init__(self):
        super(ExtendLib, self).__init__([StudentKeyword(self)])
```