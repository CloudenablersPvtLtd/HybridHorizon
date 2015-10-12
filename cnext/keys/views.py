from horizon import messages
from django.utils import translation
from django.shortcuts import render, redirect
from signup.models import Key, KeyForm
import logging
LOG = logging.getLogger(__name__)

def manage_keys(request):
    user, created = Key.objects.get_or_create(name=request.user, defaults={'publickey': '', 'secretkey' : ''})
    if request.method == 'POST':
        form = KeyForm(request.POST, instance=user)
        if form.is_valid() and form.has_changed():
            # do something with the formset.cleaned_data
            form.save()
            messages.success(request, translation.ugettext("Keys saved."))
        return redirect(request.build_absolute_uri())
    else:
        form = KeyForm(instance=user)
    return render(request, 'cnext/keys/manage.html', {'form': form})
