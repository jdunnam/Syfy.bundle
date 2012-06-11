NAME = 'Syfy'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

# gives us basic list of Show/Showname
SHOWSLIST="http://feed.theplatform.com/f/hQNl-B/sgM5DlyXAfwt/categories?&form=json&fields=fullTitle,title&q=fullTitle:Shows"

# use %s as format of Shows/Showname, returns only full episodes guids
EPISODESGUIDS="http://feed.theplatform.com/f/hQNl-B/2g1gkJT0urp6/?&form=json&fields=guid&fileFields=duration,url,width,height&byCategories=%s&byCustomValue=%7BfullEpisode%7D%7Btrue%7D&count=true"

# use %s as format guid|guid|guid|guid) -- returns main show's SMIL url as $url
EPISODESINFO="http://feed.theplatform.com/f/hQNl-B/2g1gkJT0urp6/?&form=json&fields=guid,title,description,:subtitle,content,thumbnails,categories,:fullEpisode,:disallowSharing%20&fileFields=url,duration,width,height,contentType,fileSize,format&byGuid=%s"

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



def getAllShows():
	oc = ObjectContainer (view_group='List')
	
	data=JSON.ObjectFromURL(SHOWSLIST)
	for item in data['entries']:
		oc.add(
			DirectoryObject(key=Callback(getShowList,show=item['plcategory$fullTitle']),title=item['title'])
		)
	return oc


def getShowList(show):
	#Log("Gerk: show passed: %s",show)
	oc = ObjectContainer (view_group='List')
	show = show.replace(' ','+')
 	showurl="http://feed.theplatform.com/f/hQNl-B/2g1gkJT0urp6/?&form=json&fields=guid&fileFields=duration,url,width,height&byCategories="+show+"&byCustomValue=%7BfullEpisode%7D%7Btrue%7D&count=true"

	guids=""	

	data=JSON.ObjectFromURL(showurl)
	for item in data['entries']:
		guids=guids+item['guid']+"|"

# 	# Now Let's grab any other content they have here that are not full episodes
#  	showurl="http://feed.theplatform.com/f/hQNl-B/2g1gkJT0urp6/?&form=json&fields=guid&fileFields=duration,url,width,height&byCategories="+show+"&count=true"
# 	data=JSON.ObjectFromURL(showurl)
# 	for item in data['entries']:
# 		guids=guids+item['guid']+"|"

	if guids == "":
		oc = MessageContainer("Ooops!","There appears to be no available videos here.")
		return oc
		
		
		
	episodeurl="http://feed.theplatform.com/f/hQNl-B/2g1gkJT0urp6/?&form=json&fields=guid,title,description,:subtitle,content,thumbnails,pubdate,categories,:fullEpisode,:disallowSharing%20&fileFields=url,duration,width,height,contentType,fileSize,format&byGuid="+guids

	showdata = JSON.ObjectFromURL(episodeurl)

	for item in showdata['entries']:
		for v in item['media$content']:
			#Log(v)
			if v['plfile$format']=="MPEG4" and v['plfile$height']==720:				
				# this is the 720p mpeg4
				duration = int(float(item['media$content'][0]['plfile$duration'])*1000)
				pubdate = Datetime.FromTimestamp(int(item['pubDate']/1000))
				title=item['title']

				oc.add(
					EpisodeObject(
# 						key = Callback(getVideo,url=v['plfile$url']),
# 						rating_key = v['plfile$url'],
						url = "http://www.syfy.com/videos/vid:"+item['guid'],
						title=title,
						thumb = Resource.ContentsOfURLWithFallback(url=item['media$thumbnails'][0]['plfile$url'], fallback=ICON),
						duration = duration,
						originally_available_at = pubdate
					)
				)
	
	
	return oc



def getVideo(url):
	# url is for our SMIL file
	smil = XML.ElementFromURL(url)
	video_url = smil.xpath("//a:video[1]/@src", namespaces=NAMESPACES)[0]
	#Log(video_url)
	return Redirect(video_url)

