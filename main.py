import spotipy
import urllib3

from spotipy.oauth2 import SpotifyClientCredentials
from pyAudioAnalysis import audioBasicIO
from pyAudioAnalysis import audioFeatureExtraction
from pymongo import MongoClient

urllib3.disable_warnings()

client_credentials_manager = SpotifyClientCredentials("dcdfa7be7b354e4fb3db2771eb3a2f14", "a5251e1ee2a549858b5d36f00ecefd6d")
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

#client_mongo = MongoClient('localhost', 27017)
#database_mongo = client_mongo.dbMusicCollector
#collection_mongo = database_mongo.TracksMetrics

n = 0

#Todos os generos visitados: mais 3 milhoes de tracks
genres = ["Rock"]
limit = 50

http = urllib3.PoolManager()
arq = open('teste.arff', 'w')
arq.write("@relation Escola\n\n")

arq.write("@attribute ZeroCrossingRate numeric\n")
arq.write("@attribute Energy numeric\n")
arq.write("@attribute EntropyOfEnergy numeric\n")
arq.write("@attribute SpectralCentroid numeric\n")
arq.write("@attribute SpectralSpread numeric\n")
arq.write("@attribute SpectralEntropy numeric\n")
arq.write("@attribute SpectralFlux numeric\n")
arq.write("@attribute SpectralRollof numeric\n")
arq.write("@attribute Mfccs1 numeric\n")
arq.write("@attribute Mfccs2 numeric\n")
arq.write("@attribute Mfccs3 numeric\n")
arq.write("@attribute Mfccs4 numeric\n")
arq.write("@attribute Mfccs5 numeric\n")
arq.write("@attribute Mfccs6 numeric\n")
arq.write("@attribute Mfccs7 numeric\n")
arq.write("@attribute Mfccs8 numeric\n")
arq.write("@attribute Mfccs9 numeric\n")
arq.write("@attribute Mfccs10 numeric\n")
arq.write("@attribute Mfccs11 numeric\n")
arq.write("@attribute Genre {Rock, Pop, Classical}\n\n")

arq.write("@data\n")

for genre in genres:
    n = 0;
    #Consulta 50 musicas por genero
    result = sp.search(q=genre, limit=limit)

    while result['tracks']['next'] or n == 650:

        tracks = []
        for i in range(0, limit):

            previewUrl = result['tracks']['items'][i]['preview_url']

            if previewUrl is not None:

                n += 1
                #Download do arquivo .mp3
                response = http.request('GET', previewUrl)

                #Salva arquivo .mp3 na pasta musics
                path = 'musics/temp.mp3'
                with open(path, 'wb') as f:
                    f.write(response.data)

                #Extracao das caracteristicas
                [Fs, x] = audioBasicIO.readAudioFile(path)

                try:
                    F = audioFeatureExtraction.stFeatureExtraction(x, Fs, 0.005 * Fs, 0.03 * Fs)
                except ValueError:
                    print genre, n, previewUrl + "ERRO"

                features = {
                    "id": result['tracks']['items'][i]['id'],
                    "name": result['tracks']['items'][i]['name'],
                    "artist": result['tracks']['items'][i]['artists'][0]['name'],
                    "genre": genre,
                    "preview_url": previewUrl,
                    "zeroCrossingRate": F.item(0),
                    "energy": F.item(1),
                    "entropyOfEnergy": F.item(2),
                    "spectralCentroid": F.item(3),
                    "spectralSpread": F.item(4),
                    "spectralEntropy": F.item(5),
                    "spectralFlux": F.item(6),
                    "spectralRollof": F.item(7),
                    "mfccs": [F.item(8), F.item(9), F.item(10), F.item(11), F.item(12), F.item(13), F.item(14), F.item(15), F.item(16), F.item(17), F.item(18)]
                }

                arq.write(str(F.item(0)) + ", " + str(F.item(1)) + ", " + str(F.item(2)) + ", " + str(F.item(3)) + ", " + str(F.item(4)) + ", " + str(F.item(5)) + ", " + str(F.item(6)) + ", " + str(F.item(7)) + ", " + str(F.item(8)) + ", " + str(F.item(9)) + ", " + str(F.item(10)) + ", " + str(F.item(11)) + ", " + str(F.item(12)) + ", " + str(F.item(13)) + ", " + str(F.item(14)) + ", " + str(F.item(15)) + ", " + str(F.item(16)) + ", " + str(F.item(17)) + ", " + str(F.item(18)) + ", " + genre + "\n")
                # track = collection_mongo.find({"id": result['tracks']['items'][i]['id']})

                #if track.count() == 0:
                print genre, n, previewUrl
                    #tracks.append(features)

            #end_if
        #end_for

       # if len(tracks) > 1:
         #   response = collection_mongo.insert_many(tracks)
      #  else:
       #     if len(tracks) == 1:
        #        response = collection_mongo.insert(tracks)

        result = sp.next(result['tracks'])
    #end_while
#end_for

print('FIM!')
arq.close()
f.close()
response.release_conn()