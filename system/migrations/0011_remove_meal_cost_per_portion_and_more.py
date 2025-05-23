# Generated by Django 5.2 on 2025-05-04 18:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0010_remove_stockitem_unit_of_measure_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meal',
            name='cost_per_portion',
        ),
        migrations.RemoveField(
            model_name='meal',
            name='portion_size',
        ),
        migrations.RemoveField(
            model_name='meal',
            name='unit_of_measure',
        ),
        migrations.AlterField(
            model_name='meal',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.CreateModel(
            name='MealIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_per_person', models.FloatField()),
                ('meal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.meal')),
                ('stock_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.stockitem')),
            ],
        ),
        migrations.AddField(
            model_name='meal',
            name='ingredients',
            field=models.ManyToManyField(through='system.MealIngredient', to='system.stockitem'),
        ),
    ]
