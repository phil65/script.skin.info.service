######################################################
#####################FOR SKINNERS#####################
######################################################

Start the script with RunScript(script.skin.info.service) in startup.xml
Properties will be available in the corresponding media windows.

New properties:

For artists:
Window(home).Property(...)
    'Artist.Album.%d.Title' % i
    'Artist.Album.%d.Plot' % i
    'Artist.Album.%d.PlotOutline' % i
    'Artist.Album.%d.Year' % i
    'Artist.Album.%d.Duration' % i
    'Artist.Album.%d.Thumb' % i
    'Artist.Album.%d.ID' % i
    'Artist.Albums.Newest'   
    'Artist.Albums.Oldest'   
    'Artist.Albums.Count'   
    'Artist.Albums.Playcount'  

For Albums:
Window(home).Property(...)
    'Album.Song.%d.Title' % i
    'Album.Song.%d.FileExtension' % i
    'Album.Songs.TrackList'   
    'Album.Songs.Discs' 
    'Album.Songs.Discs'   
    'Album.Songs.Duration'   
    'Album.Songs.Count' 

For movie sets:
Window(home).Property(...)
    'Set.Movie.%d.Art(clearlogo)' % i
    'Set.Movie.%d.Art(fanart)' % i
    'Set.Movie.%d.Art(poster)' % i
    'Set.Movie.%d.Art(discart)' % i
    'Set.Movies.Plot'   
    'Set.Movies.ExtendedPlot'   
    'Set.Movies.Runtime'   
    'Set.Movies.Writer'   
    'Set.Movies.Director'   
    'Set.Movies.Genre'   
    'Set.Movies.Years'   
    'Set.Movies.Count' 

For movie years, directors, actors, genres, studios countries and tags:
Window(home).Property(...)
    'Detail.Movie.%d.Art(poster)' % i
    'Detail.Movie.%d.Art(fanart)' % i
    'Detail.Movie.%d.Path' % i

For movies:
Window(movieinformation).Property(...)
    AudioLanguage.%d' % i
    AudioCodec.%d' % i
    AudioChannels.%d' % i
    SubtitleLanguage.%d' % i
