$Id$

--------------------------------------------------
About CPSRSS
--------------------------------------------------

Want to display syndicated content on your CPS portal? This product adds a new
type of box to CPS 3.x. You then can lay out RSS feeds using the boxes
management form. Available feeds are centralized in the portal_rss tool.

Administrators can set globally how many entries are to show, and local managers
can change this setting for displaying less entries.

The feeds can be refreshed at each access or "lazily", after the given timeout.
This caching reduces overload and avoid increasing response time because of slow
syndicated sites.

The current version relies on Mark Pilgrim's Ultraliberal RSS parser. It has
been tested with version 2.5.3, which supports RSS feeds expressed in the
following formats: RSS 0.9x, RSS 1.0 (and RDF/XML-based format) and 2.0.

Note to CPS 2 users:

  This product is intended for use with CPS 3.x only. You should still use
  NuxRSS along with CPS 2.x.

--------------------------------------------------
HOW TO INSTALL
--------------------------------------------------

- Copy CPSRSS into your zope/Products directory

- It should contain a copy of Mark Pilgrim's Ultraliberal RSS Parser
  (feedreader.py). If it does not, you can get a copy at [1]. You should use
  version 2.5.3 or later. Copy feedparser.py to the CPSRSS directory or to your
  standard zope python lib directory (e.g. lib/python relative to Zope's main
  dir).

[1] http://diveintomark.org/projects/feed_parser/

- An Installer is now available for CPSRSS, but you still need to do one manual
  operation: as CPSRSS is not a final product, it is necessary to edit either
  getBoxTypes.py in CPSDefault/skins/cps_default or getCustomBoxTypes.py in
  your own product and add the following declaration to the list of items
  returned:

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

- The remainder of the installation process is straightforward, as it
  consists in executing the product's installer (as you would for any other
  product).

- From the ZMI, go to the CPS root, instantiate an External Method with the
  following parameters:
  ID = any Id you want, like cpsrssinst
  Title = anything you want, like CPSRSS Installer
  Module Name = CPSRSS.install
  Function Name = install

- Execute the script by going to the Test tab. This should automatically create
  a portal_rss tool, an RSS Box portal_type, a cps_rss portal_skin and it
  should insert cps_rss in the list of layers for skin Basic.

- You can then add channels through the tool as follows.

- Select portal_rss and add a channel, then enter an ID and the feed's URL in
  the 'Channel URL' field.

- You can test that the feed is retrieved correctly by going to the refresh tab
  of the portal_rss tool, clicking refresh, and then selecting your channel
  (properties).  The title and description should now be filled by values
  retrieved from the actual feed.

- Check new_window if you want news items links to open in blank
  windows instead of the current one.

- check HTML feed if the feed's URL already provides HTML that you do not want
  to be transformed (this will just retrieve the HTML fragment at the given URL
  and put it in the RSS Box).

- It is also possible to limit the number of items displayed for a given feed,
  by entering a non-zero integer value in field nbMaxItems. Value zero is the
  default value and displays all items (no limit).

- Go to the box management interface on the CPS site ; add an RSS Box and
  select a channel from the drop-down list (which contains all channels
  configured in portal_rss). Save your changes. An RSS Box should now be
  visible in your portal.
  Its location depends on the slot you selected, as for any other box.


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
