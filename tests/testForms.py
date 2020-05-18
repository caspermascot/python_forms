from casper import forms
import time
from datetime import timedelta

class LoginForm(forms.Form):
    username = forms.CharField(default='tr', max_length=10, custom_error='not valid', required=False)
    email = forms.EmailField(default='ert@ge.c', required=False, label='user_email')
    age = forms.IntegerField(default='5', required=False)
    choice = forms.CheckBoxField(choices=['gender'], default='gender', required=False)
    data_list = forms.DataListField(choices=['firefox', 'chrome'], required=False)
    boolean = forms.BooleanField(required=False,default='No')
    decimal = forms.DecimalField(default='45', required=False)
    date = forms.DateField(default='2020.05.12', required=False)
    date_time = forms.DateTimeField(default='2020.05.12 12:02:22', required=False, max_value='2020.06.20')
    time_field = forms.TimeField(default='12:00:03', required=False)
    password = forms.PasswordField(must_contain_lower_case=True, must_contain_number=True, must_contain_symbol=False,default='Passwprd1',required=False, min_length=5)
    phone = forms.PhoneField(default='0456432234', internationalize=False, required=False)
    url = forms.UrlField(default='www.google.com', required=False)


    class Meta:
        form_method = 'get'
        form_url = '/jkl/'


class RegisterForm(forms.Form):
    email = forms.EmailField()
    date_time = forms.DateTimeField()



start_time = time.monotonic()
data = initial ={'username':'ada','email':'email'}
login = LoginForm()
print(login.is_valid())
print(login.clean_data())
print(login.errors())
print(login.as_json())


end_time = time.monotonic()
print(timedelta(seconds=end_time - start_time))