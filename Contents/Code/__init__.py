NAME = 'Syfy'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

# gives us basic list as Show/Showname
SHOWSLIST="http://feed.theplatform.com/f/hQNl-B/sgM5DlyXAfwt/categories?&form=json&fields=fullTitle,title&q=fullTitle:Shows"

NAMESPACES = {"a":"http://www.w3.org/2005/SMIL21/Language"}


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



####################################################################################################
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


####################################################################################################
def getShowList(show):
	oc = ObjectContainer (view_group='InfoList')
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
	for item in data['entries']:
		guids=guids+item['guid']+"|"

	if guids == "":
		oc = MessageContainer("Sorry","There appears to be no full episodes available for this show.")
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
				thumbs = SortImages(item['media$thumbnails'])
				Log("http://www.syfy.com/videos/vid:"+item['guid'])
				oc.add(
					EpisodeObject(
						url = "http://www.syfy.com/videos/vid:"+item['guid'],
						title=title,
						thumb = Resource.ContentsOfURLWithFallback(url=thumbs, fallback=ICON),
						duration = duration,
						originally_available_at = pubdate
					)
				)
	
	
	return oc


####################################################################################################
def SortImages(images=[]):
    
    sorted_thumbs = sorted(images, key=lambda thumb : int(thumb['plfile$height']), reverse=True)
    thumb_list = []
    for thumb in sorted_thumbs:
        thumb_list.append(thumb['plfile$url'])

    return thumb_list

