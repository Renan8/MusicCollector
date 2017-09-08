import spotipy
import urllib3

from spotipy.oauth2 import SpotifyClientCredentials
from pyAudioAnalysis import audioBasicIO
from pyAudioAnalysis import audioFeatureExtraction
from pymongo import MongoClient

urllib3.disable_warnings()

client_credentials_manager = SpotifyClientCredentials("dcdfa7be7b354e4fb3db2771eb3a2f14", "a5251e1ee2a549858b5d36f00ecefd6d")
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

client_mongo = MongoClient('mongodb://127.0.0.1', 27017)
database_mongo = client_mongo.dbMusicCollector
collection_mongo = database_mongo.tracks

n = 0

#Todos os generos visitados: mais 3 milhoes de tracks
genres = ["rock"]
limit = 50

http = urllib3.PoolManager()

for genre in genres:

    #Consulta 50 musicas por genero
    result = sp.search(q=genre, limit=limit)

    while result['tracks']['next']:

        tracks = []
        for i in range(0, limit):

            previewUrl = result['tracks']['items'][i]['preview_url']

            if previewUrl is not None:

                n += 1
                print genre, n, previewUrl

                #Download do arquivo .mp3
                response = http.request('GET', previewUrl)

                #Salva arquivo .mp3 na pasta musics
                path = 'musics/temp.mp3'
                with open(path, 'wb') as f:
                    f.write(response.data)

                #Extracao das caracteristicas
                [Fs, x] = audioBasicIO.readAudioFile(path)
                F = audioFeatureExtraction.stFeatureExtraction(x, Fs, 0.005 * Fs, 0.03 * Fs)

                features = {
                    "id": result['tracks']['items'][i]['id'],
                    "name": result['tracks']['items'][i]['name'],
                    "artist": result['tracks']['items'][i]['artists'][0]['name'],
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

                tracks.append(features)
            #end_if
        #end_for
        collection_mongo.insert_many(tracks)
        result = sp.next(result['tracks'])
    #end_while
#end_for

print('FIM!')

f.close()
response.release_conn()