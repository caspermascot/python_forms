import re

from dateutil.parser import parse

from casper.exceptions.exceptions import FieldCreateFailedException, ValidationFailedException
from casper.widgets.widgets import Widgets, Validator


class BaseField:
    is_valid = False
    __validated = False
    style = None
    label = None
    field_name = None

    def as_json(self) -> {}:
        return {
            'field_type': self.get_field_type(self),
            'field_name': self.field_name,
            'label' : self.label,
            'style' : self.style
        }

    def as_html(self) -> str:
        return " "

    def as_p(self) -> str:
        return " "

    def get_html_fields(self):
        raise NotImplementedError

    def set_field_name(self, name:str=None) -> None:
        self.field_name = name
        if not self.label:
            self.label = name

    @staticmethod
    def get_field_type(field) -> str:
        return ''.join([i for i in (str(type(field)).split('.'))[-1] if i.isalpha()])



class BaseButtonField(BaseField):
    button_type = None
    def __init__(self, label:str=None,style:str = None, **kwargs):
        self.label = label
        self.style = style
        super().__init__()

    def as_json(self) -> {}:
        return {**super().as_json(),**{
            'button_type': self.button_type
        }}

    def get_html_fields(self):
        return {
            'html' : """<input class='{}' type='{}' name='{}' id='id_{}' />""".format(self.style, self.button_type, self.field_name, self.field_name),
            'error': '',
            'help_text':'',
            'label': ''
        }


class Fields(BaseField):
    data = None
    default = None
    required = False
    allow_blank = True
    allow_null = True
    read_only = False
    regex = None
    place_holder = None
    help_text = None
    custom_error = None
    error = None
    clean_data = None
    widget = None
    auto_focus = False
    auto_complete = False
    validators = None

    def __init__(self, default=None, required: bool=True, allow_null: bool=True,
                 allow_blank: bool=True, read_only: bool=False, label:str=None, regex:str=None,
                 place_holder:str=None, custom_error:str=None, help_text:str=None,
                 widget: Widgets=None,auto_focus:bool=False, auto_complete:bool = False,
                 validators:list = None, style:str=None, **kwargs):
        self.required = required
        self.default = default
        self.allow_blank = allow_blank
        self.allow_null = allow_null
        self.read_only = read_only
        self.label = label
        self.regex = regex
        self.place_holder = place_holder
        self.widget = widget
        self.custom_error = custom_error
        self.auto_complete = auto_complete
        self.auto_focus = auto_focus
        self.help_text = help_text
        self.validators = validators
        self.__validate_created_field()
        self.style = style

        super().__init__()



    def __validate_created_field(self):
        if self.required and self.default:
            raise FieldCreateFailedException('Cannot set required to True when a default is provided')


    def get_field_data(self):
        if not self.data:
            return self.default
        return self.data


    def set_data(self, data) -> None:
        self.data = data


    def set_default(self, default) -> None:
        self.default = default


    def validate(self, data=None):
        if data is None:
            data = self.get_field_data()

        #general validation
        form_validator = FormValidator(self)
        try:
            data = form_validator.run(data=data)
        except ValidationFailedException as e:
            if self.custom_error is not None:
                self.error = self.custom_error
                raise ValidationFailedException(self.custom_error)
            else:
                self.error = str(e)
                raise ValidationFailedException(str(e))


        if self.validators:
            for validator in self.validators:
                if isinstance(validator, Validator):
                    data = validator.run(data=data)
        self.clean_data = data
        return self.clean_data

    def as_json(self) -> {}:
        return {**super().as_json(),**{
            'required': self.required,
            'default': self.default,
            'allow_blank':self.allow_blank,
            'allow_null': self.allow_null,
            'read_only': self.read_only,
            'regex': self.regex,
            'place_holder': self.place_holder,
            'help_text':self.help_text,
            'custom_error':self.custom_error,
            'auto_focus': self.auto_focus,
            'auto_complete':self.auto_complete,
        }}

    def get_html_fields(self):
        res = {
            'html' : '',
            'error': '',
            'help_text':'',
            'label': """<span><label class='{}' for='{}'>{}</label></span>""".format(self.style, self.field_name, self.label)
        }
        if self.error:
            res['error'] = """<span class='form_field_error'>{}</span""".format(self.error)
        if self.help_text:
            res['error'] = """<span class='form_help_text'>{}</span""".format(self.help_text)

        return res


class FormValidator(Validator):

    field = None
    data = None

    def __init__(self, field:Fields):
        self.field = field


    def run(self, data):
        field = self.field
        self.data = data

        if field.required and not data:
            raise ValidationFailedException('This field is required')
        if not field.allow_null and data is None:
            raise ValidationFailedException('This field cannot be null')
        if not field.allow_blank and not data:
            raise ValidationFailedException('This field cannot be blank')

        if data is None:
            return data

        try:
            if field.regex:
                if not re.match(field.regex, data):
                    raise ValidationFailedException("""Value does not match the pattern {}""".format(field.regex))

            field_type = field.get_field_type(field)
            if hasattr(self, field_type) and callable(getattr(self, field_type)):
                func = getattr(self, field_type)
                return func(data)
        except Exception as e:
            raise ValidationFailedException(str(e))
        return data


    @staticmethod
    def check_max_length(data, max_length) -> None:
        if len(data) > max_length:
            raise ValidationFailedException("""Length cannot be more than {}""".format(max_length))

    @staticmethod
    def check_min_length(data, min_length) -> None:
        if len(data) < min_length:
            raise ValidationFailedException("""Length cannot be less than {}""".format(min_length))

    @staticmethod
    def check_max_value(data, max_value, field='Value') -> None:
        if data > max_value:
            raise ValidationFailedException("""{} cannot be more than {}""".format(field, max_value))

    @staticmethod
    def check_min_value(data, min_value, field='Value') -> None:
        if data < min_value:
            raise ValidationFailedException("""{} cannot be less than {}""".format(field, min_value))

    @staticmethod
    def validate_choice_field(data, choices) -> str:
        data_as_list = str(data).split(',')
        for val in data_as_list:
            if not val in choices:
                raise ValidationFailedException("""{} is not a valid option for this field""".format(val))
        return str(data)

    @staticmethod
    def parse_to_time(data):
        try:
            return parse(str(data))
        except Exception:
            raise ValidationFailedException('Invalid datetime object')

    def CharField(self, data):
        if getattr(self.field, 'max_length', None) is not None:
            self.check_max_length(data=data, max_length=getattr(self.field, 'max_length'))

        if getattr(self.field, 'min_length', None) is not None:
            self.check_min_length(data=data, min_length=getattr(self.field, 'min_length'))
        return str(data)

    @staticmethod
    def ColorField(data):
        if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', data):
            raise ValidationFailedException("Invalid hex color")
        return str(data)

    @staticmethod
    def BooleanField(data):
        try:
            if type(data) == str:
                data = data.lower()

            if not data in ['true', 'false', True, False, 'ok', 'yes', 'no']:
                raise Exception
            bool_options = {
                'true':True,
                'false': False,
                True: True,
                False: False,
                'ok': True,
                'yes': True,
                'no': False
            }

            return bool_options[data]

        except Exception:
            raise ValidationFailedException('Invalid Boolean')

    def CheckBoxField(self, data):
        return self.validate_choice_field(data=data, choices=getattr(self.field, 'choices'))

    def ChoiceField(self, data):
        return self.validate_choice_field(data=data, choices=getattr(self.field, 'choices'))

    def DateField(self, data):
        data = self.parse_to_time(data=data)
        if getattr(self.field, 'max_value', None) is not None:
            self.check_max_value(data=data, max_value=self.parse_to_time(getattr(self.field, 'max_value')),field='Date value')

        if getattr(self.field, 'min_value', None) is not None:
            self.check_min_value(data=data, min_value=self.parse_to_time(getattr(self.field, 'min_value')),field='Date value')

        if data.hour > 0:
            raise ValidationFailedException('Value is not a valid date')
        return data

    def DateTimeField(self, data):
        if not ':' in str(data):
            raise ValidationFailedException('Value is not a valid datetime')

        data = self.parse_to_time(data=data)
        if getattr(self.field, 'max_value', None) is not None:
            self.check_max_value(data=data, max_value=self.parse_to_time(getattr(self.field, 'max_value')))

        if getattr(self.field, 'min_value', None) is not None:
            self.check_min_value(data=data, min_value=self.parse_to_time(getattr(self.field, 'min_value')))

        return data

    def DecimalField(self, data):
        if getattr(self.field, 'max_value', None) is not None:
            self.check_max_value(data=data, max_value=getattr(self.field, 'max_value'))

        if getattr(self.field, 'min_value', None) is not None:
            self.check_min_value(data=data, min_value=getattr(self.field, 'min_value'))
        try:
            from decimal import Decimal
            return Decimal(str(data).replace(',','.'))
        except Exception:
            raise ValidationFailedException('Invalid numeric value for a decimal')

    @staticmethod
    def EmailField(data):
        try:
            data = str(data)
            from email.utils import parseaddr
            parsed_email = parseaddr(data)
            if parsed_email[1] != data:
                raise Exception
        except Exception:
            raise ValidationFailedException('Invalid email')
        return data

    def IntegerField(self, data):
        try:
            data = str(data)
            for char in data:
                if not char.isdigit():
                    raise Exception

            data = int(data)
        except Exception:
            raise ValidationFailedException('Invalid integer')

        if getattr(self.field, 'max_value', None) is not None:
            self.check_max_value(data=data, max_value=getattr(self.field, 'max_value'))

        if getattr(self.field, 'min_value', None) is not None:
            self.check_min_value(data=data, min_value=getattr(self.field, 'min_value'))
        return int(data)

    def FloatField(self, data):
        if getattr(self.field, 'max_value', None) is not None:
            self.check_max_value(data=data, max_value=getattr(self.field, 'max_value'))

        if getattr(self.field, 'min_value', None) is not None:
            self.check_min_value(data=data, min_value=getattr(self.field, 'min_value'))
        try:
            return float(data)
        except Exception:
            raise ValidationFailedException('Invalid numeric value for a float')

    def RangeField(self, data):
        if getattr(self.field, 'max_value', None) is not None:
            self.check_max_value(data=data, max_value=getattr(self.field, 'max_value'))

        if getattr(self.field, 'min_length', None) is not None:
            self.check_min_value(data=data, min_value=getattr(self.field, 'min_value'))

        return data

    def RadioField(self, data):
        return self.validate_choice_field(data=data, choices=getattr(self.field, 'choices'))

    def TimeField(self, data):
        if not re.match(
                r"^((([0]?[1-9]|1[0-2])(:|\.)[0-5][0-9]((:|\.)[0-5][0-9])?( )?(AM|am|aM|Am|PM|pm|pM|Pm))|(([0]?[0-9]|1[0-9]|2[0-3])(:|\.)[0-5][0-9]((:|\.)[0-5][0-9])?))$", str(data)):
            raise ValidationFailedException('Value is not a valid time')

        data = self.parse_to_time(data=data)
        if getattr(self.field, 'max_value', None) is not None:
            self.check_max_value(data=data, max_value=self.parse_to_time(getattr(self.field, 'max_value')))

        if getattr(self.field, 'min_value', None) is not None:
            self.check_min_value(data=data, min_value=self.parse_to_time(getattr(self.field, 'min_value')))

        return data

    def SlugField(self, data):
        if getattr(self.field, 'max_length', None) is not None:
            self.check_max_length(data=data, max_length=getattr(self.field, 'max_length'))

        if getattr(self.field, 'min_length', None) is not None:
            self.check_min_length(data=data, min_length=getattr(self.field, 'min_length'))
        return str(data)

    @staticmethod
    def UrlField(data):
        try:
            data = str(data)
            if not re.match(
                    r'((http://|https://|ftp\://)|(www.))+(([a-zA-Z0-9\.-]+\.[a-zA-Z]{2,4})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(/[a-zA-Z0-9%:/-_\?\.\'~]*)?',
                    data):
                raise Exception
        except Exception:
            raise ValidationFailedException('Invalid url')

        return data

    @staticmethod
    def UuidField(data):
        try:
            data = str(data)
            if not re.match(
                    r'[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}',
                    data):
                raise Exception
        except Exception:
            raise ValidationFailedException('Invalid uuid')

        return data

    def FileField(self, data):
        return data

    def ImageField(self, data):
        return data

    def TextField(self, data):
        if getattr(self.field, 'max_length', None) is not None:
            self.check_max_length(data=data, max_length=getattr(self.field, 'max_length'))

        if getattr(self.field, 'min_length', None) is not None:
            self.check_min_length(data=data, min_length=getattr(self.field, 'min_length'))
        return str(data)

    def PasswordField(self, data):
        has_number = has_upper = has_lower = has_symbol = False
        try:
            data = str(data)
            for char in data:
                if char.isdigit():
                    has_number = True
                if char.islower():
                    has_lower = True
                if char.isupper():
                    has_upper = True
                if not char.isalnum():
                    has_symbol = True
        except Exception:
            raise ValidationFailedException('Invalid password')

        if getattr(self.field, 'max_length', None) is not None:
            self.check_max_length(data=data, max_length=getattr(self.field, 'max_length'))

        if getattr(self.field, 'min_length', None) is not None:
            self.check_min_length(data=data, min_length=getattr(self.field, 'min_length'))


        if getattr(self.field, 'must_contain_number', None):
            if not has_number:
                raise ValidationFailedException('Password must contain a numeric character')

        if getattr(self.field, 'must_contain_symbol', None):
            if not has_symbol:
                raise ValidationFailedException('Password must contain a symbol')

        if getattr(self.field, 'must_contain_upper_case', None):
            if not has_upper:
                raise ValidationFailedException('Password must contain an upper case character')

        if getattr(self.field, 'must_contain_lower_case', None):
            if not has_lower:
                raise ValidationFailedException('Password must contain a lower case character')

        return data

    def PhoneField(self, data):
        try:
            data = str(data)
            if not re.match(
                    r'^\s*(?:\+?(\d{1,3}))?([-. (]*(\d{3})[-. )]*)?((\d{3})[-. ]*(\d{2,4})(?:[-.x ]*(\d+))?)\s*$',
                    data):
                raise Exception
        except Exception:
            raise ValidationFailedException('Invalid Phone')
        if getattr(self.field, 'internationalize', None):
            if data[:1] != '+' and data[:2] != '00':
                raise ValidationFailedException('Phone must be in international format')

        return data

    @staticmethod
    def HiddenField(data):
        return data

