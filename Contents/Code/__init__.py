NAME = 'Syfy'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

# gives us basic list of Show/Showname
SHOWSLIST="http://feed.theplatform.com/f/hQNl-B/sgM5DlyXAfwt/categories?&form=json&fields=fullTitle,title&q=fullTitle:Shows"



####################################################################################################
def Start():
	Plugin.AddPrefixHandler("/video/syfy", MainMenu, NAME, ICON, ART)

	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

	# Setup the default attributes for the ObjectContainer
	ObjectContainer.title1 = NAME
	ObjectContainer.view_group = 'List'
	ObjectContainer.art = R(ART)
	
	# Setup the default attributes for the other objects
	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON)
	VideoClipObject.art = R(ART)
	EpisodeObject.thumb = R(ICON)
	EpisodeObject.art = R(ART)

	# Setup some basic things the plugin needs to know about
	HTTP.CacheTime = CACHE_1HOUR
	
	HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
def MainMenu():
	return getAllShows()



def getAllShows():
	oc = ObjectContainer (view_group='List')
	
	data=JSON.ObjectFromURL(SHOWSLIST)
	for item in data['entries']:
		oc.add(
			DirectoryObject(key=Callback(getShowList,show=item['plcategory$fullTitle']),title=item['title'])
		)


	# sort here
	oc.objects.sort(key = lambda obj: obj.title)

	return oc


def getShowList(show):
	oc = ObjectContainer (view_group='List')
	show = show.replace(' ','+')
 	showurl="http://feed.theplatform.com/f/hQNl-B/2g1gkJT0urp6/?&form=json&fields=guid&fileFields=duration,url,width,height&byCategories="+show+"&byCustomValue=%7BfullEpisode%7D%7Btrue%7D&count=true"

	guids=""	

	data=JSON.ObjectFromURL(showurl)
	for item in data['entries']:
		guids=guids+item['guid']+"|"

	# Leaving this for possible consideration at some point, but there is a LOT of small and mostly
	# useless video when we do this, which means longer load times, etc
# 	# Now Let's grab any other content they have here that are not full episodes
#  	showurl="http://feed.theplatform.com/f/hQNl-B/2g1gkJT0urp6/?&form=json&fields=guid&fileFields=duration,url,width,height&byCategories="+show+"&count=true"
# 	data=JSON.ObjectFromURL(showurl)
# 	for item in data['entries']:
# 		guids=guids+item['guid']+"|"

	if guids == "":
		oc = MessageContainer("Ooops!","There appears to be no full episodes available for this show.")
		return oc
		
		
	episodeurl="http://feed.theplatform.com/f/hQNl-B/2g1gkJT0urp6/?&form=json&fields=guid,title,description,:subtitle,content,thumbnails,pubdate,categories,:fullEpisode,:disallowSharing%20&fileFields=url,duration,width,height,contentType,fileSize,format&byGuid="+guids

	showdata = JSON.ObjectFromURL(episodeurl)

	for item in showdata['entries']:
		for v in item['media$content']:
			if v['plfile$format']=="MPEG4" and v['plfile$height']==720:				
				# this is the 720p mpeg4
				duration = int(float(item['media$content'][0]['plfile$duration'])*1000)
				pubdate = Datetime.FromTimestamp(int(item['pubDate']/1000))
				title=item['title']

				oc.add(
					EpisodeObject(
						key = Callback(getVideo,url=v['plfile$url']),
						rating_key = v['plfile$url'],
#						url = "http://www.syfy.com/videos/vid:"+item['guid'],
						title=title,
						thumb = Resource.ContentsOfURLWithFallback(url=item['media$thumbnails'][0]['plfile$url'], fallback=ICON),
						duration = duration,
						originally_available_at = pubdate
					)
				)
	
	
	return oc



def getVideo(url):
	# NB: There is currently an issue doing a Redirect() with this channel from a URL Service for iOS 
	# (and possibly other) devices/clients that result in the video not working on them.
	# There are URL Services wating, once this is sorted out they will be added but for now 
	# I think it's best to release this channel and hold back the URL services as opposed to limiting iOS access.
	# -- Gerk , 2012/06/12

	# url is direct url for our SMIL file
	smil = XML.ElementFromURL(url)
	video_url = smil.xpath("//a:video[1]/@src", namespaces=NAMESPACES)[0]
	return Redirect(video_url)

