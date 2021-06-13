import django
from django.conf import settings
from django.db import connection, migrations, models
from django.db.migrations.loader import MigrationLoader
import numpy as np
import pgvector.django
from pgvector.django import VectorExtension, VectorField, IvfflatIndex, L2Distance, MaxInnerProduct, CosineDistance

settings.configure(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'pgvector_python_test',
        }
    }
)
django.setup()


class Item(models.Model):
    factors = VectorField(dimensions=3)

    class Meta:
        app_label = 'myapp'
        indexes = [
            IvfflatIndex(
                name='my_index',
                fields=['factors'],
                lists=100,
                opclasses=['vector_l2_ops']
            )
        ]


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        VectorExtension(),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('factors', pgvector.django.VectorField(dimensions=3)),
            ],
        ),
        migrations.AddIndex(
            model_name='item',
            index=pgvector.django.IvfflatIndex(fields=['factors'], lists=1, name='my_index', opclasses=['vector_l2_ops']),
        )
    ]


# probably a better way to do this
migration = Migration('initial', 'myapp')
loader = MigrationLoader(connection, replace_migrations=False)
loader.graph.add_node(('myapp', migration.name), migration)
sql_statements = loader.collect_sql([(migration, False)])

with connection.cursor() as cursor:
    cursor.execute("DROP TABLE IF EXISTS myapp_item")
    cursor.execute('\n'.join(sql_statements))


def create_items():
    vectors = [
        [1, 1, 1],
        [2, 2, 2],
        [1, 1, 2]
    ]
    for i, v in enumerate(vectors):
        item = Item(id=i + 1, factors=v)
        item.save()


class TestDjango(object):
    def setup_method(self, test_method):
        Item.objects.all().delete()

    def test_l2_distance(self):
        create_items()
        items = Item.objects.order_by(L2Distance('factors', [1, 1, 1]))
        assert [v.id for v in items] == [1, 3, 2]

    def test_max_inner_product(self):
        create_items()
        items = Item.objects.order_by(MaxInnerProduct('factors', [1, 1, 1]))
        assert [v.id for v in items] == [2, 3, 1]

    def test_cosine_distance(self):
        create_items()
        items = Item.objects.order_by(CosineDistance('factors', [1, 1, 1]))
        assert [v.id for v in items] == [1, 2, 3]
