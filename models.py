class Game(object):
    '''
    '''
    pass
    # game_uuid = UUIDField(unique=True)
    # word = CharField(max_length=256)
    # word_length = IntegerField()
    # result = CharField(max_length=16, default='in_progress')
    # create_time = DateTimeField(default=datetime.utcnow)
    # update_time = DateTimeField(default=datetime.utcnow)

    # class Meta:
    #     database = db

    # def save(self, *args, **kwargs):
    #     self.update_time = datetime.utcnow()
    #     return super(Game, self).save(*args, **kwargs)


class LetterGuessed(object):
    '''
    '''
    # game = ForeignKeyField(Game, related_name='letters')
    # letter = CharField(max_length=1)
    # attempts_left = IntegerField()
    # message = CharField(max_length=256)
    # create_time = DateTimeField(default=datetime.utcnow)

    # class Meta:
    #     database = db
    pass
