============================================
HybridHorizon (Extended OpenStack Dashboard)
============================================

Horizon (https://github.com/openstack/horizon/) is a Django-based project aimed
at providing a complete OpenStack Dashboard along with an extensible framework
for building new dashboards from reusable components.

The ``openstack_dashboard`` module is a reference implementation of a Django
site that uses the ``horizon`` app to provide web-based interactions with the
various OpenStack projects.

HybridHorizon is extended form of Horizon which provides access to manage
multiple cloud providers and platforms such as AWS, ComputeNext(Global Cloud
MarketPlace) along with OpenStack. Also HybridHorizon allows to manage multiple
accounts of a provider/platform.

For release management:

 * https://github.com/CloudenablersPvtLtd/HybridHorizon/releases

For issue tracking:

 * https://github.com/CloudenablersPvtLtd/HybridHorizon/issues


Getting Started
===============

For local development, first create a virtualenv for the project.
In the ``tools`` directory there is a script to create one for you:

  $ python tools/install_venv.py

Alternatively, the ``run_tests.sh`` script will also install the environment
for you and then run the full test suite to verify everything is installed
and functioning correctly.

Now that the virtualenv is created, you need to configure your local
environment.  To do this, create a ``local_settings.py`` file in the
``openstack_dashboard/local/`` directory.  There is a
``local_settings.py.example`` file there that may be used as a template.

If all is well you should able to run the development server locally:

  $ tools/with_venv.sh manage.py runserver

or, as a shortcut::

  $ ./run_tests.sh --runserver


Development
===========

For development, start with the getting started instructions above.
Once you have a working virtualenv and all the necessary packages, read on.

If dependencies are added to either ``horizon`` or ``openstack_dashboard``,
they should be added to ``requirements.txt``.

The ``run_tests.sh`` script invokes tests and analyses on both of these
components in its process, and it is what Jenkins uses to verify the
stability of the project. If run before an environment is set up, it will
ask if you wish to install one.

To run the unit tests::

    $ ./run_tests.sh


Deployment
==========

Steps to deploy HybridHorizon using Apache in new ubuntu machine,

Install Prerequisites::

    $ apt-get update

    $ apt-get upgrade

    $ apt-get install python-dev python-pip git apache2

    $ apt-get install mongodb libapache2-mod-wsgi

Clone HybridHorizon Code from GitHub::

    $ git clone https://github.com/CloudenablersPvtLtd/HybridHorizon.git /opt/hybrid_horizon

Install the Requirements::

    $ cd /opt/hybrid_horizon

    $ pip install .

To collect the static js and css files::

    $ python manage.py collectstatic

Notification Configuration::

  Change notification configuration details in
        /opt/hybrid_horizon/config.yaml

Change the settings::

Change the SITE_URL value from 127.0.0.0 into Current IP fo machine.

File Path: /opt/hybrid_horizon/openstack_dashboard/settings.py

   SITE_URL = "http://192.168.1.11:8000"

By default HybridHorizon will run port 8000, If you want to change it

Give the access to directory for Apache user::

    $ chown -R www-data:www-data /opt/hybrid_horizon/

Copy the configuration file and restart the Apache::

    $ cp /opt/hybrid_horizon/hybrid_horizon_apache.conf /etc/apache2/sites-enabled/hybrid_horizon_apache.conf

    $ service apache2 restart

Access the HybridHorizon from your browser with URL::

    http://192.168.1.11:8000
