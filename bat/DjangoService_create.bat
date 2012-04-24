@echo off
echo create DjangoService
sc create DjangoService type= share start= auto binpath= "D:\python\djangosite_start.bat" DisplayName= "DjangoService" depend= Tcpip
echo DjangoService created