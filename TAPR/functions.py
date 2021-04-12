# Code to Flash all Error Messages
# taken from Stack Overflow post by i_4_got 27-11-2012
# accessed 1-2-2021
# https://stackoverflow.com/questions/13585663/flask-wtfform-flash-does-not-display-errors

from flask import flash

def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash( (error), 'error')

# end of referenced code.