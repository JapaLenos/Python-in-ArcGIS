###Crée une zone tampon autour d'un département (donnée vectorielle de type polygone)
##puis découpe des échantillons (données vectorielles de type point) selon les limites de cette zone tampon
import arcpy
from arcpy import env #import de la fonction env du module arcpy

arcpy.env.overwriteOutput = True

print ('Import des bibliothèques et des modules : terminé')

try : 
    database = r'D:\chemin\vers\votre\gdb.gdb'#attention pas d'espace ni de caractères spéciaux
    arcpy.env.workspace = database #défini le dossier de sortie dans l'environnement de travail, dans lequel seront enregistrées par défaut les données en sortie
    
    dpt = 'Isere'
    echants_atmo = 'indice_ATMO'

    #zone tampon
    arcpy.analysis.Buffer(dpt, "Isere_Buffer_1_5km", "1.5 Kilometers")

    #découpe
    arcpy.analysis.Clip(echants_atmo, "Isere_Buffer_1_5km", 
                    "Echantillons_ATMO_Isere")

    print('Analyse : terminée')


except Exception as err :
    arcpy.AddError(err)
    print (err)