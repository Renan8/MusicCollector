import spotipy
import urllib3

from spotipy.oauth2 import SpotifyClientCredentials
from pyAudioAnalysis import audioBasicIO
from pyAudioAnalysis import audioFeatureExtraction

urllib3.disable_warnings()

client_credentials_manager = SpotifyClientCredentials("dcdfa7be7b354e4fb3db2771eb3a2f14", "a5251e1ee2a549858b5d36f00ecefd6d")
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

n = 0

#Todos os generos visitados: mais 3 milhoes de tracks
genres = ["rock", "pop", "classical", "blues", "electro", "house", "jazz"]
limit = 50

http = urllib3.PoolManager()

for genre in genres:

    #Consulta 50 musicas por genero
    result = sp.search(q=genre, limit=limit)

    while result['tracks']['next']:

        for i in range(0, 50):

            previewUrl = result['tracks']['items'][i]['preview_url']

            if previewUrl is not None:

                n += 1
                print genre, n, previewUrl

                #Download do arquivo .mp3
                response = http.request('GET', previewUrl)

                #Salva arquivo .mp3 na pasta musics
                path = 'musics/' + result['tracks']['items'][i]['id'] + '.mp3'
                with open(path, 'wb') as f:
                    f.write(response.data)

                #Extracao das caracteristicas
                [Fs, x] = audioBasicIO.readAudioFile(path)
                F = audioFeatureExtraction.stFeatureExtraction(x, Fs, 0.005 * Fs, 0.03 * Fs)
                print(F)

            #end_if
        #end_for

        result = sp.next(result['tracks'])

    #end_while
#end_for

f.close()
response.release_conn()