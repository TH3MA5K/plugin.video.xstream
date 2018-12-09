# -*- coding: utf-8 -*-
from resources.lib import logger
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser

SITE_IDENTIFIER = 'hdfilme'
SITE_NAME = 'HDfilme'
SITE_ICON = 'hdfilme.png'

URL_MAIN = 'https://hdfilme.net'
URL_MOVIES = URL_MAIN + '/movie-movies?'
URL_SHOWS = URL_MAIN + '/movie-series?'
URL_SEARCH = URL_MAIN + '/movie-search?key=%s'

URL_PARMS_ORDER_UPDATE = 'sort=top'
URL_PARMS_ORDER_UPDATE_ASC = URL_PARMS_ORDER_UPDATE + '&sort_type=asc'
URL_PARMS_ORDER_YEAR = 'sort=year'
URL_PARMS_ORDER_YEAR_ASC = URL_PARMS_ORDER_YEAR + '&sort_type=asc'
URL_PARMS_ORDER_NAME = 'sort=name'
URL_PARMS_ORDER_NAME_ASC = URL_PARMS_ORDER_NAME + '&sort_type=asc'
URL_PARMS_ORDER_VIEWS = 'sort=view'
URL_PARMS_ORDER_VIEWS_ASC = URL_PARMS_ORDER_VIEWS + '&sort_type=asc'
URL_PARMS_ORDER_IMDB = 'sort=imdb'
URL_PARMS_ORDER_IMDB_ASC = URL_PARMS_ORDER_IMDB + '&sort_type=asc'
URL_PARMS_ORDER_HDRATE = 'sort=rate'
URL_PARMS_ORDER_HDRATE_ASC = URL_PARMS_ORDER_HDRATE + '&sort_type=asc'


def load():
    logger.info("Load %s" % SITE_NAME)
    oGui = cGui()
    params = ParameterHandler()
    params.setParam('sUrl', URL_MOVIES)
    oGui.addFolder(cGuiElement('Filme', SITE_IDENTIFIER, 'showMenu'), params)
    params.setParam('sUrl', URL_SHOWS)
    oGui.addFolder(cGuiElement('Serien', SITE_IDENTIFIER, 'showMenu'), params)
    oGui.addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    oGui.setEndOfDirectory()


def showMenu():
    oGui = cGui()
    params = ParameterHandler()
    baseURL = params.getValue('sUrl')
    params.setParam('sUrl', baseURL + URL_PARMS_ORDER_UPDATE)
    oGui.addFolder(cGuiElement('Neu hinzugefügt', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', baseURL + URL_PARMS_ORDER_YEAR)
    oGui.addFolder(cGuiElement('Herstellungsjahr', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', baseURL + URL_PARMS_ORDER_NAME_ASC)
    oGui.addFolder(cGuiElement('Alphabetisch', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', baseURL + URL_PARMS_ORDER_VIEWS)
    oGui.addFolder(cGuiElement('Top Aufrufe', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', baseURL + URL_PARMS_ORDER_IMDB)
    oGui.addFolder(cGuiElement('IMDB Punkt', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', baseURL + URL_PARMS_ORDER_HDRATE)
    oGui.addFolder(cGuiElement('Bewertung HDFilme', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', baseURL)
    oGui.addFolder(cGuiElement('Genre', SITE_IDENTIFIER, 'showGenre'), params)
    oGui.setEndOfDirectory()


def showGenre():
    oGui = cGui()
    params = ParameterHandler()
    entryUrl = params.getValue('sUrl')
    sHtmlContent = cRequestHandler(entryUrl).request()
    pattern = 'Genre</option>.*?</div>'
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)

    if  isMatch:
        pattern = 'value="([^"]+)">([^<]+)'
        isMatch, aResult = cParser.parse(sContainer, pattern)

    if not isMatch:
        oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    for sID, sName in sorted(aResult, key=lambda k: k[1]):
        params.setParam('sUrl', entryUrl + 'category=' + sID + '&country=&sort=&key=&sort_type=desc')
        oGui.addFolder(cGuiElement(sName.strip(), SITE_IDENTIFIER, 'showEntries'), params)
    oGui.setEndOfDirectory()


def showEntries(entryUrl=False, sGui=False, sSearchText=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    if not entryUrl: entryUrl = params.getValue('sUrl')
    iPage = int(params.getValue('page'))
    oRequest = cRequestHandler(entryUrl + '&page=' + str(iPage) if iPage > 0 else entryUrl, ignoreErrors=(sGui is not False))
    sHtmlContent = oRequest.request()
    pattern = '<ul[^>]class="products row">(.*?)</ul>'
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)

    if isMatch:
        pattern = '<div[^>]*class="box-product clearfix"[^>]*>\s*?'
        pattern += '<a[^>]*href="([^"]*)"[^>]*>.*?'
        pattern += '<img[^>]*src="([^"]*)"[^>]*>.*?'
        pattern += '(?:<div[^>]*class="episode"[^>]*>([^"]*)</div>.*?)?'
        pattern += '<div[^>]*class="popover-title"[^>]*>.*?'
        pattern += '<span[^>]*class="name"[^>]*>([^<>]*)</span>.*?'
        pattern += '<div[^>]*class="popover-content"[^>]*>.*?<p>([^<]+)</p>'
        isMatch, aResult = cParser.parse(sContainer, pattern)

    if not isMatch:
        if not sGui: oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    cf = cRequestHandler.createUrl(entryUrl, oRequest)
    total = len(aResult)
    for sUrl, sThumbnail, sEpisodeNr, sName, sDesc in aResult:
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        sThumbnail = sThumbnail.replace('_thumb', '').replace('https://images1-focus-opensocial.googleusercontent.com/gadgets/proxy?container=focus&amp;refresh=31536000&amp;resize_w=135&amp;resize_h=185&amp;url=', '') + cf
        isMatch, sYear = cParser.parse(sName, "(.*?)\((\d*)\)")
        for name, year in sYear:
            sName = name
            sYear = year
            break

        isTvshow = True if sEpisodeNr else False
        if URL_PARMS_ORDER_YEAR in entryUrl and not isTvshow:
            sName += ' (' + str(sYear) + ')'
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showEpisodes' if isTvshow else 'showHosters')
        oGuiElement.setMediaType('tvshow' if isTvshow else 'movie')
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setFanart(sThumbnail)
        oGuiElement.setDescription(sDesc)
        if sYear:
            oGuiElement.setYear(sYear)
        params.setParam('entryUrl', sUrl)
        params.setParam('sName', sName)
        params.setParam('sThumbnail', sThumbnail)
        params.setParam('sDesc', sDesc)
        oGui.addFolder(oGuiElement, params, isTvshow, total)
    if not sGui:
        sPageNr = int(params.getValue('page'))
        if sPageNr == 0:
            sPageNr = 2
        else:
            sPageNr += 1
        params.setParam('page', int(sPageNr))
        params.setParam('sUrl', entryUrl)
        oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setView('tvshows' if URL_SHOWS in entryUrl else 'movies')
        oGui.setEndOfDirectory()


def showEpisodes():
    oGui = cGui()
    params = ParameterHandler()
    sUrl = params.getValue('entryUrl')
    sThumbnail = params.getValue('sThumbnail')
    sDesc = params.getValue('sDesc')
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = 'episode="([\d]+).*?-([\d]+)-stream.*?episode=([\d]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)

    if not isMatch:
        if not sGui: oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    total = len(aResult)
    for eID, sID, eNr in aResult:
        oGuiElement = cGuiElement('Folge ' + eNr , SITE_IDENTIFIER, "showHosters2")
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setFanart(sThumbnail)
        oGuiElement.setDescription(sDesc)
        params.setParam('eID', eID)
        params.setParam('sID', sID)
        oGui.addFolder(oGuiElement, params, False, total)
    oGui.setView('episodes')
    oGui.setEndOfDirectory()


def showHosters2():
    eID = ParameterHandler().getValue('eID')
    sID = ParameterHandler().getValue('sID')
    hosters = []
    sHtmlContent = cRequestHandler(URL_MAIN + '/movie/load-stream/' + sID + '/' + eID + '?server=1').request()

    pattern = 'file":"([^"]+).*?label":"([^"]+)'
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    for sUrl, sName in aResult:
        hoster = {'link': sUrl, 'name': sName}
        hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def showHosters():
    sUrl = ParameterHandler().getValue('entryUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = 'data-episode-id="([^"]+).*?load[^>] "([^"]+)"'
    isMatch, aResult = cParser().parse(sHtmlContent, pattern)
    hosters = []
    if isMatch:
        for sID, sUrl in aResult:
            sHtmlContent = cRequestHandler(URL_MAIN + sUrl + sID + '?server=1').request()
            pattern = 'file":"([^"]+).*?label":"([^"]+)'
            isMatch, aResult = cParser().parse(sHtmlContent, pattern)
            for sUrl, sName in aResult:
                hoster = {'link': sUrl, 'name': sName}
                hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    if 'googleapis' in sUrl:
        return [{'streamUrl': sUrl, 'resolved': True}]
    else:
        return [{'streamUrl': sUrl, 'resolved': False}]


def showSearch():
    oGui = cGui()
    sSearchText = oGui.showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    oGui.setEndOfDirectory()


def _search(oGui, sSearchText):
    showEntries(URL_SEARCH % sSearchText, oGui, sSearchText)
