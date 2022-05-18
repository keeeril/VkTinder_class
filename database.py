from peewee import SqliteDatabase, Model, PrimaryKeyField, CharField

db = SqliteDatabase('package/database.db')


class VkUsers(Model):
    id = PrimaryKeyField(unique=True)
    first_name = CharField()
    last_name = CharField()

    class Meta:
        database = db
        order_by = 'id'
        db_table = 'vk_users'
