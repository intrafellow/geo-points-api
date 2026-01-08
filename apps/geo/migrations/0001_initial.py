import django.db.models.deletion
from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.indexes import GistIndex
from django.contrib.postgres.operations import CreateExtension
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        CreateExtension("postgis"),
        migrations.CreateModel(
            name="Point",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("title", models.CharField(blank=True, max_length=255, null=True)),
                ("location", gis_models.PointField(geography=True, srid=4326)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "geo_points",
            },
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("text", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="geo_messages",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "point",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="geo.point",
                    ),
                ),
            ],
            options={
                "db_table": "geo_messages",
            },
        ),
        migrations.AddIndex(
            model_name="point",
            index=GistIndex(fields=["location"], name="geo_points_location_gist"),
        ),
        migrations.AddIndex(
            model_name="message",
            index=models.Index(
                fields=["point", "created_at"], name="geo_messages_point_created_at_idx"
            ),
        ),
    ]
