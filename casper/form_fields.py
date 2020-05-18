from casper.Fields import Fields, BaseButtonField


class BooleanField(Fields):
    def get_html_fields(self):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ButtonField(BaseButtonField):
    def get_html_fields(self):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.field_type = 'button'


class __Choices(Fields):
    def get_html_fields(self):
        pass

    choices = None
    def __init__(self, choices: list = None, **kwargs):
        super().__init__(**kwargs)
        self.choices = choices

        if not self.choices:
            from casper.exceptions.exceptions import FieldCreateFailedException
            raise FieldCreateFailedException('Required parameter choice is missing')

    def as_json(self) -> {}:
        return {**super().as_json(),**{
            'choices': self.choices,
        }}


class ChoiceField(__Choices):
    def get_html_fields(self):
        pass

    multiple = False
    def __init__(self, multiple: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.multiple = multiple

    def as_json(self) -> {}:
        return {**super().as_json(),**{
            'multiple': self.multiple,
        }}


class CheckBoxField(ChoiceField):
    def get_html_fields(self):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class CharField(Fields):
    max_length = None
    min_length = None
    def __init__(self, max_length: int = None, min_length: int = None, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length
        self.min_length = min_length

    def as_json(self) -> {}:
        return {**super().as_json(),**{
            'max_length': self.max_length,
            'min_length': self.min_length,
        }}

    def get_html_fields(self):
        pass


class ColorField(Fields):

    def get_html_fields(self):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class DateField(Fields):
    max_value = None
    min_value = None
    def __init__(self, max_value: str = None, min_value: str = None, **kwargs):
        super().__init__(**kwargs)
        self.max_value = max_value
        self.min_value = min_value

    def as_json(self) -> {}:
        return {**super().as_json(),**{
            'max_value': self.max_value,
            'min_value': self.min_value,
        }}

    def get_html_fields(self):
        pass


class DataListField(__Choices):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_html_fields(self):
        pass


class DateTimeField(DateField):
    def get_html_fields(self):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class IntegerField(Fields):
    max_value = None
    min_value = None
    step = 0
    def __init__(self, max_value: int = None, min_value: int = None, step:float = 0, **kwargs):
        super().__init__(**kwargs)
        self.max_value = max_value
        self.min_value = min_value
        self.step = step

    def get_html_fields(self):
        pass

    def as_json(self) -> {}:
        return {**super().as_json(),**{
            'max_value': self.max_value,
            'min_value': self.min_value,
            'step': self.step
        }}


class DecimalField(IntegerField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_html_fields(self):
        pass


class EmailField(Fields):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_html_fields(self):
        pass


class FileField(Fields):
    min_size = None
    max_size = None
    file_type = None
    src = None
    def __init__(self, min_size:int = None,  max_size:int = None, file_type:str = None, src:str=None, **kwargs):
        super().__init__(**kwargs)
        self.min_size = min_size
        self.max_size = max_size
        self.file_type = file_type
        self.src = src

    def get_html_fields(self):
        pass


class FloatField(IntegerField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_html_fields(self):
        pass


class HiddenField(Fields):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_html_fields(self):
        pass


class ImageField(FileField):
    width = None
    height = None
    def __init__(self, width:int = None, height:int = None, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        self.file_type = 'image/*'

    def get_html_fields(self):
        pass


class PasswordField(CharField):
    must_contain_number = False
    must_contain_symbol = False
    must_contain_upper_case = False
    must_contain_lower_case = False
    def __init__(self, must_contain_number:bool = False,
                 must_contain_symbol:bool = False,
                 must_contain_upper_case:bool = False,
                 must_contain_lower_case:bool = False, **kwargs):
        super().__init__(**kwargs)
        self.must_contain_number = must_contain_number
        self.must_contain_symbol = must_contain_symbol
        self.must_contain_upper_case = must_contain_upper_case
        self.must_contain_lower_case = must_contain_lower_case


    def as_json(self) -> {}:
        return {**super().as_json(),**{
            'must_contain_number': self.must_contain_number,
            'must_contain_symbol': self.must_contain_symbol,
            'must_contain_upper_case': self.must_contain_upper_case,
            'must_contain_lower_case': self.must_contain_lower_case,
        }}


class PhoneField(CharField):

    internationalize = False
    def __init__(self, internationalize:bool=False, **kwargs):
        super().__init__(**kwargs)
        self.internationalize = internationalize

    def as_json(self) -> {}:
        return {**super().as_json(),**{
            'internationalize': self.internationalize,
        }}

    def get_html_fields(self):
        pass


class RadioField(__Choices):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_html_fields(self):
        pass


class RangeField(IntegerField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_html_fields(self):
        pass


class ResetButtonField(BaseButtonField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.field_type = 'reset'

    def get_html_fields(self):
        pass


class SlugField(CharField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_html_fields(self):
        pass


class SubmitButtonField(BaseButtonField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.field_type = 'submit'

    def get_html_fields(self):
        pass


class TextField(Fields):
    max_length = None
    min_length = None
    cols = None
    rows = None
    def __init__(self, rows:int=None, cols:int = None, max_length: int = None, min_length: int = None, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length
        self.min_length = min_length
        self.cols = cols
        self.rows = rows


    def as_json(self) -> {}:
        return {**super().as_json(),**{
            'max_length': self.max_length,
            'min_length': self.min_length,
            'cols': self.cols,
            'rows': self.rows,
        }}

    def get_html_fields(self):
        pass

class TimeField(DateField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_html_fields(self):
        pass


class UrlField(Fields):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_html_fields(self):
        pass


class UuidField(Fields):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_html_fields(self):
        pass