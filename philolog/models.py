from django.db import models


class Word(models.Model):
    word_id = models.IntegerField(db_index=True)
    # seq = models.BigIntegerField(db_index=True)
    lexicon = models.CharField(max_length=11, db_index=True)
    word = models.CharField(max_length=255, db_index=True)
    sort_key = models.CharField(max_length=255, db_index=True, default='')
    definition = models.TextField()

    def __str__(self):
        return self.word + " (" + self.lexicon + "_" + str(self.word_id) + ")"
