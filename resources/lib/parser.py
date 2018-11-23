# -*- coding: utf-8 -*-
import re

class cParser:
    @staticmethod
    def parseSingleResult(sHtmlContent, pattern):
        aMatches = re.compile(pattern).findall(sHtmlContent)
        if len(aMatches) == 1:
            aMatches[0] = cParser.__replaceSpecialCharacters(aMatches[0])
            return True, aMatches[0]
        return False, aMatches

    @staticmethod
    def __replaceSpecialCharacters(sString):
        return sString.replace('\\/', '/')

    @staticmethod
    def parse(sHtmlContent, pattern, iMinFoundValue=1, ignoreCase=False):
        sHtmlContent = cParser.__replaceSpecialCharacters(sHtmlContent)
        if ignoreCase:
            aMatches = re.compile(pattern, re.DOTALL | re.I).findall(sHtmlContent)
        else:
            aMatches = re.compile(pattern, re.DOTALL).findall(sHtmlContent)
        if len(aMatches) >= iMinFoundValue:
            return True, aMatches
        return False, aMatches

    @staticmethod
    def replace(pattern, sReplaceString, sValue):
        return re.sub(pattern, sReplaceString, sValue)

    @staticmethod
    def search(sSearch, sValue):
        return re.search(sSearch, sValue, re.IGNORECASE)

    @staticmethod
    def escape(sValue):
        return re.escape(sValue)

    @staticmethod
    def getNumberFromString(sValue):
        pattern = "\d+"
        aMatches = re.findall(pattern, sValue)
        if len(aMatches) > 0:
            return int(aMatches[0])
        return 0
