from django.db import migrations


def create_production_site(apps, schema_editor):

    Site = apps.get_model(
        'sites',
        'Site'
    )

    site, created = Site.objects.get_or_create(
        domain='hotel-booking-fasq.onrender.com',
        defaults={
            'name': 'Hotel Booking',
        }
    )

    if not created:

        site.name = 'Hotel Booking'
        site.save()


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(
            create_production_site
        ),
    ]