from django.db import models
from django.contrib.auth.models import AbstractUser

class Department(models.Model):
	name = models.CharField(max_length=100, unique=True)
	description = models.TextField(blank=True)

	def __str__(self):
		return self.name


class Role(models.Model):
	name = models.CharField(max_length=50, unique=True)
	description = models.TextField(blank=True)

	def __str__(self):
		return self.name

class Employee(AbstractUser):
	department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
	roles = models.ManyToManyField(Role, blank=True, related_name='employees')

	class Meta:
		verbose_name = 'Employee'
		verbose_name_plural = 'Employees'

	def __str__(self):
		full = self.get_full_name().strip()
		return full or self.username

