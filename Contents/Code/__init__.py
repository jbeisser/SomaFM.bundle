
from random import randint

TITLE    = 'SomaFM: Listener Supported, Commercial Free Internet Radio'
APISERV  = 'http://api.somafm.com/'
STATIONS = APISERV + 'channels.xml'
CACHE    = 600


# make sure to replace artwork with what you want
# these filenames reference the example files in
# the Contents/Resources/ folder in the bundle
ART         = 'art-default.jpg'
ICON        = 'icon-default.png'
ICON_SEARCH = 'icon-search.png'


####################################################################################################

def Start():
    Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    # initial default attributes
    ObjectContainer.title1     = TITLE
    ObjectContainer.view_group = "List"
    ObjectContainer.art        = R(ART)
    DirectoryObject.thumb      = R(ICON)
    DirectoryObject.art        = R(ART)
    TrackObject.thumb          = R(ICON)


@handler('/music/somafm', TITLE)
def MainMenu():

    oc = ObjectContainer()

    stations = XML.ElementFromURL(STATIONS).xpath('//channels')
    #for station in stations.xpath('./channel'):

    i = 0
    for station in stations[0].xpath('./channel'):
        Log.Debug('Loading.. %d' % i)
        i = i + 1


        title       = station.xpath('./title')[0].text
        description = station.xpath('./description')[0].text
        dj          = station.xpath('./dj')[0].text
        #twitter     = station.xpath('./twitter')[0].text
        #splsmp3     = station.xpath("./slowpls[@format='mp3']")[0].text
        fplsmp3     = station.xpath("./fastpls[@format='mp3']")[0].text
        #splsaac     = station.xpath("./slowpls[@format='aacp']")[0].text
        #fplsaac     = station.xpath('./fastpls[@format="aacp"]')[0].text
        listeners   = station.xpath('./listeners')[0].text
        thumb       = station.xpath('./image')[0].text
        genre       = station.xpath('./genre')[0].text
        date        = station.xpath('./updated')[0].text

        Log.Debug('Added %s' % title)

        genre = genre.split('|')


        Log.Info('Channel: %s, dj: %s' % (title, dj))
        Log.Info('Genre: %s' % (genre))
        Log.Info('Thumb: %s' % (thumb))
        Log.Info('Pls: %s' % (fplsmp3))
        Log.Info('Description: %s' % (description))


        pls = GetPls(fplsmp3)
        stm = randStm(pls)
        Log.Debug("Stream for %s: %s" % (title, stm))

        oc.add(TrackObject(
            #url = stm,
            key     = stm,
            rating_key = stm,
            title   = title,
            duration = -1,
            genres   = genre,
            thumb   = Callback(Thumb, url=thumb),
            items   = [ MediaObject(
                audio_codec = AudioCodec.MP3,
                protocols   = [ Protocol.Shoutcast, 
                    Protocol.HTTPLiveStreaming ])
                ]
            ))

    Log.Debug('%d channels' % len(oc))
    return oc


def GetPls(pls):
    ''' returns a dictionary of streams from the pls file'''
    p = HTTP.Request(pls, immediate=True).content
    return pls2dict(p)


def pls2dict(pls):
    d = {}
    for l in pls.split('\n'):
        l.strip()
        try:
            k, v = l.split('=')
            d[k.lower()] = v
        except:
            pass
    return d


def randStm(d):
    i = randint(1, int(d['numberofentries']))
    return d['file%d' % i]


def Thumb(url):
    Log.Info('Attempting to get thumbnail: %s' % url)
    try:
        data = HTTP.Request(url).content
        Log.Info('Success.')
        return DataObject(data)
    except:
        Log.Info('Failed')
        return Redirect(R(ICON))
