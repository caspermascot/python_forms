import unittest

from casper import forms


class TestForms(unittest.TestCase):
    '''base test class'''

class ContactForm(forms.Form):
    id = forms.IntegerField(default=1, required=False)
    email = forms.EmailField(allow_null=False, allow_blank=False)
    website = forms.UrlField(required=False)
    message = forms.TextField()
    submit = forms.SubmitButtonField()

    class Meta:
        form_method = 'post'
        form_url = '/contact/'

class TestContactForm(TestForms):

    @staticmethod
    def get_contact_form():
        return ContactForm()


    def test_contact_with_initial(self):
        # this test should pass
        initial_data = {'id':4, 'email': 'someone@example.com', 'website':'www.some_website.com','message':'hello'}
        contact_form = ContactForm(initial=initial_data)
        self.assertTrue(contact_form.is_valid())

        contact_form.is_valid()
        cleaned_data = contact_form.clean_data()
        self.assertEqual(initial_data['id'], cleaned_data['id'])
        self.assertEqual({}, contact_form.errors())
