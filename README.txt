$Id$

--------------------------------------------------
About CPSRSS - Installation procedure
--------------------------------------------------

This product replaces NuxRSS and is intended for use with CPS 3. CPS
2.x users should install NuxRSS.

The current version relies on Mark Pilgrim's Ultraliberal RSS parser. It has
been tested with version 2.5.3, which supports RSS feeds expressed in the
following formats: RSS 0.9x, RSS 1.0 (and RDF/XML-based format) and 2.0.

--------------------------------------------------
HOW TO INSTALL
--------------------------------------------------

- Copy CPSRSS into your zope/Products directory

- It should contain a copy of Mark Pilgrim's Ultraliberal RSS Parser
  (feedreader.py). If it does not, you can get a copy at [1]. You should use
  version 2.5.3 or later. Copy feedreader.py to the CPSRSS directory or to your
  standard zope python lib directory (e.g. lib/python relative to Zope's main
  dir). 
  
  Note: you might also want to get timeoutsocket.py from [2] which is
  used by the parser if present (put it in the same directorty). This is however
  not mandatory, and might cause trouble as it has not yet been extensively 
  tested

[1] http://diveintomark.org/projects/feed_parser/
[2] http://www.timo-tasi.org/python/timeoutsocket.py

-------------------------
The Installer for this product is not yet available, so it is necessary
to follow these steps for now:
-------------------------

-As CPSRSS is not a final product, it is necessary to edit either
getBoxTypes.py in CPSDefault/skins/cps_default or getCustomBoxTypes.py
in your own product and add the following declaration to the list of
items returned:

{'category': 'rssbox',
 'title': 'portal_type_RssBox_title',
 'desc': 'portal_type_RssBox_description',
 'types': [{'provider': 'rss',
            'id': 'default',
            'desc': 'description_rss_rssbox_default'},
           ]
 },

If you forget to do that, you will probably get something like a
TypeError when attempting to add an RSS Box in your portal.

Note: it might be necessary to restart your Zope server after this step.

- Open the ZMI and go to the CPS main dir

- Add an RSS Tool from the drop down list, which will create a portal_rss tool

- Select portal_rss and add a channel, then enter an ID and the feed's URL in
  the 'Channel URL' field. Remember the ID as it will be required later for
  linking a box to the channel (we will refer to it later as channel_id).

- You can then test that the feed is retrieved correctly by going to the
  refresh tab of the portal_rss tool, clicking refresh, and then selecting your
  channel (properties).  The title and description should now be filled by
  values retrieved from the actual feed.

- Check new_window if you want news items links to open in blank
  windows instead of the current one.

- In portal_types, add a Factory-based Type Information ; select
  CPSRSS: RSS Box
 
- Back again to CPS's root, select portal_skins. Add a FileSystem Directory
  View object and choose CPSRSS/skins. Assign an ID to the
  newly-created layer, and then insert it in the list of layers of all skins
  that should use it (e.g. Basic) by going back to the properties tab of
  portal_skins. Don't forget to save.

- Go to the box management interface on the CPS site ; add an RSS Box and fill
  the Channel field with the channel_id you should have remembered
  Note: a future version of CPSRSS will probably offer a drop-down list containing
  all available channel_ids so that people do not have to know/remember those 


--------------------------------------------------
RSS Tool configuration
--------------------------------------------------

It is possible to configure some options in the properties tab of the
portal_rss tool. These options apply to all channels:

- lazy_refresh: check this box if the channel's content should not be
  updated each time the page is reloaded, but only when a given amount
  of time (specified by refresh_delay in seconds) has elapsed since the 
  last refresh.

- refresh_delay: see above item

If lazy_refresh is not checked, the channels will be refreshed each time
a page containing boxes displaying them is reloaded. Note that the underlying
RSS parser features its own mechanism to download the feed only if it changed
since the last time it checked for it.