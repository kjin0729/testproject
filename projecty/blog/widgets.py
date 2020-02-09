from django import forms
from django.urls import reverse_lazy


class SuggestPostWidget(forms.SelectMultiple):
    template_name = 'blog/widgets/suggest.html'

    class Media:
        css = {
            'all': [
                'blog/css/admin_post_form.css',

            ]
        }
        js = ['blog/js/suggest.js']

    def __init__(self, attrs=None):
        super().__init__(attrs)
        if 'class' in self.attrs:
            self.attrs['class'] += ' suggest'
        else:
            self.attrs['class'] = 'suggest'

class UploadableTextarea(forms.Textarea):
    class Media:
        js = [
        'blog/js/csrf.js',
        'blog/js/upload/js',
        ]

    def __init__(self, attrs=None):
        super().__init__(attrs)
        if 'class' in self.attrs:
            self.attrs['class'] += ' uploadable vLargeTextField'
        else:
            self.attrs['class'] = 'uploadable vLargeTextField'
        self.attrs['data-url'] = reverse_lazy('blog:image_upload')


class CustomCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = 'blog/widgets/custom_checkbox.html'
    option_template_name = 'blog/widgets/custom_checkbox_option.html'

    def __init__(self, attrs=None):
        super().__init__(attrs)
        if 'class' in self.attrs:
            self.attrs['class'] += ' custom-checkbox'
        else:
            self.attrs['class'] = 'custom-checkbox'
