##parameters=**kw
"""This script is deprecated in favor of direct call to a view.
"""

portal = context.portal_url.getPortalObject()
view = portal.restrictedTraverse('@@channels_restricted')
return view.rssItems(cont_id='portal_rss', **kw)
