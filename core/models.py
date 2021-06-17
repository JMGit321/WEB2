from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

# Create your models here.
class Causa(models.Model):
    titulo = models.CharField(max_length=60)
    data = models.DateField(auto_now=True)
    meta = models.DecimalField(max_digits=10,decimal_places=2)
    recebido = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    descricao = models.TextField()
    fins = models.TextField()
    info = models.TextField()
    foto = models.ImageField(upload_to="media2")
    ativo = models.BooleanField(default=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'causa'

class Doacao(models.Model):
    valor = models.DecimalField(max_digits=10,decimal_places=2)
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)
    causa = models.ForeignKey(Causa, on_delete=models.CASCADE)
    data = models.DateField(auto_now=True)
    horario = models.TimeField(auto_now=True)
    def __str__(self):
        return self.causa.titulo

    class Meta:
        db_table = 'doacao'


class UserProfile(models.Model):
    user   = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="media2")
    def _str_(self):
        return self.user.username

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
             return self.image.url



