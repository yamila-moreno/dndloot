import datetime
import sqlite3

con = sqlite3.connect('dndloot.db')
cursor = con.cursor()

def _calculate_price_in_cu(quantity):
    quantity, money_type = int(quantity[0:-2]), quantity[-2:]
    money_types = {'au': 100, 'ag': 10, 'cu': 1}
    price_in_cu = quantity * money_types[money_type]
    return price_in_cu


def _recalculate_balance(quantity, inc=True):
    au, ag, cu = _get_balance()
    balance_cu = (au * 100) + (ag * 10) + cu

    quantity_cu = _calculate_price_in_cu(quantity)
    if inc:
        new_balance = balance_cu + quantity_cu
    else:
        new_balance = balance_cu - quantity_cu

    au = new_balance // 100
    rest = new_balance % 100
    ag = rest // 10
    rest = rest % 10
    cu = rest

    querystr = "UPDATE balance set au={}, ag={}, cu={}".format(au, ag, cu)
    cursor.execute(querystr)
    con.commit()


def _get_balance():
    querystr = "select au, ag, cu from balance"
    au, ag, cu = cursor.execute(querystr).fetchall()[0]
    return (au, ag, cu)


def object_exists(obj_id):
    querystr = "SELECT * from inventory where id = {}".format(obj_id)
    res = cursor.execute(querystr)
    return len(res.fetchall()) == 1


def add_to_log(description):
    now = datetime.datetime.now().strftime('%d-%m-%Y')
    querystr = "INSERT INTO log(datetime, description) VALUES('{}', '{}')".format(now, description)
    cursor.execute(querystr)
    con.commit()


def buy(name, description, price):
    """
    Compramos cosas para vivir: alojamiento, comida, transporte
    """
    # Añadimos al log
    description = "Compramos {} por {}: {}".format(name, price, description)
    add_to_log(description)

    _recalculate_balance(price, inc=False)


def buy_to_inventory(obj_name, description, price, owner=None):
    """
    Compramos algo para el inventario: pociones, armas, información
    """
    # Añadimos al inventario
    querystr = "INSERT INTO inventory(name, description, price, owner) VALUES('{}', '{}', '{}', '{}')".format(obj_name, description, price, owner)
    cursor.execute(querystr)

    # Añadimos al log
    if owner:
        description = "Compramos {} por {} y se lo quedó {}: {}".format(obj_name, price, owner, description)
    else:
        description = "Compramos {} por {}: {}".format(obj_name, price,  description)
    add_to_log(description)

    _recalculate_balance(price, inc=False)


def add_to_inventory(obj_name, description, owner=None):
    """
    Conseguimos algo para el inventario porque nos lo regalan o lo robamos
    """
    # Añadimos al inventario
    querystr = "INSERT INTO inventory(name, description, price, owner) VALUES('{}', '{}', '{}', '{}')".format(obj_name, description, '0', owner)
    cursor.execute(querystr)

    # Añadimos al log
    if owner:
        description = "Conseguimos {} y se lo quedó {}: {}".format(obj_name, owner, description)
    else:
        description = "Conseguimos {}: {}".format(obj_name, description)
    add_to_log(description)


def use_inventory(obj_id, description):
    """
    Usamos algún objeto del inventario: en una lucha o similar (o nos lo roban)
    """
    querystr = "SELECT name from inventory where id = {}".format(obj_id)
    obj_name = cursor.execute(querystr).fetchall()[0][0]

    # Quitamos el objeto del inventario
    querystr = "DELETE FROM inventory where id = {}".format(obj_id)
    cursor.execute(querystr)

    # Añadimos al log
    description = "Usamos {}: {}".format(obj_name, description)
    add_to_log(description)


def add_to_balance(price, description):
    """
    Conseguimos dinero porque nos lo dan o lo robamos
    """
    # Añadimos al log
    description = "Conseguimos {}: {}".format(price, description)
    add_to_log(description)

    # recalcular el balance
    _recalculate_balance(price)


def query_inventory():
    querystr = "SELECT id, name, description, price, owner from inventory"
    inventory = cursor.execute(querystr).fetchall()
    return inventory

def query_balance():
    au, ag, cu = _get_balance()
    au, ag, cu = '{}au'.format(au), '{}ag'.format(ag), '{}cu'.format(cu)
    return (au, ag, cu)


def query_log():
    querystr = "SELECT datetime, description from log order by id DESC"
    log = cursor.execute(querystr).fetchall()
    return log


### SQLITE TABLES
#
# create table log(id INTEGER PRIMARY KEY, datetime TEXT, description TEXT);
#
# create table inventory(id INTEGER PRIMARY KEY, name TEXT, description TEXT, price TEXT, owner TEXT);
#
# create table balance(au INTEGER, ag INTEGER, cu INTEGER);
#
# INSERT INTO balance(au, ag, cu) values(0,0,0);
