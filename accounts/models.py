from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import os

def avatar_upload_to(instance, filename):
    """
        Define a lógica e o caminho de armazenamento para os arquivos de imagem do avatar do usuário no sistema, 
    o objetivo principal é garantir que cada arquivo seja armazenado de forma única, segura e organizada pelo ID do Usuário Individual
    """
    ext = os.path.splitext(filename)[1]  
    
    filename = f"{uuid.uuid4()}{ext}"
    
    user_id = instance.id or "temp"
    
    return f'avatars/user_{user_id}/{filename}'

class User(AbstractUser):
    
    bio = models.TextField(blank=True)
    interests = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(
        upload_to=avatar_upload_to,
        blank=True,
        null=True,
        default='avatars/default.png'
    )

   
    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)

   
    def xp_for_next_level(self) -> int:
        """
        Retorna quanto de XP é necessário para atingir o próximo nível
        """
        return 100 * self.level

    def add_xp(self, amount: int):
        """
        Adiciona XP."""
        
        if amount <= 0:
            return

        self.xp += amount

        
        while self.xp >= self.xp_for_next_level():
            self.xp -= self.xp_for_next_level()
            self.level += 1

       
        self.save(update_fields=['xp', 'level'])

   
    @property
    def xp_percentage(self):
        """
        Retorna a porcentagem de XP da barra atual (0 a 100)
        """
        return int((self.xp / self.xp_for_next_level()) * 100)


    def __str__(self):
        return f"{self.username} (Level {self.level})"
    
    
class User(AbstractUser):
    xp = models.IntegerField(default=0)

    @property
    def level(self):
        return self.xp // 100 + 1
