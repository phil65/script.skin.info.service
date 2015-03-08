import urllib
import xbmc
import xbmcaddon
import xbmcgui
import datetime
import urllib2
import os
import sys
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__language__ = __addon__.getLocalizedString
Addon_Data_Path = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % __addonid__).decode("utf-8"))

window = xbmcgui.Window(10000)
wnd = xbmcgui.Window(12003)
locallist = []


def GetSimilarArtistsInLibrary(id, db_artists):
    from OnlineMusicInfo import GetSimilarById
    simi_artists = GetSimilarById(id)
    if simi_artists is None:
        log('Last.fm didn\'t return proper response')
        return None
    artists = []
    for (count, simi_artist) in enumerate(simi_artists):
        for (count, db_artist) in enumerate(db_artists["result"]["artists"]):
            if db_artist['musicbrainzartistid'] != '':
                if db_artist['musicbrainzartistid'] == simi_artist['mbid']:
                    artists.append(db_artist)
            elif db_artist['artist'] == simi_artist['name']:
                json_response = db.executeJSONRPC(
                    '{"jsonrpc": "2.0", "method": "AudioLibrary.GetArtistDetails", "params": {"properties": ["genre", "description", "mood", "style", "born", "died", "formed", "disbanded", "yearsactive", "instrument", "fanart", "thumbnail"], "artistid": %s}, "id": 1}' % str(db_artist['artistid']))
                json_response = unicode(json_response, 'utf-8', errors='ignore')
                json_response = simplejson.loads(json_response)
                item = json_response["result"]["artistdetails"]
                newartist = {"Title": item['label'],
                             "Genre": " / ".join(item['genre']),
                             "Thumb": item['thumbnail'],  # remove
                             "Fanart": item['fanart'],  # remove
                             "Art(thumb)": item['thumbnail'],
                             "Art(fanart)": item['fanart'],
                             "Description": item['description'],
                             "Born": item['born'],
                             "Died": item['died'],
                             "Formed": item['formed'],
                             "Disbanded": item['disbanded'],
                             "YearsActive": " / ".join(item['yearsactive']),
                             "Style": " / ".join(item['style']),
                             "Mood": " / ".join(item['mood']),
                             "Instrument": " / ".join(item['instrument']),
                             "LibraryPath": 'musicdb://artists/' + str(item['artistid']) + '/'}
                artists.append(newartist)
    log('%i of %i artists found in last.FM is in XBMC database' % (len(artists), len(simi_artists)))
    return artists


def Get_JSON_response(query):
    json_response = xbmc.executeJSONRPC(query)
    json_response = unicode(json_response, 'utf-8', errors='ignore')
    return simplejson.loads(json_response)


def media_streamdetails(filename, streamdetails):
    info = {}
    video = streamdetails['video']
    audio = streamdetails['audio']
    if '3d' in filename:
        info['videoresolution'] = '3d'
    elif video:
        videowidth = video[0]['width']
        videoheight = video[0]['height']
        if (videowidth <= 720 and videoheight <= 480):
            info['videoresolution'] = "480"
        elif (videowidth <= 768 and videoheight <= 576):
            info['videoresolution'] = "576"
        elif (videowidth <= 960 and videoheight <= 544):
            info['videoresolution'] = "540"
        elif (videowidth <= 1280 and videoheight <= 720):
            info['videoresolution'] = "720"
        elif (videowidth >= 1281 or videoheight >= 721):
            info['videoresolution'] = "1080"
        elif (videowidth >= 1921 or videoheight >= 1081):
            info['videoresolution'] = "4k"
        else:
            info['videoresolution'] = ""
    elif (('dvd') in filename and not ('hddvd' or 'hd-dvd') in filename) or (filename.endswith('.vob' or '.ifo')):
        info['videoresolution'] = '576'
    elif (('bluray' or 'blu-ray' or 'brrip' or 'bdrip' or 'hddvd' or 'hd-dvd') in filename):
        info['videoresolution'] = '1080'
    else:
        info['videoresolution'] = '1080'
    if video:
        info['videocodec'] = video[0]['codec']
        if (video[0]['aspect'] < 1.4859):
            info['videoaspect'] = "1.33"
        elif (video[0]['aspect'] < 1.7190):
            info['videoaspect'] = "1.66"
        elif (video[0]['aspect'] < 1.8147):
            info['videoaspect'] = "1.78"
        elif (video[0]['aspect'] < 2.0174):
            info['videoaspect'] = "1.85"
        elif (video[0]['aspect'] < 2.2738):
            info['videoaspect'] = "2.20"
        else:
            info['videoaspect'] = "2.35"
    else:
        info['videocodec'] = ''
        info['videoaspect'] = ''
    if audio:
        info['audiocodec'] = audio[0]['codec']
        info['audiochannels'] = audio[0]['channels']
    else:
        info['audiocodec'] = ''
        info['audiochannels'] = ''
    return info


def media_path(path):
    # Check for stacked movies
    try:
        path = os.path.split(path)[0].rsplit(' , ', 1)[1].replace(",,", ",")
    except:
        path = os.path.split(path)[0]
    # Fixes problems with rared movies and multipath
    if path.startswith("rar://"):
        path = [os.path.split(urllib.url2pathname(path.replace("rar://", "")))[0]]
    elif path.startswith("multipath://"):
        temp_path = path.replace("multipath://", "").split('%2f/')
        path = []
        for item in temp_path:
            path.append(urllib.url2pathname(item))
    else:
        path = [path]
    return path[0]


def log(txt):
    if isinstance(txt, str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (__addonid__, txt)
    xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)


def GetStringFromUrl(encurl):
    succeed = 0
    while succeed < 5:
        try:
            req = urllib2.Request(encurl)
            req.add_header('User-agent', 'XBMC/13.2 ( ptemming@gmx.net )')
            res = urllib2.urlopen(req)
            html = res.read()
       #     log("URL String: " + html)
            return html
        except:
            log("GetStringFromURL: could not get data from %s" % encurl)
            xbmc.sleep(1000)
            succeed += 1
    return ""


def Notify(header, line='', line2='', line3=''):
    xbmc.executebuiltin('Notification(%s, %s, %s, %s)' % (header, line, line2, line3))


def prettyprint(string):
    log(simplejson.dumps(string, sort_keys=True, indent=4, separators=(',', ': ')))


def set_artist_properties(audio):
    count = 1
    latestyear = 0
    firstyear = 0
    playcount = 0
    for item in audio['result']['albums']:
        window.setProperty('Artist.Album.%d.Title' % count, item['title'])
        window.setProperty('Artist.Album.%d.Year' % count, str(item['year']))
        window.setProperty('Artist.Album.%d.Thumb' % count, item['thumbnail'])
        window.setProperty('Artist.Album.%d.DBID' % count, str(item.get('albumid')))
        window.setProperty('Artist.Album.%d.Label' % count, item['albumlabel'])
        if item['playcount']:
            playcount = playcount + item['playcount']
        if item['year'] > latestyear:
            latestyear = item['year']
        if firstyear == 0 or item['year'] < firstyear:
            firstyear = item['year']
        count += 1
    if firstyear > 0 and latestyear < 2020:
        window.setProperty('Artist.Albums.Newest', str(latestyear))
        window.setProperty('Artist.Albums.Oldest', str(firstyear))
    window.setProperty('Artist.Albums.Count', str(audio['result']['limits']['total']))
    window.setProperty('Artist.Albums.Playcount', str(playcount))


def set_album_properties(json_response):
    count = 1
    duration = 0
    discnumber = 0
    tracklist = ""
    for item in json_response['result']['songs']:
        window.setProperty('Album.Song.%d.Title' % count, item['title'])
        tracklist += "[B]" + str(item['track']) + "[/B]: " + item['title'] + "[CR]"
        array = item['file'].split('.')
        window.setProperty('Album.Song.%d.FileExtension' % count, str(array[-1]))
        if item['disc'] > discnumber:
            discnumber = item['disc']
        duration += item['duration']
        count += 1
    minutes = duration / 60
    seconds = duration % 60
    window.setProperty('Album.Songs.Discs', str(discnumber))
    window.setProperty('Album.Songs.Duration', str(minutes).zfill(2) + ":" + str(seconds).zfill(2))
    window.setProperty('Album.Songs.Tracklist', tracklist)
    window.setProperty('Album.Songs.Count', str(json_response['result']['limits']['total']))


def set_movie_properties(json_response):
    count = 1
    runtime = 0
    writer = []
    director = []
    genre = []
    country = []
    studio = []
    years = []
    plot = ""
    title_list = ""
    title_header = "[B]" + str(json_response['result']['setdetails']['limits']['total']) + " " + xbmc.getLocalizedString(20342) + "[/B][CR]"
    for item in json_response['result']['setdetails']['movies']:
        art = item['art']
        streaminfo = media_streamdetails(item['file'].encode('utf-8').lower(), item['streamdetails'])
        window.setProperty('Set.Movie.%d.DBID' % count, str(item.get('movieid')))
        window.setProperty('Set.Movie.%d.Title' % count, item['label'])
        window.setProperty('Set.Movie.%d.Plot' % count, item['plot'])
        window.setProperty('Set.Movie.%d.PlotOutline' % count, item['plotoutline'])
        window.setProperty('Set.Movie.%d.Path' % count, media_path(item['file']))
        window.setProperty('Set.Movie.%d.Year' % count, str(item['year']))
        window.setProperty('Set.Movie.%d.Duration' % count, str(item['runtime'] / 60))
        window.setProperty('Set.Movie.%d.VideoResolution' % count, streaminfo["videoresolution"])
        window.setProperty('Set.Movie.%d.Art(clearlogo)' % count, art.get('clearlogo', ''))
        window.setProperty('Set.Movie.%d.Art(discart)' % count, art.get('discart', ''))
        window.setProperty('Set.Movie.%d.Art(fanart)' % count, art.get('fanart', ''))
        window.setProperty('Set.Movie.%d.Art(poster)' % count, art.get('poster', ''))
        window.setProperty('Detail.Movie.%d.Art(fanart)' % count, art.get('fanart', ''))  # hacked in
        window.setProperty('Detail.Movie.%d.Art(poster)' % count, art.get('poster', ''))
        title_list += "[I]" + item['label'] + " (" + str(item['year']) + ")[/I][CR]"
        if item['plotoutline']:
            plot += "[B]" + item['label'] + " (" + str(item['year']) + ")[/B][CR]" + item['plotoutline'] + "[CR][CR]"
        else:
            plot += "[B]" + item['label'] + " (" + str(item['year']) + ")[/B][CR]" + item['plot'] + "[CR][CR]"
        runtime += item['runtime']
        count += 1
        if item.get("writer"):
            writer += [w for w in item["writer"] if w and w not in writer]
        if item.get("director"):
            director += [d for d in item["director"] if d and d not in director]
        if item.get("genre"):
            genre += [g for g in item["genre"] if g and g not in genre]
        if item.get("country"):
            country += [c for c in item["country"] if c and c not in country]
        if item.get("studio"):
            studio += [s for s in item["studio"] if s and s not in studio]
        years.append(str(item['year']))
    window.setProperty('Set.Movies.Plot', plot)
    if json_response['result']['setdetails']['limits']['total'] > 1:
        window.setProperty('Set.Movies.ExtendedPlot', title_header + title_list + "[CR]" + plot)
    else:
        window.setProperty('Set.Movies.ExtendedPlot', plot)
    window.setProperty('Set.Movies.Title', title_list)
    window.setProperty('Set.Movies.Runtime', str(runtime / 60))
    window.setProperty('Set.Movies.Writer', " / ".join(writer))
    window.setProperty('Set.Movies.Director', " / ".join(director))
    window.setProperty('Set.Movies.Genre', " / ".join(genre))
    window.setProperty('Set.Movies.Country', " / ".join(country))
    window.setProperty('Set.Movies.Studio', " / ".join(studio))
    window.setProperty('Set.Movies.Years', " / ".join(years))
    window.setProperty('Set.Movies.Count', str(json_response['result']['setdetails']['limits']['total']))


def clear_properties():
    if xbmc.getCondVisibility("Window.IsActive(videolibrary)"):
        for i in range(1, 40):
            window.clearProperty('Set.Movie.%d.Art(clearlogo)' % i)
            window.clearProperty('Set.Movie.%d.Art(fanart)' % i)
            window.clearProperty('Set.Movie.%d.Art(poster)' % i)
            window.clearProperty('Set.Movie.%d.Art(discart)' % i)
            window.clearProperty('Detail.Movie.%d.Art(poster)' % i)
            window.clearProperty('Detail.Movie.%d.Art(fanart)' % i)
            window.clearProperty('Detail.Movie.%d.Path' % i)
            wnd.clearProperty('AudioLanguage.%d' % i)
            wnd.clearProperty('AudioCodec.%d' % i)
            wnd.clearProperty('AudioChannels.%d' % i)
            wnd.clearProperty('SubtitleLanguage.%d' % i)
        window.clearProperty('Set.Movies.Plot')
        window.clearProperty('Set.Movies.ExtendedPlot')
        window.clearProperty('Set.Movies.Runtime')
        window.clearProperty('Set.Movies.Writer')
        window.clearProperty('Set.Movies.Director')
        window.clearProperty('Set.Movies.Genre')
        window.clearProperty('Set.Movies.Country')
        window.clearProperty('Set.Movies.Studio')
        window.clearProperty('Set.Movies.Years')
        window.clearProperty('Set.Movies.Count')
    else:
        for i in range(1, 40):
            window.clearProperty('Artist.Album.%d.Title' % i)
            window.clearProperty('Artist.Album.%d.Plot' % i)
            window.clearProperty('Artist.Album.%d.PlotOutline' % i)
            window.clearProperty('Artist.Album.%d.Year' % i)
            window.clearProperty('Artist.Album.%d.Duration' % i)
            window.clearProperty('Artist.Album.%d.Thumb' % i)
            window.clearProperty('Artist.Album.%d.ID' % i)
            window.clearProperty('Album.Song.%d.Title' % i)
            window.clearProperty('Album.Song.%d.FileExtension' % i)
            window.clearProperty('Detail.Music.%d.Art(fanart)' % i)
            window.clearProperty('Detail.Music.%d.Art(thumb)' % i)
            window.clearProperty('Detail.Music.%d.DBID' % i)
            window.clearProperty('Detail.Music.%d.Genre' % i)
            window.clearProperty('Detail.Music.%d.Title' % i)
            window.clearProperty('Detail.Music.%d.Year' % i)
            window.clearProperty('Detail.Music.%d.Artist' % i)
        window.clearProperty('Album.Songs.TrackList')
        window.clearProperty('Album.Songs.Discs')
        window.clearProperty('Artist.Albums.Newest')
        window.clearProperty('Artist.Albums.Oldest')
        window.clearProperty('Artist.Albums.Count')
        window.clearProperty('Artist.Albums.Playcount')
        window.clearProperty('Album.Songs.Discs')
        window.clearProperty('Album.Songs.Duration')
        window.clearProperty('Album.Songs.Count')


def passDataToSkin(name, data, prefix="", debug=False):
    if data is not None:
       # log( "%s%s.Count = %s" % (prefix, name, str(len(data)) ) )
        for (count, result) in enumerate(data):
            if debug:
                log("%s%s.%i = %s" % (prefix, name, count + 1, str(result)))
            for (key, value) in result.iteritems():
                window.setProperty('%s%s.%i.%s' % (prefix, name, count + 1, str(key)), unicode(value))
                if debug:
                    log('%s%s.%i.%s --> ' % (prefix, name, count + 1, str(key)) + unicode(value))
        window.setProperty('%s%s.Count' % (prefix, name), str(len(data)))
    else:
        window.setProperty('%s%s.Count' % (prefix, name), '0')
        log("%s%s.Count = None" % (prefix, name))
