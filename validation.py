"""
A module for validation in lab_4
"""


def ensure_type(annotations):  # пусть будет *cls_inst - кортеж: ((cls1, inst1), (cls2, inst2), ...)
    # Если придираться, здесь instance неверно употреблено. instance = экземпляр класса, это у тебя
    # arg. Здесь более правильное название переменной было бы klass или cls (и так, и так называют)
    # А вместо arg как раз instance.
    for instance, arg in annotations.items():
        if not isinstance(arg, instance):
            raise ValueError


def is_empty(*args):  # более понятное название: ensure_not_empty
    for arg in args:
        if not arg:  # сюда также входит и 0, точно ли так правильно? может != 0 сначала?
            raise ValueError


def is_in(item, sequence):  # более понятное название: ensure_in_seq / ensure_in / ensure_membership
    if item not in sequence:
        raise KeyError


def is_correct_length(sequence, length):  # ensure_length
    if len(sequence) != length:
        raise ValueError
