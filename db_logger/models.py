import logging
from django.db import models
from six import python_2_unicode_compatible
from django.utils.translation import gettext_lazy as _
import requests
from project.settings_local import *
from project.settings_local import DEV, SEND_BOT

LOG_LEVELS = (
    (logging.NOTSET, _('NotSet')),
    (logging.INFO, _('Info')),
    (logging.WARNING, _('Warning')),
    (logging.DEBUG, _('Debug')),
    (logging.ERROR, _('Error')),
    (logging.FATAL, _('Fatal')),
)


@python_2_unicode_compatible
class StatusLog(models.Model):
    logger_name = models.CharField(max_length=100)
    level = models.PositiveSmallIntegerField(choices=LOG_LEVELS, default=logging.ERROR, db_index=True)
    msg = models.TextField()
    trace = models.TextField(blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True, verbose_name='Created at')

    def __str__(self):
        return self.msg

    def save(self, *args, **kwargs):
        levels = {40: 'Error', 50: 'Fatal'}
        level = levels.get(self.level)
        if level and SEND_BOT:
            text = f'{"<b>DEV</b> " if DEV else ""}<b>{level}</b>\n{self.msg}\n{self.trace}'

            data = {
                'text': text,
                'parse_mode': 'html',
                'chat_id': CHAT_ID,
            }

            requests.post(f'https://api.telegram.org/bot{BOT_ID}/sendMessage', data=data)
        super(StatusLog, self).save(*args, **kwargs)

    class Meta:
        ordering = ('-create_datetime',)
        verbose_name_plural = verbose_name = "Логгер"
