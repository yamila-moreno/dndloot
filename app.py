from prompt_toolkit import print_formatted_text, prompt, PromptSession
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import Validator
from terminaltables import SingleTable


import dndloot


options = [
    [1, 'Comprar cosas para vivir (alojamiento, comida, transporte...)'],
    [2, 'Comprar objeto para el inventario (pociones, armas)'],
    [3, 'Añadir objetos (gratis) al inventario'],
    [4, 'Añadir dinero a la saca (recompensa, loot, robos...)'],
    [5, 'Usar algún objeto del inventario'],
    [6, 'Ver qué tenemos en el inventario'],
    [7, 'Ver cuánto dinero tenemos'],
    [8, 'Ver el histórico de acciones']
]


def is_valid_money(how_much):
    if not how_much:
        return False

    q, m = how_much[:-2], how_much[-2:]
    return q.isdigit() and m in ['au', 'ag', 'cu']



money_validator = Validator.from_callable(
    is_valid_money,
    error_message='Eso no es dinero',
    move_cursor_to_end=True)


def buy():
    name = prompt('¿En qué os gastáis el dinero? ')
    description = prompt('Cuéntame más ')
    price = prompt('¿Cuánto ha costado? ', validator=money_validator, validate_while_typing=False)
    dndloot.buy(name=name, description=description, price=price)


def buy_to_inventory():
    obj_name = prompt('¿Qué objeto habéis comprado? ')
    description = prompt('Cuéntame más ')
    price = prompt('¿Cuánto ha costado? ', validator=money_validator, validate_while_typing=False)
    owner = prompt('¿Se lo queda alguien? ')
    dndloot.buy_to_inventory(obj_name=obj_name, description=description, price=price, owner=owner)


def add_to_inventory():
    obj_name = prompt('¿Qué objeto habéis conseguido? ')
    description = prompt('Cuéntame más ')
    owner = prompt('¿Se lo queda alguien? ')
    dndloot.add_to_inventory(obj_name=obj_name, description=description, owner=owner)


def is_valid_obj_id(obj_id):
    return obj_id and dndloot.object_exists(obj_id)


def use_inventory():
    validator = Validator.from_callable(
        is_valid_obj_id,
        error_message='Ese objeto no existe',
        move_cursor_to_end=True)

    query_inventory()
    obj_id = int(prompt('¿Qué objeto habéis usado? [elige el id] ', validator=validator, validate_while_typing=False))
    why = prompt('¿Y para qué? ')
    dndloot.use_inventory(obj_id=obj_id, description=why)



def add_to_balance():
    how_much = prompt('¿Cuánto habéis conseguido? ', validator=money_validator, validate_while_typing=False)
    why = prompt('¿Y eso? ')
    dndloot.add_to_balance(price=how_much, description=why)


def query_inventory():
    inventory = dndloot.query_inventory()
    table_options = [['Id', 'Name', 'Description', 'Price', 'Owner']] + inventory
    table = SingleTable(table_options)
    print(table.table)


def query_balance():
    bl = dndloot.query_balance()
    print("Tenemos: {}, {} y {}".format(bl[0], bl[1], bl[2]))


def query_log():
    log = dndloot.query_log()
    table_options = [['Cuándo', 'Qué pasó']] + log
    table = SingleTable(table_options)
    print(table.table)


def is_valid_option(text):
    return (text and text.isdigit() and int(text) >= 0 and int(text) < 9)


def choose_option():
    validator = Validator.from_callable(
        is_valid_option,
        error_message='Elige una opción adecuada',
        move_cursor_to_end=True)

    option = int(prompt('¿Qué queréis esta vez? [0 para ver opciones] ', validator=validator, validate_while_typing=False))

    if option == 0:
        show_options()
    elif option == 1:
        buy()
    elif option == 2:
        buy_to_inventory()
    elif option == 3:
        add_to_inventory()
    elif option == 4:
        add_to_balance()
    elif option == 5:
        use_inventory()
    elif option == 6:
        query_inventory()
    elif option == 7:
        query_balance()
    elif option == 8:
        query_log()


def show_options():
    table_options = [['Id', 'Opción']] + options
    table = SingleTable(table_options)
    print(table.table)


def main():
    session = PromptSession()
    show_options()

    while True:
        try:
            print('\n')
            choose_option()
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

    print('¡Hasta la próxima aventura!')


if __name__ == '__main__':
    main()
