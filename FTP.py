# Autor: Wojciech Dołęga
# Nr indeksu: 304535

import os
import Metashape

doc = Metashape.app.document

def list_files(dir):
    r = []
    for root, dirs, files in os.walk(dir):
        for name in files:
            r.append(os.path.join(root, name))
    return r

def add_chunks(path):
    for i in range(1, 3):
        new_chunk = doc.addChunk()
        new_chunk.label = f'Chunk_{i}'
        new_chunk.addPhotos(list_files(f'{path}\chunk_{i}'))
        new_chunk.enabled = True
    
def load_photos():
    # master_folder = ('G:\Zamek_Krolewski\images')
    master_folder = ('D:\projekty\python\p_foto\images') # folder ze zdjeciami podzielonymi na foldery wedlug chunkow
    for chunk in list(doc.chunks):
        doc.remove(chunk)
    add_chunks(master_folder)

def match_align(chunk):
    for frame in chunk.frames:
        frame.matchPhotos(downscale=4, generic_preselection=True, reference_preselection=False)
    chunk.alignCameras()

def orient_photos():
    for chunk in doc.chunks:
        match_align(chunk)
    
def load_reference():
    # sciezka pliku z punktami referencyjnymi
    # reference_path = ('G:\Zamek_Krolewski\key_points\osnowa_UAV.txt')
    reference_path = 'D:\projekty\python\p_foto\osnowa_UAV.txt'
    #############################################
    for chunk in doc.chunks:
        chunk.importReference(path=reference_path, format=Metashape.ReferenceFormatCSV, columns='nyxz', delimiter='\t', create_markers=True)
        chunk.crs = Metashape.CoordinateSystem("EPSG::4326")
        chunk.marker_crs = Metashape.CoordinateSystem("EPSG::2178")

def save_marker_location():
    # domyslny folder w ktorym ma byc zapisany plik
    # master_path = 'G:\Zamek_Krolewski'   
    master_path = 'D:\projekty\python\p_foto'
    #############################################
    path = os.path.join(master_path, "coords")
    for i, chunk in enumerate(doc.chunks):
        file = open(f'{path}_{i+1}.txt', 'w')
        chunk.exportReference(path=f'{path}_{i+1}.txt', format=Metashape.ReferenceFormatCSV, items=Metashape.ReferenceItemsMarkers, delimiter=' ', precision=4)
        file.close()


#################################
# funkcja wzieta z forum Agisoft Metashape https://agisoft.freshdesk.com/support/solutions/articles/31000154629-how-to-select-fixed-percent-of-the-points-gradual-selection-using-python?fbclid=IwAR1CAeJrWBPwbl9RZSYrAiObEJiHgn7zUHVwqOISD6Z7ShRFDqxC1HbI23Q
def remove_points():
    TARGET_PERCENT = 80
    for chunk in doc.chunks:
        points = chunk.point_cloud.points
        f = Metashape.PointCloud.Filter()
        f.init(chunk, criterion = Metashape.PointCloud.Filter.ReprojectionError)
        list_values = f.values
        list_values_valid = list()
        for i in range(len(list_values)):
            if points[i].valid:
                list_values_valid.append(list_values[i])
        list_values_valid.sort()
        target = int(len(list_values_valid) * TARGET_PERCENT / 100)
        threshold = list_values_valid[target]
        f.selectPoints(threshold) 
        f.removePoints(threshold)

def build_dense_cloud():
    for chunk in doc.chunks:
        chunk.buildDepthMaps(downscale=8, filter_mode=Metashape.AggressiveFiltering)           
        chunk.buildDenseCloud(point_colors=True)

def build_model():
    for chunk in doc.chunks:
        chunk.buildModel(surface_type=Metashape.Arbitrary, interpolation=Metashape.EnabledInterpolation, 
                            face_count=Metashape.FaceCount.MediumFaceCount, source_data=Metashape.DenseCloudData)
def build_dem():
    for chunk in doc.chunks:
        chunk.buildDem()

def build_orthophotomap():
    projection= Metashape.OrthoProjection()
    for chunk in doc.chunks:
        chunk.buildOrthomosaic(surface_data=Metashape.DataSource.ModelData, blending_mode=Metashape.BlendingMode.MosaicBlending, projection=projection)
    
def merge_chunks():
    doc.mergeChunks(chunks=[chunk.key for chunk in doc.chunks], merge_markers=True, merge_tiepoints=True, merge_depth_maps=False,
                        merge_dense_clouds=True, merge_models=True, merge_elevations=True, merge_orthomosaics=True)

Metashape.app.removeMenuItem('Skrypt_304535')
Metashape.app.addMenuItem('Skrypt_304535/Dodawanie zdjęć', load_photos)
Metashape.app.addMenuItem('Skrypt_304535/Orientacja zdjęć', orient_photos)
Metashape.app.addMenuItem('Skrypt_304535/Dodawanie punktów osnowy', load_reference)
Metashape.app.addMenuItem('Skrypt_304535/Eksport markerów', save_marker_location)
Metashape.app.addMenuItem('Skrypt_304535/Usuwanie punktów', remove_points)
Metashape.app.addMenuItem('Skrypt_304535/Generowanie chmury', build_dense_cloud)
Metashape.app.addMenuItem('Skrypt_304535/Generowanie siatki', build_model)
Metashape.app.addMenuItem('Skrypt_304535/Generowanie NMPT', build_dem)
Metashape.app.addMenuItem('Skrypt_304535/Generowanie ortofotomapy', build_orthophotomap)
Metashape.app.addMenuItem('Skrypt_304535/Łączenie chunków', merge_chunks)