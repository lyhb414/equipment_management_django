from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, Group

class Equipment(models.Model):
    equipId = models.CharField(max_length=100, default="0")
    name = models.CharField(max_length=100)
    totalNum = models.IntegerField(default=0)
    borrowNum = models.IntegerField(default=0) 
    location = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    createUser = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                   on_delete=models.CASCADE, 
                                   default = 0,)

    def __str__(self):
        return self.name

class BorrowHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    itemId = models.CharField(max_length=100)
    borrowNum = models.IntegerField()
    borrowTime = models.DateTimeField(auto_now_add=True)
    returnNum = models.IntegerField(default=0)
    isOver = models.BooleanField(default=False)
    
    def returnItem(self, returnItemNum, returnUser):
        if returnItemNum > self.borrowNum - self.returnNum:
            return (False, "归还数量大于此次借用需归还数量")
        else:
            try:
                equipment = Equipment.objects.get(id=self.itemId)
            except Equipment.DoesNotExist:
                 return (False, "未查询到对应器材")

            if equipment.borrowNum < returnItemNum:
                return (False, "归还数量大于此设备的借用数量")

            equipment.borrowNum -= returnItemNum
            equipment.save()

            return_history = ReturnHistory(borrowHistory=self, returnNum=returnItemNum, returnUser = returnUser)
            return_history.save()

            self.returnNum += returnItemNum
            self.save()

        if self.returnNum == self.borrowNum:
            self.isOver = True
            self.save()

        return (True, "归还成功")
    
    def returnAllItem(self, returnUser):
        if self.isOver:
            return (False, "本次借用已完毕，无需归还")
        else:
            return self.returnItem(self.borrowNum - self.returnNum, returnUser)
        
class ReturnHistory(models.Model):
    borrowHistory = models.ForeignKey(BorrowHistory, on_delete=models.CASCADE, related_name='returnHistorys')
    returnUser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    returnNum = models.IntegerField()
    returnTime = models.DateTimeField(auto_now_add=True)

class EquipmentModification(models.Model):
    equipment_id = models.TextField(null=True, blank=True)
    equipment_name = models.TextField(null=True, blank=True)
    modification_type = models.IntegerField(default=0)
    modification_data = models.TextField(null=True, blank=True)
    username = models.TextField(null=True, blank=True)
    user_firstname = models.TextField(null=True, blank=True)
    modification_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Equipment Modification #{self.id}"