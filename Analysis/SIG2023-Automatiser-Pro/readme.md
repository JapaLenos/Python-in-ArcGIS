# Automatiser des flux de travail dans ArcGIS Pro

**Atelier présenté à la conférence SIG2023**

### Code ArcPy--
+ Le script *analyses_simples.py* montre comment utiliser ArcPy pour automatiser deux analyses basiques : zone tampon et découpe.
+ Le script *analyses_completes_polluants_atmos.py* montre comment un workflow d'interpolation de concentration en polluants atmosphérique en itérant sur les polluants puis en créant des zones tampons sur chaque département contenu dans un shapefile et en découpant les rasters d'interpolations à l'emprise de ces zones tampons.
+ Le script *exemple_toolbox.pyt* montre comment transformer le script suivant en toolbox utilisable directement dans ArcGIS Pro, et en y intégrant des paramètres utilisateurs.

[Note] Pour que les scripts fonctionnent, la bibliothèque ArcPy doit être installée dans l'environnement d'exécution

### Gérer ses environnements avec l'invite de commande--
Exécutez votre gestionnaire d'environnements (ex : [miniconda](https://docs.conda.io/en/latest/miniconda.html)) en tant qu'**administrateur**
+Cloner l'envrionnement par défaut d'ArcGIS Pro (remplacer _myclonename_ par le nom souhaité pour votre clone) :
```
conda create --name myclonename --clone arcgispro-py3
```
+[Facultatif] vérifier que l'environnement a bien été créé :
```
conda env list
```
+Activer son environnement cloné :
```
conda activate myclonename 
```
+Vérifier les packages présents dans son environnement :
```
conda list 
```
+Installer un nouveau package dans son environnement (ligne de commande à adapter selon le package, à rechercher dans sa documentation ; exemple pour [scikit-learn](https://scikit-learn.org/stable/install.html)):
```
pip install -U scikit-le
```
[Présentation pdf de la partie Python de l'atelier](FILE_NAME.pdf)
