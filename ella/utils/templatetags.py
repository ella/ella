from django.template import TemplateSyntaxError


def parse_getfor(tokens):
    """parse typical ``get_whatever`` **for** ``blah.blah blah`` **as** ``varname`` triplet"""
    tag_name = tokens[0]

    error = TemplateSyntaxError("Second argument in '%s' tag must be 'for'" % tag_name)
    try:
        if tokens[1] != 'for': raise error
    except IndexError:
        raise error

    return tag_name, tokens[2:]


def parse_getforas_triplet(tokens):
    """parse typical ``get_whatever`` **for** ``blah.blah blah`` **as** ``varname`` triplet"""
    tag_name, definition = parse_getfor(tokens[:-2])

    error = TemplateSyntaxError("Last but one argument in '%s' tag must be 'as'" % tag_name)
    try:
        if tokens[-2] != 'as': raise error
    except IndexError:
        raise error

    definition = tokens[2:-2]
    var_name = tokens[-1]

    return tag_name, definition, var_name

