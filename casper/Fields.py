import re

from dateutil.parser import parse

from casper.exceptions.exceptions import FieldCreateFailedException, ValidationFailedException
from casper.widgets.widgets import Widgets, Validator


class BaseField:
    _is_valid = False
    __validated = False
    style = None
    label = None
    name = None

    def as_json(self) -> dict:
        return {
            'field_type': self._get_field_type(self),
            'field_name': self.name,
            'label' : self.label,
            'style' : self.style
        }

    def as_html(self) -> str:
        html = """<div class=''>field_help_text field_label field_html <br> field_error</div>""".format(self.style)
        return self.__html_output(html=html)

    def as_p(self) -> str:
        html = """<p class=''>field_help_text field_label field_html field_error</p>""".format(self.style)
        return self.__html_output(html=html)

    def as_table(self) -> str:
        html = """<div class=''><span>field_help_text field_label field_html field_error</span></div>""".format(self.style)
        return self.__html_output(html=html)

    def as_u(self) -> str:
        html = """<li class=''><span>field_help_text field_label field_html field_error</span></li>""".format(self.style)
        return self.__html_output(html=html)

    def __html_output(self, html) -> str:
        fields = self._get_html_fields()
        return html.replace('field_help_text', fields['help_text']) \
            .replace('field_label', fields['label']) \
            .replace('field_html', fields['html']) \
            .replace('field_error', fields['error'])\
            .replace('None', '')

    def _get_html_fields(self):
        raise NotImplementedError

    def _set_field_name(self, name:str=None) -> None:
        self.name = name
        if not self.label:
            self.label = name

    @staticmethod
    def _get_field_type(field) -> str:
        return ''.join([i for i in (str(type(field)).split('.'))[-1] if i.isalpha()])


class BaseButtonField(BaseField):
    button_type = None
    def __init__(self, *,label:str=None,style:str = None, **kwargs):
        self.label = label
        self.style = style
        super().__init__()

    def as_json(self) -> dict:
        return {**super().as_json(),**{
            'button_type': self.button_type
        }}

    def _get_html_fields(self) -> dict:
        return {
            'html' : """<input class='{}' type='{}' name='{}' id='id_{}' />""".format(self.style, self.button_type, self.name, self.name),
            'error': '',
            'help_text':'',
            'label': ''
        }


class Fields(BaseField):
    _data = None
    _default = None
    _required = False
    _allow_blank = True
    _allow_null = True
    _read_only = False
    _disabled = False
    _regex = None
    _place_holder = None
    help_text = None
    _custom_error = None
    _error = None
    _clean_data = None
    _widget = None
    _auto_focus = False
    _auto_complete = False
    _validators = None

    def __init__(self, data=None, default=None, required: bool=True, allow_null: bool=True,
                 allow_blank: bool=True, read_only: bool=False, label:str=None, regex:str=None,
                 place_holder:str=None, custom_error:str=None, help_text:str=None,
                 widget: Widgets=None,auto_focus:bool=False, auto_complete:bool = False,
                 validators:list = None, style:str=None, disabled:bool=False, **kwargs):
        self._required = required
        self._default = default
        self._allow_blank = allow_blank
        self._allow_null = allow_null
        self._read_only = read_only
        self._disabled = disabled
        self.label = label
        self._regex = regex
        self._place_holder = place_holder
        self._widget = widget
        self._custom_error = custom_error
        self._auto_complete = auto_complete
        self._auto_focus = auto_focus
        self.help_text = help_text
        self._validators = validators
        self.__validate_created_field()
        self.style = style
        super().__init__()
        if data is not None:
            self._set_data(data)






    # def __setattr__(self, key, value):
    #     print(value)


    def __validate_created_field(self) -> None:
        if self._required and self._default:
            raise FieldCreateFailedException('Cannot set required to True when a default is provided')

    def _get_field_data(self):
        if not self._data:
            return self._default
        return self._data

    def _set_data(self, data) -> None:
        self._data = data
        self.validate()

    def _set_default(self, default) -> None:
        self._default = default

    def _set_error(self, error:str) -> None:
        if self._custom_error:
            self._error = error
        else:
            self._error = error

    def validate(self, data=None):
        if data is None:
            data = self._get_field_data()

        #general validation
        form_validator = FormValidator(self)
        try:
            data = form_validator.run(data=data)
        except ValidationFailedException as e:
            error = str(e)
            self._set_error(error)
            raise ValidationFailedException(error)


        # user defined validators
        if self._validators:
            try:
                for validator in self._validators:
                    if isinstance(validator, Validator):
                        data = validator.run(data=data)
            except Exception as e:
                error = str(e)
                self._set_error(error)
                raise ValidationFailedException(error)

        self._clean_data = data
        return self._clean_data

    def as_json(self) -> dict:
        return {**super().as_json(),**{
            'required': self._required,
            'default': self._default,
            'data': self._data,
            'allow_blank':self._allow_blank,
            'allow_null': self._allow_null,
            'read_only': self._read_only,
            'regex': self._regex,
            'place_holder': self._place_holder,
            'help_text':self.help_text,
            'custom_error':self._custom_error,
            'auto_focus': self._auto_focus,
            'auto_complete':self._auto_complete,
        }}

    def _get_base_html_fields(self) -> dict:
        label=None
        if self.label:
            label = self.label.title()
        res = {
            'html': '',
            'error': '',
            'help_text': '',
            'label': """<span><label class='{}' for='{}'>{}</label></span><br>""".format(self.style, self.name,
                                                                                         label)
        }
        if self._error:
            res['error'] = """<span class='form_field_error'>{}<br></span""".format(self._error)
        if self.help_text:
            res['help_text'] = """<span class='form_help_text'>{}<br></span""".format(self.help_text)

        return res

    def _get_html_fields(self) -> dict:
        return self._get_base_html_fields()

    def _get_field_form_defaults(self) -> str:
        defaults = ''
        if self._place_holder:
            defaults += """pattern='{}' """.format(self._regex)

        if self._regex:
            defaults += """placeholder='{}' """.format(self._place_holder)

        if self.name:
            defaults += """id='id_{}' """.format(self.name)

        field_type = self._get_field_type(self)

        if not field_type in ['CheckBoxField','ChoiceField', 'RadioField', 'DataListField']:
            if self._get_field_data():
                defaults += """value='{}' """.format(self._get_field_data())

            if self._auto_complete:
                defaults += """autocomplete='on' """

        if not field_type in ['CheckBoxField','ChoiceField']:
            if self._required:
                defaults += """required='true' """

        if not field_type in ['CheckBoxField', 'RadioField']:
            if self.name:
                defaults += """name='{}' """.format(self.name)

        if self._auto_focus:
            defaults += """autofocus='true' """

        if self._read_only:
            defaults += """readonly='true' """

        if self._disabled:
            defaults += """disabled='true' """

        return defaults


class FormValidator(Validator):

    field = None
    data = None

    def __init__(self, field:Fields):
        self.field = field


    def run(self, data):
        field = self.field
        self.data = data

        if field._required and not data:
            raise ValidationFailedException('This field is required')
        if not field._allow_null and data is None:
            raise ValidationFailedException('This field cannot be null')
        if not field._allow_blank and not data:
            raise ValidationFailedException('This field cannot be blank')

        if data is None:
            return data

        try:
            if field._regex:
                if not re.match(field._regex, data):
                    raise ValidationFailedException("""Value does not match the pattern {}""".format(field._regex))

            field_type = field._get_field_type(field)
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
        choice_keys = []
        for val in choices:
            choice_keys.append(list(val.values())[0])
        for val in data:
            if not val in choice_keys:
                raise ValidationFailedException("""{} is not a valid option for this field""".format(val))
        return str(data)

    @staticmethod
    def _slugify(text):
        non_url_safe = ['"', '#', '$', '%', '&', '+',
                        ',', '/', ':', ';', '=', '?',
                        '@', '[', '\\', ']', '^', '`',
                        '{', '|', '}', '~', "'"]
        translate_table = {ord(char): u'' for char in non_url_safe}
        text = text.translate(translate_table)
        text = u'_'.join(text.split())
        return text

    @staticmethod
    def parse_to_time(data):
        try:
            return parse(str(data))
        except Exception:
            raise ValidationFailedException('Invalid datetime object')

    def CharField(self, data) -> str:
        if getattr(self.field, '_max_length', None) is not None:
            self.check_max_length(data=data, max_length=getattr(self.field, '_max_length'))

        if getattr(self.field, '_min_length', None) is not None:
            self.check_min_length(data=data, min_length=getattr(self.field, '_min_length'))
        return str(data)

    @staticmethod
    def ColorField(data) -> str:
        if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', data):
            raise ValidationFailedException("Invalid hex color")
        return str(data)

    @staticmethod
    def BooleanField(data) -> bool:
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

    def CheckBoxField(self, data) -> str:
        return self.validate_choice_field(data=data, choices=getattr(self.field, '_choices'))

    def ChoiceField(self, data) -> str:
        return self.validate_choice_field(data=data, choices=getattr(self.field, '_choices'))

    def DataListField(self, data) -> str:
        return self.validate_choice_field(data=data, choices=getattr(self.field, '_choices'))

    def DateField(self, data):
        data = self.parse_to_time(data=data)
        if getattr(self.field, '_max_vale', None) is not None:
            self.check_max_value(data=data, max_value=self.parse_to_time(getattr(self.field, '_max_vale')),field='Date value')

        if getattr(self.field, '_min_vale', None) is not None:
            self.check_min_value(data=data, min_value=self.parse_to_time(getattr(self.field, '_min_vale')),field='Date value')

        if data.hour > 0:
            raise ValidationFailedException('Value is not a valid date')
        return data

    def DateTimeField(self, data):
        if not ':' in str(data):
            raise ValidationFailedException('Value is not a valid datetime')

        data = self.parse_to_time(data=data)
        if getattr(self.field, '_max_value', None) is not None:
            self.check_max_value(data=data, max_value=self.parse_to_time(getattr(self.field, '_max_value')))

        if getattr(self.field, '_min_vale', None) is not None:
            self.check_min_value(data=data, min_value=self.parse_to_time(getattr(self.field, '_min_vale')))

        return data

    def DecimalField(self, data):
        if getattr(self.field, '_max_value', None) is not None:
            self.check_max_value(data=data, max_value=getattr(self.field, '_max_value'))

        if getattr(self.field, '_min_vale', None) is not None:
            self.check_min_value(data=data, min_value=getattr(self.field, '_min_vale'))
        try:
            from decimal import Decimal
            return Decimal(str(data).replace(',','.'))
        except Exception:
            raise ValidationFailedException('Invalid numeric value for a decimal')

    @staticmethod
    def EmailField(data) -> str:
        try:
            data = str(data)
            if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", data):
                raise Exception

            from email.utils import parseaddr
            parsed_email = parseaddr(data)
            if parsed_email[1] != data:
                raise Exception
        except Exception:
            raise ValidationFailedException('Invalid email')
        return data

    def IntegerField(self, data) -> int:
        try:
            data = str(data)
            for char in data:
                if not char.isdigit():
                    raise Exception

            data = int(data)
        except Exception:
            raise ValidationFailedException('Invalid integer')

        if getattr(self.field, '_max_value', None) is not None:
            self.check_max_value(data=data, max_value=getattr(self.field, '_max_value'))

        if getattr(self.field, '_min_vale', None) is not None:
            self.check_min_value(data=data, min_value=getattr(self.field, '_min_vale'))
        return int(data)

    def FloatField(self, data) -> float:
        if getattr(self.field, '_max_value', None) is not None:
            self.check_max_value(data=data, max_value=getattr(self.field, '_max_value'))

        if getattr(self.field, '_min_vale', None) is not None:
            self.check_min_value(data=data, min_value=getattr(self.field, '_min_vale'))
        try:
            return float(data)
        except Exception:
            raise ValidationFailedException('Invalid numeric value for a float')

    def RangeField(self, data):
        if getattr(self.field, '_max_value', None) is not None:
            self.check_max_value(data=data, max_value=getattr(self.field, '_max_value'))

        if getattr(self.field, '_min_length', None) is not None:
            self.check_min_value(data=data, min_value=getattr(self.field, '_min_vale'))

        return data

    def RadioField(self, data) -> str:
        return self.validate_choice_field(data=data, choices=getattr(self.field, '_choices'))

    def TimeField(self, data):
        if not re.match(
                r"^((([0]?[1-9]|1[0-2])(:|\.)[0-5][0-9]((:|\.)[0-5][0-9])?( )?(AM|am|aM|Am|PM|pm|pM|Pm))|(([0]?[0-9]|1[0-9]|2[0-3])(:|\.)[0-5][0-9]((:|\.)[0-5][0-9])?))$", str(data)):
            raise ValidationFailedException('Value is not a valid time')

        data = self.parse_to_time(data=data)
        if getattr(self.field, '_max_value', None) is not None:
            self.check_max_value(data=data, max_value=self.parse_to_time(getattr(self.field, '_max_value')))

        if getattr(self.field, '_min_value', None) is not None:
            self.check_min_value(data=data, min_value=self.parse_to_time(getattr(self.field, '_min_vale')))

        return data

    def SlugField(self, data) -> str:
        if getattr(self.field, '_max_length', None) is not None:
            self.check_max_length(data=data, max_length=getattr(self.field, '_max_length'))

        if getattr(self.field, '_min_length', None) is not None:
            self.check_min_length(data=data, min_length=getattr(self.field, '_min_length'))
        return self._slugify(str(data))

    @staticmethod
    def UrlField(data) -> str:

        try:
            data = str(data)
            from urllib.parse import urlparse
            if not data == urlparse(url=data).geturl():
                raise Exception
        except Exception:
            raise ValidationFailedException('Invalid url')

        return data

    @staticmethod
    def UuidField(data) -> str:
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

    def TextField(self, data) -> str:
        if getattr(self.field, '_max_length', None) is not None:
            self.check_max_length(data=data, max_length=getattr(self.field, '_max_length'))

        if getattr(self.field, '_min_length', None) is not None:
            self.check_min_length(data=data, min_length=getattr(self.field, '_min_length'))
        return str(data)

    def PasswordField(self, data) -> str:
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

        if getattr(self.field, '_max_length', None) is not None:
            self.check_max_length(data=data, max_length=getattr(self.field, '_max_length'))

        if getattr(self.field, '_min_length', None) is not None:
            self.check_min_length(data=data, min_length=getattr(self.field, '_min_length'))


        if getattr(self.field, '_must_contain_number', None):
            if not has_number:
                raise ValidationFailedException('Password must contain a numeric character')

        if getattr(self.field, '_must_contain_symbol', None):
            if not has_symbol:
                raise ValidationFailedException('Password must contain a symbol')

        if getattr(self.field, '_must_contain_upper_case', None):
            if not has_upper:
                raise ValidationFailedException('Password must contain an upper case character')

        if getattr(self.field, '_must_contain_lower_case', None):
            if not has_lower:
                raise ValidationFailedException('Password must contain a lower case character')

        return data

    def PhoneField(self, data) -> str:
        try:
            data = str(data)
            if not re.match(
                    r'^\s*(?:\+?(\d{1,3}))?([-. (]*(\d{3})[-. )]*)?((\d{3})[-. ]*(\d{2,4})(?:[-.x ]*(\d+))?)\s*$',
                    data):
                raise Exception
        except Exception:
            raise ValidationFailedException('Invalid Phone')
        if getattr(self.field, '_internationalize', None):
            if data[:1] != '+' and data[:2] != '00':
                raise ValidationFailedException('Phone must be in international format')

        return data

    @staticmethod
    def HiddenField(data):
        return data

