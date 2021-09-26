## Kód

Itt található a **Python + OpenCV** segítségével készített kódbázis.

Mindenki olyan fejlesztőkörnyezetet használ amilyet csak akar, de a fejlesztőkörnyezet specifikus 
fájlokat/mappákat rakja a *.gitignore*-ba. Például *Visual Studio Code* esetére a 

```
.vscode/
```

sor ignorálja a *Visual Studio Code* beállításait. Szintén senki se töltse fel a virtuális *Python* környezetet 
amit a projekthez használ. Ez általában a *.venv* mappában van. Látható hogy ez már bent van a *.gitignore*-ban, 
de ha más néven vagy máshol hozzátok létre a virtuális környezetet, akkor azt mindenképp rakjátok a *.gitignore*-ba.

### Függőségek

A projekt függőségei *pip3* segítségével vannak kezelve. Például egy könvtár/csomag így telepíthető.

```
pip3 install [csomag neve]
```

A projekt függőségei és ezek verziói a *requirements.txt*-ben vannak felsorolva. 
Ha új függőséget húz be valaki, akkor frissítse ezt a fájlt, hogy a többiek is tudják futtatni a kódot:

```
pip3 freeze > requirements.txt
```

Az összes függőséget így lehet telepíteni a *requirements.txt* alapján:

```
pip3 install -r requirements.txt
```