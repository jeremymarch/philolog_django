from django.db import models

class Word(models.Model):
    word_id = models.IntegerField(unique=True)
    # seq = models.BigIntegerField(db_index=True)
    lexicon = models.CharField(max_length=10, db_index=True)
    word = models.CharField(max_length=255, db_index=True)
    # word_sort = models.CharField(max_length=255, db_index=True)
    definition = models.TextField()
