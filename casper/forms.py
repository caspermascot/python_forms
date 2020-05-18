from casper import BaseField
from casper.exceptions.exceptions import ValidationFailedException
from casper.form_fields import *


class DeclaredFieldsMetaClass(type):
    def __new__(cls, name, bases, attrs):
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

        new_class = super(DeclaredFieldsMetaClass, cls).__new__(cls, name, bases, attrs)

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
    __validated = False
    __errors = {}
    __clean_data = {}
    __initial = {}
    __data = {}
    __style = None
    __method = None
    __url = None


    def __init__(self, data:dict=None, initial:dict=None, **kwargs) -> None:
        self.__fields = self.__get_form_fields()
        self.__form_name = self.__get_form_name()
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
                val.set_field_name(key)

    def __validate(self):
        self.__validated = True
        for field in self.__fields:
            try:
                self.__clean_data[field] = self.__fields[field].validate()
            except ValidationFailedException as e:
                self.__errors[field] = str(e)
            except Exception as e:
                self.__errors[field] = str(e)

        if self.__errors:
            self.valid = False
            self.__clean_data = {}
        else:
            self.valid = True

    def __set_data(self, data:dict) -> None:
        self.__data = data
        for key in data:
            if key in self.__fields:
                self.__fields[key].set_data(data[key])

        self.__validate()

    def __set_initial_data(self, initial:dict) -> None:
        self.__initial = initial
        for key in initial:
            if key in self.__fields:
                self.__fields[key].set_default(initial[key])

    def clean_data(self) -> dict:
        if self.__validated is False:
            raise Exception('not validated')
        return self.__clean_data

    def errors(self) -> dict:
        if self.__validated is False:
            raise Exception('not validated')
        return self.__errors

    def __get_form_fields(self) -> dict:
        return getattr(self,'declared_fields', {})

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

    def __as_html(self):
        return " as html"

    def __as_table(self):
        return "as table"

    def as_json(self) -> list:
        response = []
        form_fields = getattr(self, 'all_form_fields', [])

        for key,val in form_fields:
            response.append(val.as_json())
        return response

    # def __new__(cls, *args, **kwargs):
    #     return cls.__as_html(cls)

    # def __call__(self, *args, **kwargs):
    #     return "call"
    # def __call__(self, *args, **kwargs):
    #     if hasattr(self, 'mymethod') and callable(getattr(self, 'mymethod')):
    #         return self.mymethod()
    #
    # def __getattr__(self, item):
    #     return "called"
        # if hasattr(self, 'mymethod') and callable(getattr(self, 'mymethod')):
        #     return self.mymethod()


class Form(BaseForm, metaclass=DeclaredFieldsMetaClass):
    """a collection"""