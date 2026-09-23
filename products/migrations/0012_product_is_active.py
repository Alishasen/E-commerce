from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_order_email_order_full_name_order_phone_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]