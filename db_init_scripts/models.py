import peewee
import os


class area(peewee.Model):
    aid = peewee.CharField(primary_key=True, unique=True)
    zone_address = peewee.CharField()

    class Meta:
        database = peewee.PostgresqlDatabase(
            os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
        )


class service_plans(peewee.Model):
    pid = peewee.CharField(primary_key=True, unique=True)
    name = peewee.CharField()
    speed = peewee.CharField()
    price = peewee.CharField()

    class Meta:
        database = peewee.PostgresqlDatabase(
            os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
        )


class customer_data(peewee.Model):
    cid = peewee.CharField(primary_key=True, unique=True)
    customer_name = peewee.CharField()
    address = peewee.CharField()
    pid = peewee.ForeignKeyField(service_plans, to_field="pid")
    prepaid_months = peewee.IntegerField()
    aid = peewee.ForeignKeyField(area, to_field="aid")

    class Meta:
        database = db


class active_faults(peewee.Model):
    fid = peewee.CharField(primary_key=True, unique=True)
    faults_name = peewee.CharField()
    aid = peewee.ForeignKeyField(area, to_field="aid")
    Resolved = peewee.BooleanField(default=False)

    class Meta:
        database = db


class technician_data(peewee.Model):
    tid = peewee.CharField(primary_key=True, unique=True)
    name = peewee.CharField()
    aid = peewee.ForeignKeyField(area, to_field="aid")
    phone_no = peewee.CharField()
    specialty = peewee.CharField()

    class Meta:
        database = db


class supported_plans(peewee.Model):
    pid = peewee.ForeignKeyField(service_plans, to_field="pid")
    aid = peewee.ForeignKeyField(area, to_field="aid")

    class Meta:
        database = db
