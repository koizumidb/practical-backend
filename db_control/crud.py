# db_control/crud.py
# pandas を使わずに SQLAlchemy だけで JSON を返す版

# uname() error回避
import platform
print("platform", platform.uname())

import json
import sqlalchemy
from sqlalchemy import insert, delete, update, select
from sqlalchemy.orm import sessionmaker

from db_control.connect_MySQL import engine


def myinsert(mymodel, values: dict):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        with session.begin():
            session.execute(insert(mymodel).values(values))
        return "inserted"
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        return "IntegrityError"
    finally:
        session.close()


def myselect(mymodel, customer_id: str):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        with session.begin():
            rows = session.query(mymodel).filter(mymodel.customer_id == customer_id).all()

        result = []
        for r in rows:
            # モデルの列を辞書化（Customers 以外でも動く）
            d = {c.name: getattr(r, c.name) for c in r.__table__.columns}
            result.append(d)

        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": repr(e)}, ensure_ascii=False)
    finally:
        session.close()


def myselectAll(mymodel):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        with session.begin():
            rows = session.execute(select(mymodel)).scalars().all()

        result = []
        for r in rows:
            d = {c.name: getattr(r, c.name) for c in r.__table__.columns}
            result.append(d)

        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": repr(e)}, ensure_ascii=False)
    finally:
        session.close()


def myupdate(mymodel, values: dict):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        customer_id = values.pop("customer_id")
        with session.begin():
            session.execute(
                update(mymodel)
                .where(mymodel.customer_id == customer_id)
                .values(values)
            )
        return "put"
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        return "IntegrityError"
    except Exception as e:
        session.rollback()
        return repr(e)
    finally:
        session.close()


def mydelete(mymodel, customer_id: str):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        with session.begin():
            session.execute(delete(mymodel).where(mymodel.customer_id == customer_id))
        return f"{customer_id} is deleted"
    except Exception as e:
        session.rollback()
        return repr(e)
    finally:
        session.close()
