# -*- coding: utf-8 -*-

import arcpy


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Analyse de concentration en polluants de l'air"
        self.alias = "Analyse_concentration_polluants"

        # List of tool classes associated with this toolbox
        self.tools = [AnalyseConcentration]


class AnalyseConcentration(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Analyse de concentration en polluants de l'air"
        self.description = "Analyse de concentration en polluants (au choix de l'utilisateur entre : NO2, O3, PM10, PM25, SO2) de chaque département d'une région"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""


        database = arcpy.Parameter(
        displayName="Géoodatabase",
        name="database",
        datatype="DEWorkspace",
        parameterType="Required",
        direction="Input")

        echants_atmo = arcpy.Parameter(
        displayName="Couche d'échantillons d'analyses ATMO",
        name="echants_atmo",
        datatype="GPFeatureLayer",
        parameterType="Required",
        direction="Input")
        echants_atmo.filter.list = ["Point"]

        dpts = arcpy.Parameter(
        displayName="Couche de région contenant les différents départements",
        name="dpts",
        datatype="GPFeatureLayer",
        parameterType="Required",
        direction="Input")
        dpts.filter.list = ["Polygon"]

        zone_tampon = arcpy.Parameter(
        displayName="Zone Tampon",
        name="zone_tampon",
        datatype="GPLinearUnit",
        parameterType="Required",
        direction="Input")
        zone_tampon.value = '1.5 Kilometers'

        NO2 = arcpy.Parameter(
        displayName="NO2",
        name="NO2",
        datatype="GPBoolean",
        direction="Input",
        parameterType="Optional")

        SO2 = arcpy.Parameter(
        displayName="SO2",
        name="SO2",
        datatype="GPBoolean",
        direction="Input",
        parameterType="Optional")

        O3 = arcpy.Parameter(
        displayName="O3",
        name="O3",
        datatype="GPBoolean",
        direction="Input",
        parameterType="Optional")

        PM10 = arcpy.Parameter(
        displayName="PM10",
        name="PM10",
        datatype="GPBoolean",
        direction="Input",
        parameterType="Optional")

        PM25 = arcpy.Parameter(
        displayName="PM25",
        name="PM25",
        datatype="GPBoolean",
        direction="Input",
        parameterType="Optional")

        params = [database,echants_atmo, dpts, zone_tampon,NO2,SO2,O3,PM10,PM25]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, params):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, params):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, params, messages):

        database = params[0].valueAsText
        arcpy.env.workspace = database #définit le dossier de sortie dans l'environnement de travail, dans lequel seront enregistrées par défaut les données en sortie
        arcpy.env.overwriteOutput = True

        echants_atmo = params[1].valueAsText
        dpts = params[2].valueAsText
        zone_tampon = params[3].valueAsText

        polluants = []      
        params_polluants = {4:"conc_no2", 5:"conc_so2", 6:"conc_o3", 7:"conc_pm10",8:"conc_pm25"}
        for cle, valeur in params_polluants.items() :
            if params[cle].valueAsText == 'true' :
                polluants.append(valeur)

        messages.addMessage("Paramètres récupérés. Analyse des polluants : {0}".format(polluants))

        

        #Itération dans les polluants
        rasters_analyses_polluants = []
        for polluant in polluants :
            messages.addMessage("Analyse de {0}".format(polluant))
            #Krigeage Bayésien Empirique
            raster_interpolation = "raster_interpolation_{0}".format(polluant)
            arcpy.ga.EmpiricalBayesianKriging(echants_atmo, polluant, "",raster_interpolation)
            rasters_analyses_polluants.append(raster_interpolation)

        #Itération dans les départements
        champ = "nom"
        with arcpy.da.SearchCursor (dpts, champ) as cursor :
            for row in cursor :

                messages.addMessage("Département : {0}".format(row[0]))

                arcpy.management.MakeFeatureLayer(dpts, "dpts_lyr", where_clause="nom = '{0}'".format(row[0]))

                #zone tampon
                arcpy.analysis.Buffer("dpts_lyr", "{0}_Buffer_1_5km".format(row[0]), zone_tampon)

                for raster_interpolation in rasters_analyses_polluants :
                    #extraction par masque
                    outExtractByMask = arcpy.sa.ExtractByMask(raster_interpolation, "{0}_Buffer_1_5km".format(row[0]))
                    outExtractByMask.save("{0}_{1}".format(row[0],raster_interpolation))
            
                messages.addMessage("Analyses terminées pour le département {0}, suppression des données temporaires".format(row[0]))
                arcpy.management.Delete("{0}_Buffer_1_5km".format(row[0]))

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return