"""
Signals para o app Funcionários
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Funcionario


@receiver(pre_save, sender=Funcionario)
def atribuir_superior_automatico(sender, instance, **kwargs):
    """
    Automaticamente define o chefe do setor como superior do funcionário,
    SOMENTE se o superior não foi definido manualmente.
    
    Lógica:
    - Se superior está preenchido → usa o superior definido manualmente
    - Se superior está vazio → usa o chefe do setor automaticamente
    - Chefe do setor nunca será seu próprio superior
    """
    # Se já tem superior definido manualmente, respeita a escolha
    if instance.superior:
        return
    
    # Se não tem setor, não pode definir superior automático
    if not instance.setor:
        return
    
    # Se o setor não tem chefe, não pode definir superior automático
    if not instance.setor.chefe:
        return
    
    # Não pode ser seu próprio superior (caso seja o chefe do setor)
    if instance.pk and instance.setor.chefe.pk == instance.pk:
        return
    
    # Define o chefe do setor como superior automaticamente
    instance.superior = instance.setor.chefe


@receiver(post_save, sender=Funcionario)
def atualizar_subordinados_ao_definir_chefe_setor(sender, instance, created, **kwargs):
    """
    Quando um funcionário é definido como chefe de um setor,
    atualiza automaticamente todos os funcionários daquele setor
    para terem ele como superior (exceto se já tiverem superior definido).
    """
    # Verifica se é chefe de algum setor
    if not instance.is_chefe():
        return
    
    setor = instance.setor_chefiado
    
    # Atualiza funcionários do setor que não têm superior ou têm o chefe antigo
    funcionarios_sem_superior = setor.funcionarios.filter(
        superior__isnull=True
    ).exclude(pk=instance.pk)
    
    for funcionario in funcionarios_sem_superior:
        funcionario.superior = instance
        # Usa update() para evitar recursão infinita
        Funcionario.objects.filter(pk=funcionario.pk).update(superior=instance)
