from casper.Fields import Fields, BaseButtonField
from casper.exceptions.exceptions import ValidationFailedException


class BooleanField(Fields):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_html_fields(self):
        html = """<span> <input class='{}' type='text' {} /></span>""".format(self.style, super()._get_field_form_defaults())
        res = super()._get_html_fields()
        res['html'] = html
        return res

class ButtonField(BaseButtonField):
    def _get_html_fields(self):
        return super()._get_html_fields()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.field_type = 'button'

class __Choices(Fields):
    def _get_html_fields(self):
        return super()._get_html_fields()

    choices = None
    def __init__(self, choices: list = None, **kwargs):
        super().__init__(**kwargs)
        self.set_choice(choices=choices)


    def set_choice(self, choices:list = None):
        if choices is None or not choices:
            from casper.exceptions.exceptions import FieldCreateFailedException
            raise FieldCreateFailedException('Required parameter choice is missing')

        all_choice = []
        for val in choices:
            if isinstance(val, dict):
                all_choice.append(val)
            else:
                all_choice.append({val:val})

        self.choices = all_choice

    def _get_field_data(self):
        try:
            data = super()._get_field_data()
            if data:
                if isinstance(data,list):
                    return data
                else:
                    return data.split(',')
        except Exception:
            raise ValidationFailedException('Invalid data supplied for choice')


    def as_json(self) -> {}:
        return {**super().as_json(),**{
            'choices': self.choices,
        }}


class ChoiceField(__Choices):
    multiple = False
    def __init__(self, multiple: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.multiple = multiple

    def as_json(self) -> {}:
        return {**super().as_json(),**{
            'multiple': self.multiple,
        }}

    def _get_html_fields(self):
        field_data = super()._get_field_data()
        html = """<span> <select class='{}' type='number' {} """.format(self.style, super()._get_field_form_defaults())
        if self.multiple:
            html += "multiple='true' "
        html += '/>'

        if self.choices:
            for row in self.choices:
                temp = """<option value='{}' """.format(list(row.values())[0])
                if field_data is not None and list(row.values())[0] in field_data:
                    temp += "selected='true' "
                html += """{}>{}</option>""".format(temp, str(list(row.keys())[0]).title())

        html += '</select></span>'

        res = super()._get_base_html_fields()
        res['html'] = html
        return res




class CheckBoxField(ChoiceField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_html_fields(self):
        field_data = super()._get_field_data()
        form_defaults = super()._get_field_form_defaults()


        html = ''
        if self.choices:
            for row in self.choices:
                temp = """<input class = '{}' type='checkbox' {} value='{}' """.format(self.style, form_defaults, list(row.values())[0])

                if self.field_name:
                    if self.multiple:
                        temp += """name='{}[]' """.format(self.field_name)
                    else:
                        temp += """name='{}' """.format(self.field_name)

                if field_data is not None and list(row.values())[0] in field_data:
                    temp += "checked='true' >"

                temp += """<label for='{}' class='{}'>{}</label>""".format(self.field_name, self.style, str(list(row.keys())[0]).title())

                html += temp

        html += '</select></span>'

        res = super()._get_html_fields()
        res['html'] = html
        return res


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

    def _get_html_fields(self):
        html = """<span> <input class='{}' type='text' {} """.format(self.style, super()._get_field_form_defaults())
        if self.max_length:
            html += """minlength='{}' """.format(self.min_length)

        if self.max_length:
            html += """maxlength='{}' """.format(self.max_length)

        html += '/></span>'

        res = super()._get_html_fields()
        res['html'] = html
        return res


class ColorField(Fields):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_html_fields(self):
        html = """<span> <input class='{}' type='color' {} /></span>""".format(self.style, super()._get_field_form_defaults())
        res = super()._get_html_fields()
        res['html'] = html
        return res


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

    def _get_html_fields(self):
        html = """<span> <input class='{}' type='date' {} """.format(self.style, super()._get_field_form_defaults())
        if self.min_value:
            html += """min='{}' """.format(self.min_value)

        if self.max_value:
            html += """max='{}' """.format(self.max_value)

        html += '/></span>'

        res = super()._get_html_fields()
        res['html'] = html
        return res


class DataListField(__Choices):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_html_fields(self):
        field_data = super()._get_field_data()
        html = """<span> <input class='{}' type='text' list='{}' {} temp_value='' />""".format(self.style, self.field_name, super()._get_field_form_defaults())


        temp_value = ''
        html += """<datalist id='{}' >""".format(self.field_name)
        if self.choices:
            for row in self.choices:
                temp = """<option value='{}' >""".format(list(row.values())[0])
                if field_data is not None and list(row.values())[0] in field_data:
                    temp_value = """value='{}'""".format(list(row.values())[0])
                html += temp

        html += '</datalist></span>'

        html = html.replace("temp_value=''", temp_value)
        res = super()._get_base_html_fields()
        res['html'] = html
        return res


class DateTimeField(DateField):
    def _get_html_fields(self):
        res = super()._get_html_fields()
        res['html'] = res['html'].replace("type='date'", "type='datetime-local'")
        return res

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
        if self._get_field_type(self) == 'IntegerField':
            self.step = int(self.step)

    def _get_html_fields(self):
        html = """<span> <input class='{}' type='number' {} """.format(self.style, super()._get_field_form_defaults())
        if self.min_value:
            html += """min='{}' """.format(self.min_value)

        if self.max_value:
            html += """max='{}' """.format(self.max_value)

        if self.step:
            html += """step='{}' """.format(self.step)

        html += '/></span>'

        res = super()._get_html_fields()
        res['html'] = html
        return res

    def as_json(self) -> {}:
        return {**super().as_json(),**{
            'max_value': self.max_value,
            'min_value': self.min_value,
            'step': self.step
        }}


class DecimalField(IntegerField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_html_fields(self):
        return super()._get_html_fields()


class EmailField(Fields):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_html_fields(self):
        html = """<span> <input class='{}' type='email' {} /></span>""".format(self.style, super()._get_field_form_defaults())
        res = super()._get_html_fields()
        res['html'] = html
        return res


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

    def _get_html_fields(self):
        return super()._get_html_fields()


class FloatField(IntegerField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_html_fields(self):
        return super()._get_html_fields()


class HiddenField(Fields):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_html_fields(self):
        html = """<span> <input class='{}' type='hidden' {} /></span>""".format(self.style, super()._get_field_form_defaults())
        res = super()._get_html_fields()
        res['html'] = html
        return res


class ImageField(FileField):
    width = None
    height = None
    def __init__(self, width:int = None, height:int = None, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        self.file_type = 'image/*'

    def _get_html_fields(self):
        return super()._get_html_fields()


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

    def _get_html_fields(self):
        res = super()._get_html_fields()
        res['html'] = res['html'].replace("type='text'", "type='password'")
        return res


class PhoneField(CharField):

    internationalize = False
    def __init__(self, internationalize:bool=False, **kwargs):
        super().__init__(**kwargs)
        self.internationalize = internationalize

    def as_json(self) -> {}:
        return {**super().as_json(),**{
            'internationalize': self.internationalize,
        }}

    def _get_html_fields(self):
        res = super()._get_html_fields()
        res['html'] = res['html'].replace("type='text'", "type='tel'")
        return res


class RadioField(__Choices):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_html_fields(self):
        field_data = super()._get_field_data()
        form_defaults = super()._get_field_form_defaults()


        html = ''
        if self.choices:
            for row in self.choices:
                temp = """<input class = '{}' type='radio' {} value='{}' """.format(self.style, form_defaults, list(row.values())[0])

                if self.field_name:

                        temp += """name='{}' """.format(self.field_name)

                if field_data is not None and list(row.values())[0] in field_data:
                    temp += "checked='true' >"

                temp += """<label for='{}' class='{}'>{}</label>""".format(self.field_name, self.style, str(list(row.keys())[0]).title())

                html += temp

        html += '</select></span>'

        res = super()._get_html_fields()
        res['html'] = html
        return res


class RangeField(IntegerField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_html_fields(self):
        return super()._get_html_fields()


class ResetButtonField(BaseButtonField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.field_type = 'reset'

    def _get_html_fields(self):
        return super()._get_html_fields()


class SlugField(CharField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_html_fields(self):
        return super()._get_html_fields()


class SubmitButtonField(BaseButtonField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.field_type = 'submit'

    def _get_html_fields(self):
        return super()._get_html_fields()


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

    def _get_html_fields(self):
        html = """<span> <textarea class='{}' type='number' {} """.format(self.style, super()._get_field_form_defaults())
        if self.min_length:
            html += """min='{}' """.format(self.min_length)

        if self.max_length:
            html += """max='{}' """.format(self.max_length)

        if self.cols:
            html += """cols='{}' """.format(self.cols)

        if self.rows:
            html += """rows='{}' """.format(self.rows)

        html += '/></textarea></span>'

        res = super()._get_html_fields()
        res['html'] = html
        return res


class TimeField(DateField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_html_fields(self):
        res = super()._get_html_fields()
        res['html'] = res['html'].replace("type='date'", "type='time'")
        return res


class UrlField(Fields):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_html_fields(self):
        html = """<span> <input class='{}' type='url' {} /></span>""".format(self.style, super()._get_field_form_defaults())
        res = super()._get_html_fields()
        res['html'] = html
        return res


class UuidField(Fields):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_html_fields(self):
        html = """<span> <input class='{}' type='text' {} /></span>""".format(self.style, super()._get_field_form_defaults())
        res = super()._get_html_fields()
        res['html'] = html
        return res