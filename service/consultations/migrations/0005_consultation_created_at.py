from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("consultations", "0004_alter_consultation_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="consultation",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, db_index=True, null=True),
        ),
    ]
