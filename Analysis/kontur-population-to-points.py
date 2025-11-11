"""
Ce code transforme les données du Kontur Population Dataset (hexagones H3) en points. 
Nécéssite un environnement ArcGIS Pro ou Server pour licencier ArcPy.
"""

import arcpy
import random

#Paramètres
input_polygons =  r"C:\Users\plouis\OneDrive - esrifrance.fr\Documents\ArcGIS\Projects\population2125\population2125.gdb\kontur_population"
output_points =  r"C:\Users\plouis\OneDrive - esrifrance.fr\Documents\ArcGIS\Projects\population2125\population2125.gdb\population_ponderee_2125"
population_field = "population" 
species_probs = {"Humain": 0.5, "IA": 0.3, "Hybride": 0.2}
cluster_size = 50000  #taille d’un cluster géographique
mix_ratio = 0.8  #homogénéité du cluster

#Initialisation
if arcpy.Exists(output_points):
    arcpy.management.Delete(output_points)

spatial_ref = arcpy.Describe(input_polygons).spatialReference
workspace = arcpy.env.workspace or "\\".join(output_points.split("\\")[:-1])
arcpy.management.CreateFeatureclass(
    out_path=workspace,
    out_name=output_points.split("\\")[-1],
    geometry_type="POINT",
    spatial_reference=spatial_ref
)

#Création des champs
arcpy.management.AddField(output_points, "ponderation", "SHORT")
arcpy.management.AddField(output_points, "pop_represented", "LONG")
arcpy.management.AddField(output_points, "espece", "TEXT", field_length=20)

#Génération des points à partir des polygones
generated_points = []

with arcpy.da.SearchCursor(input_polygons, ["OID@", "SHAPE@", population_field]) as cursor_in, \
     arcpy.da.InsertCursor(output_points, ["SHAPE@", "ponderation", "pop_represented", "espece"]) as cursor_out:

    for oid, shape, pop in cursor_in:
        if not shape or pop is None or pop < 250000:
            continue
        
        #Liste des tranches disponibles et leur pondération
        thresholds = [(1000000, 3), (500000, 2), (250000, 1)]
        
        remaining = pop
        generated = 0
        
        for threshold_pop, ponderation in thresholds:
            while remaining >= threshold_pop:
                #généreration d'un point placé aléatoirement à l’intérieur de l'hexagone
                extent = shape.extent
                minx, miny, maxx, maxy = extent.XMin, extent.YMin, extent.XMax, extent.YMax
                
                tries = 0
                while True:
                    tries += 1
                    x = random.uniform(minx, maxx)
                    y = random.uniform(miny, maxy)
                    point_geom = arcpy.PointGeometry(arcpy.Point(x, y), spatial_ref)
                    if shape.contains(point_geom):
                        generated_points.append((x, y))
                        cursor_out.insertRow([point_geom, ponderation, threshold_pop, None])
                        generated += 1
                        remaining -= threshold_pop
                        break
                    if tries > 1000:
                        break 

print(f"Étape 1 terminée : {len(generated_points)} points générés.")

#Attribution d'espèces avec regroupements géographiques
points = []
with arcpy.da.SearchCursor(output_points, ["OID@", "SHAPE@XY"]) as cursor:
    for oid, xy in cursor:
        points.append({"oid": oid, "xy": xy})

if not points:
    raise RuntimeError("Aucun point généré — vérifier les seuils de population.")

minx = min(p["xy"][0] for p in points)
miny = min(p["xy"][1] for p in points)

for p in points:
    cluster_x = int((p["xy"][0] - minx) // cluster_size)
    cluster_y = int((p["xy"][1] - miny) // cluster_size)

    #choix de l'espèce majoritaire du cluster selon les proportions globales
    random.seed(cluster_x * 1000 + cluster_y)
    major_species = random.choices(
        population=list(species_probs.keys()),
        weights=list(species_probs.values()),
        k=1
    )[0]

    #mélange local
    if random.random() < mix_ratio:
        p["species"] = major_species
    else:
        p["species"] = random.choices(
            population=list(species_probs.keys()),
            weights=list(species_probs.values()),
            k=1
        )[0]

#mise à jour du champ "espece"
with arcpy.da.UpdateCursor(output_points, ["OID@", "espece"]) as cursor:
    for row in cursor:
        oid = row[0]
        esp = next(p["species"] for p in points if p["oid"] == oid)
        row[1] = esp
        cursor.updateRow(row)

print("Étape 2 terminée : attribution d’espèces terminée.")
print("La couche de résultats est disponible ici :", output_points)