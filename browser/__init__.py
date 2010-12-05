# python package

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CPSonFive.browser import AqSafeBrowserView

class LocalRSSChannelsManagement(AqSafeBrowserView):

    def __init__(self, *args, **kwargs):
        AqSafeBrowserView.__init__(self, *args, *kwargs)
        self.aqSafeSet('container', self.lookupContainer())

    def lookupContainer(self):
        """Lookup the relevant container and set it up on self."""
        folder = self.context.aq_inner

        if cont_id is not None:
            try:
                cont = folder[cont_id]
            except KeyError:
                return None
            if not IRSSChannelContainer.providedBy(cont):
                return None

        # coding style that works if objectValues turns out to be a generator
        for cont in folder.objectValues([RSSChannelContainer.meta_type]):
            return cont

    def has_container(self):
        return self.aqSafeGet('container') is not None

    def channels(self):
        cont = self.aqSafeGet('container')
        if cont is None:
            return ()
        return cont.objectValues([RSSChannel.meta_type])
