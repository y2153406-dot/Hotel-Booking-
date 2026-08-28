from django.db import migrations


def fix_site_id(apps, schema_editor):

    Site = apps.get_model(
        'sites',
        'Site'
    )

    production_domain = (
        'hotel-booking-fasq.onrender.com'
    )


    # Get the existing production site
    site = Site.objects.filter(
        domain=production_domain
    ).first()


    # Check whether SITE_ID = 1 exists
    site_id_one = Site.objects.filter(
        id=1
    ).first()


    # If ID 1 exists, configure it correctly
    if site_id_one:

        site_id_one.domain = production_domain
        site_id_one.name = 'Hotel Booking'
        site_id_one.save()


    # If ID 1 doesn't exist and production site exists,
    # delete the old site and recreate it with ID 1
    elif site:

        site.delete()

        Site.objects.create(
            id=1,
            domain=production_domain,
            name='Hotel Booking'
        )


    # No site exists at all
    else:

        Site.objects.create(
            id=1,
            domain=production_domain,
            name='Hotel Booking'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_create_production_site'),
    ]


    operations = [
        migrations.RunPython(
            fix_site_id
        ),
    ]