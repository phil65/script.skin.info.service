import sys
import xbmc
import xbmcgui
import xbmcaddon
from Utils import *
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson


__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString


class Daemon:

    def __init__(self):
        log("version %s started" % __addonversion__)
        self._init_vars()
        self.run_backend()

    def _init_vars(self):
        self.window = xbmcgui.Window(10000)  # Home Window
        self.wnd = xbmcgui.Window(12003)  # Video info dialog
        self.musicvideos = []
        self.movies = []
        self.albums = []
        self.artists = []
        self.id = None
        self.dbid = None
        self.type = False
        self.tag = ""
        self.silent = True
        self.prop_prefix = ""
        self.Artist_mbid = None
        self.window.clearProperty('SongToMusicVideo.Path')

    def run_backend(self):
        self._stop = False
        self.previousitem = ""
        log("starting backend")
        self.musicvideos = create_musicvideo_list()
        self.movies = create_movie_list()
        self.albums = create_album_list()
        self.artists = create_artist_list()
        while (not self._stop) and (not xbmc.abortRequested):
            if xbmc.getCondVisibility("Container.Content(movies) | Container.Content(sets) | Container.Content(artists) | Container.Content(albums) | Container.Content(episodes) | Container.Content(musicvideos)"):
                self.selecteditem = xbmc.getInfoLabel("ListItem.DBID")
                if (self.selecteditem != self.previousitem):
                    self.previousitem = self.selecteditem
                    if (self.selecteditem is not "") and (self.selecteditem > -1):
                        if xbmc.getCondVisibility("Container.Content(artists)"):
                            self._set_artist_details(self.selecteditem)
                        elif xbmc.getCondVisibility("Container.Content(albums)"):
                            self._set_album_details(self.selecteditem)
                        elif xbmc.getCondVisibility("SubString(ListItem.Path,videodb://movies/sets/,left)"):
                            self._set_movieset_details(self.selecteditem)
                        elif xbmc.getCondVisibility("Container.Content(movies)"):
                            self._set_movie_details(self.selecteditem)
                        elif xbmc.getCondVisibility("Container.Content(episodes)"):
                            self._set_episode_details(self.selecteditem)
                        elif xbmc.getCondVisibility("Container.Content(musicvideos)"):
                            self._set_musicvideo_details(self.selecteditem)
                        else:
                            clear_properties()
                    else:
                        clear_properties()
            elif xbmc.getCondVisibility("Container.Content(seasons) + !Window.IsActive(movieinformation)"):
                self.window.setProperty("SeasonPoster", xbmc.getInfoLabel("ListItem.Icon"))
                self.window.setProperty("SeasonID", xbmc.getInfoLabel("ListItem.DBID"))
                self.window.setProperty("SeasonNumber", xbmc.getInfoLabel("ListItem.Season"))
            elif xbmc.getCondVisibility("Container.Content(years)"):
                if xbmc.getCondVisibility("Window.IsActive(videolibrary)"):
                    self.setMovieDetailsforCategory("year")
                else:
                    self.setAlbumDetailsforCategory("year")
            elif xbmc.getCondVisibility("Container.Content(genres)"):
                if xbmc.getCondVisibility("Window.IsActive(videolibrary)"):
                    self.setMovieDetailsforCategory("genre")
                else:
                    self.setArtistDetailsforCategory("genre")
            elif xbmc.getCondVisibility("Container.Content(directors)"):
                self.setMovieDetailsforCategory("director")
            elif xbmc.getCondVisibility("Container.Content(actors)"):
                self.setMovieDetailsforCategory("cast")
            elif xbmc.getCondVisibility("Container.Content(studios)"):
                self.setMovieDetailsforCategory("studio")
            elif xbmc.getCondVisibility("Container.Content(countries)"):
                self.setMovieDetailsforCategory("country")
            elif xbmc.getCondVisibility("Container.Content(tags)"):
                self.setMovieDetailsforCategory("tag")
            elif xbmc.getCondVisibility('Container.Content(songs)') and self.musicvideos:
                # get artistname and songtitle of the selected item
                self.selecteditem = xbmc.getInfoLabel('ListItem.DBID')
                # check if we've focussed a new song
                if self.selecteditem != self.previousitem:
                    self.previousitem = self.selecteditem
                    # clear the window property
                    self.window.clearProperty('SongToMusicVideo.Path')
                    # iterate through our musicvideos
                    for musicvideo in self.musicvideos:
                        if self.selecteditem == musicvideo[0]:  # needs fixing
                            # match found, set the window property
                            self.window.setProperty('SongToMusicVideo.Path', musicvideo[2])
                            xbmc.sleep(100)
                            # stop iterating
                            break
         #   elif xbmc.getCondVisibility("Window.IsActive(visualisation)"):
            elif False:
                self.selecteditem = xbmc.getInfoLabel('MusicPlayer.Artist')
                if (self.selecteditem != self.previousitem) and self.selecteditem:
                    self.previousitem = self.selecteditem
                    from MusicBrainz import GetMusicBrainzIdFromNet
                    log("Daemon updating SimilarArtists")
                    Artist_mbid = GetMusicBrainzIdFromNet(self.selecteditem)
                    passDataToSkin('SimilarArtistsInLibrary', None, self.prop_prefix)
                    passDataToSkin('SimilarArtists', GetSimilarArtistsInLibrary(Artist_mbid,self.artists), self.prop_prefix)
                    xbmc.sleep(2000)
            elif xbmc.getCondVisibility('Window.IsActive(screensaver)'):
                xbmc.sleep(1000)
            else:
                self.previousitem = ""
                self.selecteditem = ""
                clear_properties()
                xbmc.sleep(500)
            if xbmc.getCondVisibility("IsEmpty(Window(home).Property(skininfos_daemon_running))"):
                clear_properties()
                self._stop = True
            xbmc.sleep(100)

    def _set_song_details(self, dbid):  # unused, needs fixing
        json_response = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMusicVideos", "params": {"properties": ["artist", "file"], "sort": { "method": "artist" } }, "id": 1}')
        clear_properties()
        if ("result" in json_response) and ('musicvideos' in json_response['result']):
            set_movie_properties(json_query)

    def _set_artist_details(self, dbid):
        json_response = Get_JSON_response('{"jsonrpc": "2.0", "method": "AudioLibrary.GetAlbums", "params": {"properties": ["title", "year", "albumlabel", "playcount", "thumbnail"], "sort": { "method": "label" }, "filter": {"artistid": %s} }, "id": 1}' % dbid)
        clear_properties()
        if ("result" in json_response) and ('albums' in json_response['result']):
            set_artist_properties(json_response)

    def _set_movie_details(self, dbid):
        json_response = Get_JSON_response('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", "params": {"properties": ["streamdetails","set","setid","cast"], "movieid":%s }, "id": 1}' % dbid)
        clear_properties()
        if ("result" in json_response) and ('moviedetails' in json_response['result']):
            self._set_properties(json_response['result']['moviedetails'])

    def _set_episode_details(self, dbid):
        json_response = Get_JSON_response('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodeDetails", "params": {"properties": ["streamdetails","tvshowid","season"], "episodeid":%s }, "id": 1}' % dbid)
        clear_properties()
        if ('result' in json_response) and ('episodedetails' in json_response['result']):
            self._set_properties(json_response['result']['episodedetails'])
            seasonnumber = json_response['result']['episodedetails']['season']
            tvshowid = json_response['result']['episodedetails']['tvshowid']
            json_response = Get_JSON_response('{"jsonrpc": "2.0", "method": "VideoLibrary.GetSeasons", "params": {"properties": ["thumbnail"], "tvshowid":%s }, "id": 1}' % tvshowid)
            for season in json_response["result"]["seasons"]:
                if season["label"].split(" ")[-1] == str(seasonnumber):
                    self.window.setProperty('SeasonPoster', season["thumbnail"])

    def _set_musicvideo_details(self, dbid):
        json_response = Get_JSON_response('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMusicVideoDetails", "params": {"properties": ["streamdetails"], "musicvideoid":%s }, "id": 1}' % dbid)
        clear_properties()
        if ("result" in json_response) and ('musicvideodetails' in json_response['result']):
            self._set_properties(json_response['result']['musicvideodetails'])

    def _set_album_details(self, dbid):
        json_response = Get_JSON_response('{"jsonrpc": "2.0", "method": "AudioLibrary.GetSongs", "params": {"properties": ["title", "track", "duration", "file", "lastplayed", "disc"], "sort": { "method": "label" }, "filter": {"albumid": %s} }, "id": 1}' % dbid)
        clear_properties()
        if ("result" in json_response) and ('songs' in json_response['result']):
            set_album_properties(json_response)

    def _set_movieset_details(self, dbid):
        json_response = Get_JSON_response('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieSetDetails", "params": {"setid": %s, "properties": [ "thumbnail" ], "movies": { "properties":  [ "rating", "art", "file", "year", "director", "writer","genre" , "thumbnail", "runtime", "studio", "plotoutline", "plot", "country"], "sort": { "order": "ascending",  "method": "year" }} },"id": 1 }' % dbid)
        clear_properties()
        if ("result" in json_response) and ('setdetails' in json_response['result']):
            set_movie_properties(json_response)

    def setMovieDetailsforCategory(self, comparator):
        self.selecteditem = xbmc.getInfoLabel("ListItem.Label")
        if (self.selecteditem != self.previousitem):
            if xbmc.getCondVisibility("!Stringcompare(ListItem.Label,..)"):
                self.previousitem = self.selecteditem
                clear_properties()
                count = 1
                for movie in self.movies["result"]["movies"]:
                    if self.selecteditem in str(movie[comparator]):
                        self.window.setProperty('Detail.Movie.%i.Path' % (count), movie["file"])
                        self.window.setProperty('Detail.Movie.%i.Art(fanart)' % (count), movie["art"].get('fanart', ''))
                        self.window.setProperty('Detail.Movie.%i.Art(poster)' % (count), movie["art"].get('poster', ''))
                        count += 1
                    if count > 19:
                        break
            else:
                clear_properties()

    def setAlbumDetailsforCategory(self, comparator):
        self.selecteditem = xbmc.getInfoLabel("ListItem.Label")
        if (self.selecteditem != self.previousitem):
            if xbmc.getCondVisibility("!Stringcompare(ListItem.Label,..)"):
                self.previousitem = self.selecteditem
                clear_properties()
                count = 1
                for album in self.albums:
                    if self.selecteditem in str(album[comparator]):
                        self.window.setProperty('Detail.Music.%i.DBID' % (count), str(album["albumid"]))
                        self.window.setProperty('Detail.Music.%i.Year' % (count), str(album["year"]))
                        self.window.setProperty('Detail.Music.%i.Art(fanart)' % (count), album["fanart"])
                        self.window.setProperty('Detail.Music.%i.Art(thumb)' % (count), album["thumbnail"])
                        self.window.setProperty('Detail.Music.%i.Title' % (count), album["title"])
                        self.window.setProperty('Detail.Music.%i.Artist' % (count), " / ".join(album["artist"]))
                        count += 1
                    if count > 19:
                        break
            else:
                clear_properties()

    def setArtistDetailsforCategory(self, comparator):
        self.selecteditem = xbmc.getInfoLabel("ListItem.Label")
        if (self.selecteditem != self.previousitem):
            if xbmc.getCondVisibility("!Stringcompare(ListItem.Label,..)"):
                self.previousitem = self.selecteditem
                clear_properties()
                count = 1
                for artist in self.artists:
                    if self.selecteditem in str(artist[comparator]):
                        self.window.setProperty('Detail.Music.%i.DBID' % (count), str(artist["artistid"]))
                        self.window.setProperty('Detail.Music.%i.Art(fanart)' % (count), artist["fanart"])
                        self.window.setProperty('Detail.Music.%i.Art(thumb)' % (count), artist["thumbnail"])
                        self.window.setProperty('Detail.Music.%i.Genre' % (count), " / ".join(artist["genre"]))
                        count += 1
                    if count > 19:
                        break
            else:
                clear_properties()

    def _set_properties(self, results):
        # Set language properties
        count = 1
        audio = results['streamdetails']['audio']
        subtitles = results['streamdetails']['subtitle']
        subs = []
        streams = []
        # Clear properties before setting new ones
        clear_properties()
        for item in audio:
            streams.append(str(item['language']))
            self.wnd.setProperty('AudioLanguage.%d' % count, item['language'])
            self.wnd.setProperty('AudioCodec.%d' % count, item['codec'])
            self.wnd.setProperty('AudioChannels.%d' % count, str(item['channels']))
            count += 1
        count = 1
        for item in subtitles:
            subs.append(str(item['language']))
            self.wnd.setProperty('SubtitleLanguage.%d' % count, item['language'])
            count += 1
        wnd.setProperty('SubtitleLanguage', " / ".join(subs))
        wnd.setProperty('AudioLanguage', " / ".join(streams))
     #   self.cleared = False

if (__name__ == "__main__"):
    try:
        params = dict( arg.split("=") for arg in sys.argv[1].split("&"))
    except:
        params = {}
    if xbmc.getCondVisibility("IsEmpty(Window(home).Property(skininfos_daemon_running))"):
        xbmc.executebuiltin('SetProperty(skininfos_daemon_running,True,home)')
        log("starting daemon")
        Daemon()
    else:
        log("Daemon already active")
log('finished')
