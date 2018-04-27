import urllib
import xbmc
import xbmcaddon
import xbmcgui
import urllib2
import os
import sys
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
HOME = xbmcgui.Window(10000)
INFODIALOG = xbmcgui.Window(12003)


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
    message = u'%s: %s' % (ADDON_ID, txt)
    xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)


def GetStringFromUrl(encurl):
    succeed = 0
    while succeed < 5:
        try:
            req = urllib2.Request(encurl)
            req.add_header('User-agent', 'XBMC/13.2 ( phil65@kodi.tv )')
            res = urllib2.urlopen(req)
            html = res.read()
            return html
        except:
            log("GetStringFromURL: could not get data from %s" % encurl)
            xbmc.sleep(1000)
            succeed += 1
    return ""


def Notify(header, line='', line2='', line3=''):
    xbmc.executebuiltin('Notification(%s, %s)' % (header, line))


def prettyprint(string):
    log(simplejson.dumps(string, sort_keys=True, indent=4, separators=(',', ': ')))


def set_artist_properties(audio):
    count = 1
    latestyear = 0
    firstyear = 0
    playcount = 0
    for item in audio['result']['albums']:
        HOME.setProperty('Artist.Album.%d.Title' % count, item['title'])
        HOME.setProperty('Artist.Album.%d.Year' % count, str(item['year']))
        HOME.setProperty('Artist.Album.%d.Thumb' % count, item['thumbnail'])
        HOME.setProperty('Artist.Album.%d.DBID' % count, str(item.get('albumid')))
        HOME.setProperty('Artist.Album.%d.Label' % count, item['albumlabel'])
        if item['playcount']:
            playcount = playcount + item['playcount']
        if item['year'] > latestyear:
            latestyear = item['year']
        if firstyear == 0 or item['year'] < firstyear:
            firstyear = item['year']
        count += 1
    if firstyear > 0 and latestyear < 2020:
        HOME.setProperty('Artist.Albums.Newest', str(latestyear))
        HOME.setProperty('Artist.Albums.Oldest', str(firstyear))
    HOME.setProperty('Artist.Albums.Count', str(audio['result']['limits']['total']))
    HOME.setProperty('Artist.Albums.Playcount', str(playcount))


def set_album_properties(json_response):
    count = 1
    duration = 0
    discnumber = 0
    tracklist = ""
    for item in json_response['result']['songs']:
        HOME.setProperty('Album.Song.%d.Title' % count, item['title'])
        tracklist += "[B]" + str(item['track']) + "[/B]: " + item['title'] + "[CR]"
        array = item['file'].split('.')
        HOME.setProperty('Album.Song.%d.FileExtension' % count, str(array[-1]))
        if item['disc'] > discnumber:
            discnumber = item['disc']
        duration += item['duration']
        count += 1
    minutes = duration / 60
    seconds = duration % 60
    HOME.setProperty('Album.Songs.Discs', str(discnumber))
    HOME.setProperty('Album.Songs.Duration', str(minutes).zfill(2) + ":" + str(seconds).zfill(2))
    HOME.setProperty('Album.Songs.Tracklist', tracklist)
    HOME.setProperty('Album.Songs.Count', str(json_response['result']['limits']['total']))


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
        HOME.setProperty('Set.Movie.%d.DBID' % count, str(item.get('movieid')))
        HOME.setProperty('Set.Movie.%d.Title' % count, item['label'])
        HOME.setProperty('Set.Movie.%d.Plot' % count, item['plot'])
        HOME.setProperty('Set.Movie.%d.PlotOutline' % count, item['plotoutline'])
        HOME.setProperty('Set.Movie.%d.Path' % count, media_path(item['file']))
        HOME.setProperty('Set.Movie.%d.Year' % count, str(item['year']))
        HOME.setProperty('Set.Movie.%d.Duration' % count, str(item['runtime'] / 60))
        HOME.setProperty('Set.Movie.%d.VideoResolution' % count, streaminfo["videoresolution"])
        HOME.setProperty('Set.Movie.%d.Art(clearlogo)' % count, art.get('clearlogo', ''))
        HOME.setProperty('Set.Movie.%d.Art(discart)' % count, art.get('discart', ''))
        HOME.setProperty('Set.Movie.%d.Art(fanart)' % count, art.get('fanart', ''))
        HOME.setProperty('Set.Movie.%d.Art(poster)' % count, art.get('poster', ''))
        HOME.setProperty('Detail.Movie.%d.Art(fanart)' % count, art.get('fanart', ''))  # hacked in
        HOME.setProperty('Detail.Movie.%d.Art(poster)' % count, art.get('poster', ''))
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
    HOME.setProperty('Set.Movies.Plot', plot)
    HOME.setProperty('Set.Movies.List', title_header + title_list)
    if json_response['result']['setdetails']['limits']['total'] > 1:
        HOME.setProperty('Set.Movies.ExtendedPlot', title_header + title_list + "[CR]" + plot)
    else:
        HOME.setProperty('Set.Movies.ExtendedPlot', plot)
    HOME.setProperty('Set.Movies.Title', title_list)
    HOME.setProperty('Set.Movies.Runtime', str(runtime / 60))
    HOME.setProperty('Set.Movies.Writer', " / ".join(writer))
    HOME.setProperty('Set.Movies.Director', " / ".join(director))
    HOME.setProperty('Set.Movies.Genre', " / ".join(genre))
    HOME.setProperty('Set.Movies.Country', " / ".join(country))
    HOME.setProperty('Set.Movies.Studio', " / ".join(studio))
    HOME.setProperty('Set.Movies.Years', " / ".join(years))
    HOME.setProperty('Set.Movies.Count', str(json_response['result']['setdetails']['limits']['total']))


def clear_properties():
    if xbmc.getCondVisibility("Window.IsActive(videos)"):
        for i in range(1, 40):
            HOME.clearProperty('Set.Movie.%d.Art(clearlogo)' % i)
            HOME.clearProperty('Set.Movie.%d.Art(fanart)' % i)
            HOME.clearProperty('Set.Movie.%d.Art(poster)' % i)
            HOME.clearProperty('Set.Movie.%d.Art(discart)' % i)
            HOME.clearProperty('Detail.Movie.%d.Art(poster)' % i)
            HOME.clearProperty('Detail.Movie.%d.Art(fanart)' % i)
            HOME.clearProperty('Detail.Movie.%d.Path' % i)
            INFODIALOG.clearProperty('AudioLanguage.%d' % i)
            INFODIALOG.clearProperty('AudioCodec.%d' % i)
            INFODIALOG.clearProperty('AudioChannels.%d' % i)
            INFODIALOG.clearProperty('SubtitleLanguage.%d' % i)
        HOME.clearProperty('Set.Movies.Plot')
        HOME.clearProperty('Set.Movies.ExtendedPlot')
        HOME.clearProperty('Set.Movies.Runtime')
        HOME.clearProperty('Set.Movies.Writer')
        HOME.clearProperty('Set.Movies.Director')
        HOME.clearProperty('Set.Movies.Genre')
        HOME.clearProperty('Set.Movies.Country')
        HOME.clearProperty('Set.Movies.Studio')
        HOME.clearProperty('Set.Movies.Years')
        HOME.clearProperty('Set.Movies.Count')
    else:
        for i in range(1, 40):
            HOME.clearProperty('Artist.Album.%d.Title' % i)
            HOME.clearProperty('Artist.Album.%d.Plot' % i)
            HOME.clearProperty('Artist.Album.%d.PlotOutline' % i)
            HOME.clearProperty('Artist.Album.%d.Year' % i)
            HOME.clearProperty('Artist.Album.%d.Duration' % i)
            HOME.clearProperty('Artist.Album.%d.Thumb' % i)
            HOME.clearProperty('Artist.Album.%d.ID' % i)
            HOME.clearProperty('Album.Song.%d.Title' % i)
            HOME.clearProperty('Album.Song.%d.FileExtension' % i)
            HOME.clearProperty('Detail.Music.%d.Art(fanart)' % i)
            HOME.clearProperty('Detail.Music.%d.Art(thumb)' % i)
            HOME.clearProperty('Detail.Music.%d.DBID' % i)
            HOME.clearProperty('Detail.Music.%d.Genre' % i)
            HOME.clearProperty('Detail.Music.%d.Title' % i)
            HOME.clearProperty('Detail.Music.%d.Year' % i)
            HOME.clearProperty('Detail.Music.%d.Artist' % i)
        HOME.clearProperty('Album.Songs.TrackList')
        HOME.clearProperty('Album.Songs.Discs')
        HOME.clearProperty('Artist.Albums.Newest')
        HOME.clearProperty('Artist.Albums.Oldest')
        HOME.clearProperty('Artist.Albums.Count')
        HOME.clearProperty('Artist.Albums.Playcount')
        HOME.clearProperty('Album.Songs.Discs')
        HOME.clearProperty('Album.Songs.Duration')
        HOME.clearProperty('Album.Songs.Count')


def passDataToSkin(name, data, prefix="", debug=False):
    if data is not None:
       # log( "%s%s.Count = %s" % (prefix, name, str(len(data)) ) )
        for (count, result) in enumerate(data):
            if debug:
                log("%s%s.%i = %s" % (prefix, name, count + 1, str(result)))
            for (key, value) in result.iteritems():
                HOME.setProperty('%s%s.%i.%s' % (prefix, name, count + 1, str(key)), unicode(value))
                if debug:
                    log('%s%s.%i.%s --> ' % (prefix, name, count + 1, str(key)) + unicode(value))
        HOME.setProperty('%s%s.Count' % (prefix, name), str(len(data)))
    else:
        HOME.setProperty('%s%s.Count' % (prefix, name), '0')
        log("%s%s.Count = None" % (prefix, name))
