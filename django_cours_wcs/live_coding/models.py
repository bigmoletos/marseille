from Django.db import models

class Image(models.Model):
    image=models.ImageField( )
    createur=models.IntegerField()
    dateCreation=mdels.DateTimeField(auto_now=True)



class Objectif(models.Model):
    titre=models.CharField(max_length=100)
    date=models.DateField(null=True)
    statut=models.BooleanField()
    priorite=models.BigIntegerField() # 1234