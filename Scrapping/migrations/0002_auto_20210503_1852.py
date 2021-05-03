# Generated by Django 3.2 on 2021-05-03 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Scrapping', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='centros',
            name='calle',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='centros',
            name='ciudad',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='centros',
            name='codigo',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='centros',
            name='direccion',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='centros',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='<function static at 0x0000019C753D18B0>/img'),
        ),
        migrations.AlterField(
            model_name='centros',
            name='nombre',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='centros',
            name='numero',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='centros',
            name='pobalcion',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='centros',
            name='tipo',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
