# uname() error回避
import platform
print("platform", platform.uname())

import json
import sqlalchemy
from sqlalchemy import create_engine, insert, delete, update, select
from sqlalchemy.orm import sessionmaker

from db_control.connect_MySQL import engine
from db_control.mymodels_MySQL import Customers


def myinsert(mymodel, values):
    Session = sessionmaker(bind=engine)
    session = Session()

    query = insert(mymodel).values(values)
    try:
        with session.begin():
            session.execute(query)
    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、挿入に失敗しました")
        session.rollback()
    finally:
        session.close()

    return "inserted"


def myselect(mymodel, customer_id):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        with session.begin():
            result = (
                session.query(mymodel)
                .filter(mymodel.customer_id == customer_id)
                .all()
            )

        result_dict_list = []
        for customer_info in result:
            result_dict_list.append({
                "customer_id": customer_info.customer_id,
                "customer_name": customer_info.customer_name,
                "age": customer_info.age,
                "gender": customer_info.gender
            })

        result_json = json.dumps(result_dict_list, ensure_ascii=False)

    except Exception as e:
        print("select failed:", repr(e))
        result_json = None

    finally:
        session.close()

    return result_json


def myselectAll(mymodel):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        with session.begin():
            result = session.execute(select(mymodel)).scalars().all()

        result_dict_list = []
        for customer_info in result:
            result_dict_list.append({
                "customer_id": customer_info.customer_id,
                "customer_name": customer_info.customer_name,
                "age": customer_info.age,
                "gender": customer_info.gender
            })

        result_json = json.dumps(result_dict_list, ensure_ascii=False)

    except Exception as e:
        print("selectAll failed:", repr(e))
        result_json = None

    finally:
        session.close()

    return result_json


def myupdate(mymodel, values):
    Session = sessionmaker(bind=engine)
    session = Session()

    customer_id = values.pop("customer_id")

    query = (
        update(mymodel)
        .where(mymodel.customer_id == customer_id)
        .values(values)
    )

    try:
        with session.begin():
            session.execute(query)
    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、更新に失敗しました")
        session.rollback()
    finally:
        session.close()

    return "updated"


def mydelete(mymodel, customer_id):
    Session = sessionmaker(bind=engine)
    session = Session()

    query = delete(mymodel).where(mymodel.customer_id == customer_id)

    try:
        with session.begin():
            session.execute(query)
    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、削除に失敗しました")
        session.rollback()
    finally:
        session.close()

    return f"{customer_id} is deleted"
