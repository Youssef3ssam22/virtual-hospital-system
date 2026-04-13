from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("hospital_administration", "0003_labcatalogitem_radiologycatalogitem_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="auditlog",
            old_name="details",
            new_name="detail",
        ),
        migrations.RenameField(
            model_name="auditlog",
            old_name="timestamp",
            new_name="occurred_at",
        ),
    ]
