from django.db import models


class DownloadedDataset(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    csv = models.TextField()
