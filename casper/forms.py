from casper import BaseField
from casper.form_fields import *


class DeclaredFieldsMetaClass(type):
    def __new__(mcs, name, bases, attrs):
        fields = []
        form_fields = []

        for key, value in list(attrs.items()):
            if isinstance(value, BaseField):
                form_fields.append((key, value))

            if isinstance(value, Fields):
                fields.append((key, value))
                attrs.pop(key)
        attrs['declared_fields'] = dict(fields)
        attrs['form_name'] = name
        attrs['all_form_fields'] = form_fields


        if 'Meta' in attrs:
            meta_object = vars(attrs['Meta'])
            supported_meta = ['form_url', 'form_style', 'form_method']
            for val in supported_meta:
                if val in meta_object:
                    attrs['meta_'+val] = meta_object[val]

        new_class = super(DeclaredFieldsMetaClass, mcs).__new__(mcs, name, bases, attrs)

        # Walk through the MRO.
        declared_fields = {}
        for base in reversed(new_class.__mro__):
            # Collect fields from base class.
            if hasattr(base, 'declared_fields'):
                declared_fields.update(base.declared_fields)


            # Field shadowing.
            for attr, value in base.__dict__.items():
                if value is None and attr in declared_fields:
                    declared_fields.pop(attr)

        new_class.base_fields = declared_fields
        new_class.declared_fields = declared_fields

        return new_class


class BaseForm:
    valid = False
    __form_name = None
    __fields = None
    __base_form_fields = None
    __validated = False
    __errors = {}
    __clean_data = {}
    __initial = {}
    __data = {}
    __style = None
    __method = None
    __url = None


    def __init__(self, data:dict=None, initial:dict=None) -> None:
        self.__fields = self.__get_form_fields()
        self.__form_name = self.__get_form_name()
        self.__base_form_fields = self.__get_base_fields()
        self.__method = self.__get_form_method()
        self.__url = self.__get_form_url()
        self.__set_field_names()

        if data:
            self.__set_data(data=data)
        if initial:
            self.__set_initial_data(initial=initial)


    def is_valid(self):
        if self.__validated is False:
            self.__validate()
        return self.valid

    def __set_field_names(self):
        form_fields = getattr(self, 'all_form_fields',[])
        for key,val in form_fields:
            if isinstance(val, BaseField):
                val._set_field_name(key)

    def __get_base_fields(self) -> list:
        fields = getattr(self, 'all_form_fields', [])
        # form_fields = getattr(self, 'all_form_fields', [])
        for key, val in fields:
            setattr(self,key,val)

        return fields

    def __validate(self):
        self.__validated = True
        for field in self.__fields:
            try:
                self.__clean_data[field] = self.__fields[field].validate()
                field_custom_validation = """validate_{}""".format(field)
                if hasattr(self, field_custom_validation) and callable(getattr(self, field_custom_validation)):
                    func = getattr(self, field_custom_validation)
                    try:
                        self.__clean_data[field] = func()
                    except ValidationFailedException as e:
                        error = str(e)
                        self.__fields[field]._set_error(error)
                        raise ValidationFailedException(error)
            except ValidationFailedException as e:
                self.__errors[field] = str(e)
            except Exception as e:
                self.__errors[field] = str(e)

        if self.__errors:
            self.valid = False
            self.__clean_data = {}
        else:
            self.valid = True

    def data(self) -> dict:
        return self.__data

    def __set_data(self, data:dict) -> None:
        self.__data = data
        for key in data:
            if key in self.__fields:
                self.__fields[key]._set_data(data[key])

        self.__validate()

    def initial_data(self) -> dict:
        return self.__initial

    def __set_initial_data(self, initial:dict) -> None:
        self.__initial = initial
        for key in initial:
            if key in self.__fields:
                self.__fields[key]._set_default(initial[key])

    def clean_data(self) -> dict:
        if self.__validated is False:
            raise Exception('not validated')
        return self.__clean_data

    def errors(self) -> dict:
        if self.__validated is False:
            raise Exception('not validated')
        return self.__errors

    def __get_form_fields(self) -> list:
        return getattr(self,'declared_fields', [])

    def __get_form_name(self) -> str:
        return getattr(self,'form_name', 'form')

    def __get_form_method(self) -> str:
        return getattr(self, 'meta_form_method','post')

    def __get_form_url(self) -> str:
        return getattr(self, 'meta_form_url','')

    def __get_form_style(self) -> str:
        return getattr(self, 'meta_form_style','')

    def __as_p(self):
        return "as p"

    def as_html(self) -> str:
        tail = ''
        html = ''
        for key, val in self.__base_form_fields:
            if isinstance(val, SubmitButtonField) or isinstance(val, ResetButtonField):
                tail = tail + val.as_html()
            else:
                html = html + val.as_html()
        return (self.__get_form_output_header() + html + tail + self.__get_html_output_base()).replace('None','')

    def as_table(self):
        return "as table"

    def as_json(self) -> list:
        response = []

        for key,val in self.__base_form_fields:
            response.append(val.as_json())
        return response

    def __get_form_output_header(self) -> str:
        has_file = False
        replace = ''
        html = """<form class='{}' action='{}' method='{}' name='{}' id='id_{}' form_enctype>"""\
            .format(self.__style, self.__url, self.__method, self.__form_name, self.__form_name)

        for key,val in self.__base_form_fields:
            if isinstance(val, FileField):
                has_file = True
        if has_file:
            replace = 'enctype="multipart/form-data"'
        return html.replace('form_enctype', replace)

    def __get_html_output_base(self) -> str:
        has_submit = False
        replace = ''
        html = """ form_submit </form>"""
        for key,val in self.__base_form_fields:
            if isinstance(val, SubmitButtonField):
                has_submit = True
        if not has_submit:
            replace = '<input type="submit" value="Submit">'
        return html.replace('form_submit', replace)

    @staticmethod
    def __send_html_output(self):
        return self.as_html(self)


    def __getattr__(self, item=None):
        if item is None:
            return self.as_html()
        for key, val in self.__base_form_fields:
            if key == item:
                return val.as_html()




class Form(BaseForm, metaclass=DeclaredFieldsMetaClass):
    """form to be extended by all forms"""