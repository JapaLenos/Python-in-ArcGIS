import arcpy
from arcpy import env #import de la fonction env du module arcpy
from arcpy.sa import *

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("GeoStats")


print ('Import des bibliothèques et des modules : terminé')

try : 
    database = r'D:\arcpy\demos_automatiserPro_SIG2023\ModelBuilder_Python\Analyses_polluants_arcpy.gdb'#attention pas d'espace ni de caractères spéciaux
    arcpy.env.workspace = database #défini le dossier de sortie dans l'environnement de travail, dans lequel seront enregistrées par défaut les données en sortie
    
    dpts = 'departements_ARA'
    echants_atmo = 'indice_ATMO'

    taille_buffer = '1.5'
    unite_buffer = 'Kilometers'

    polluants = ['conc_no2','conc_o3','conc_pm25']
    
    #Itération parmis les polluants
    rasters_analyses_polluants = []
    for polluant in polluants :
        
        print("Analyse de {0}".format(polluant))
        
        #Krigeage Bayésien Empirique
        raster_interpolation = "raster_interpolation_{0}".format(polluant)
        arcpy.ga.EmpiricalBayesianKriging(echants_atmo, polluant, "",raster_interpolation)
        rasters_analyses_polluants.append(raster_interpolation)
        
    #Itération dans les départements
    champ = "nom"
    with arcpy.da.SearchCursor (dpts, champ) as cursor :
        for row in cursor :
            print("Département : {0}".format(row[0]))
            arcpy.management.MakeFeatureLayer(dpts, "dpts_lyr", where_clause="nom = '{0}'".format(row[0]))
        
            #zone tampon
            arcpy.analysis.Buffer("dpts_lyr", "{0}_Buffer_1_5km".format(row[0]), "{0} {1}".format(taille_buffer,unite_buffer))

            #extraction par masque
            for raster_interpolation in rasters_analyses_polluants :
                    #extraction par masque
                    outExtractByMask = arcpy.sa.ExtractByMask(raster_interpolation, "{0}_Buffer_1_5km".format(row[0]))
                    outExtractByMask.save("{0}_{1}".format(row[0],raster_interpolation))

            print("Analyses terminées pour le département {0}, suppression des données temporaires".format(row[0]))
            arcpy.management.Delete("{0}_Buffer_1_5km".format(row[0]))
            
    print('Analyse : terminée')


except Exception as err :
    arcpy.AddError(err)
    print (err)