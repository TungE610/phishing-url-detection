#-----------------------------------------------------------------------------
# Name:        PyLongURL.py
# Purpose:     Python Library for expanding short url using longurl.org API
#              More information on longurl.org API can be found at:
#                http://longurl.org/api.
# Author:      Ram B. Basnet rambasnet@gmail.com
#
# Created:     2010/08/12
# RCS-ID:      $Id: PyLongURL.py $
# Copyright:   (c) 2010
# Licence:     MIT License.
#-----------------------------------------------------------------------------

import urllib, urllib2
from urllib2 import HTTPError
from urlparse import urlsplit
import xml.dom.minidom
from xml.dom.minidom import Node


class APIError(Exception):
	def __init__(self, msg, error_code=None):
		self.msg = msg

	def __str__(self):
		return repr(self.msg)

__author__ = "Ram B. Basnet <rambasnet@gmail.com>"
__version__ = "1"

"""
    PyLongURL - longurl.org API in Python.
"""
class URLExpander:
    def __init__(self, userAgent=None):
        #the base URL is where ARIN is hosting the whois service
        self.baseURL = 'http://api.longurl.org/v2/'
        
        self.opener = urllib2.build_opener()
        
        if userAgent is None:
            raise APIError("All Requests must include a descriptive User-Agent header.")
            
        self.UserAgent = userAgent
        
        self.opener.addheaders = [('User-agent', self.UserAgent)]
        
        self.URLShorteningServicesList = []
        
        xmlDoc = xml.dom.minidom.parseString(self.GetURLShorteningServices(format='xml'))
        
        """ returned data has the following format: 
            {"0rz.tw":{"domain":"0rz.tw","regex":""},"2tu.us":{"domain":"2tu.us","regex":""},"3.ly":{"domain":"3.ly","regex":""},...
            
        """
        serviceNodes = xmlDoc.getElementsByTagName('service')
        for node in serviceNodes:
            for childNode in node.childNodes:
                if childNode.nodeType == Node.TEXT_NODE:
                    self.URLShorteningServicesList.append(childNode.data)

         
    def ConstructApiURL(self, baseUrl, shortUrl, params):
        return baseUrl + "expand?url=" + urllib.quote_plus(shortUrl) + "&user-agent=" + self.UserAgent + "&" + "&".join(["%s=%s" %(key, value) for (key, value) in params.iteritems()])
    
    def GetURLShorteningServices(self, format="xml"):
        """
            Return URL Shortening Services supported by longurl.org in the given format.
        """
        url = "%sservices?format=%s"%(self.baseURL, format)
        #print url
        return self.Request(url)
       
    def Request(self, url):
        try:
            return self.opener.open(url).read()
        except HTTPError:
            raise APIError("Request() failed with a %s error code.")
    
    def Expand(self, shortUrl, **kwargs):
        """
            Method that supports all the parameters supported by longurl.org's Expand URL API.
            The retured results must be parsed according to the requested format type. The default format is xml.
            Parameters:
            url
            The short URL which is to be expanded. The must start with http:// or https://, and should be URL encoded.
            all-redirects (optional)
            Set value to 1 to include all HTTP redirects in the response. Example
            content-type (optional)
            Set value to 1 to include the internet media type of the destination URL in the response. Example
            response-code (optional)
            Set value to 1 to include the HTTP response code of the destination URL in the response. Example
            title (optional)
            Set value to 1 to include the HTML title of the destination URL in the response (if a web page). Example
            rel-canonical (optional)
            Set value to 1 to include the canonical URL of the destination URL in the response (if a web page). Example
            meta-keywords (optional)
            Set value to 1 to include the meta keywords of the destination URL in the response (if a web page). Example
            meta-description (optional)
            Set value to 1 to include the meta description of the destination URL in the response (if a web page). Example
            format (optional)
            Response format. Could be xml (default), json, or php.
            callback (optional)
            Callback function name. Only used for JSONP. Requires that the format argument be set to json.
        """
        # To avoid unnecessary request: 
        # Check Url format. Must start with http or https
        # Check if the url shortner service is supported by longurl.org
        urlComponents = urlsplit(shortUrl)
        
        if urlComponents.scheme != 'http' and urlComponents.scheme != 'https':
            raise APIError("ExpandURL() failed! Short URL started with %s. It must start with http:// or https:// "%(urlComponents.scheme))
        
        
        netLoc = urlComponents.netloc
        
        if netLoc not in self.URLShorteningServicesList:
            raise APIError("ExpandUrl() failed! URL Shortener service %s is not supported by longurl.org."%netLoc)
        
        
        url = self.ConstructApiURL(self.baseURL, shortUrl, kwargs)

        return self.Request(url)
    
    def ExpandURL(self, shortUrl):
        """
        Expand a given short URL without any supported Aurguments.
        If you want to get just the long url of a given short url quickly,
        this is the easier method.
        """
        doc = xml.dom.minidom.parseString(self.Expand(shortUrl))
        nodes = doc.getElementsByTagName('long-url')
        for node in nodes:
            for childNode in node.childNodes:
                return childNode.data
                    

    
def Test():
    expander = URLExpander('Ram B. Basnet - PhD Research, NMT')
    longUrl = expander.Expand('http://is.gd/w', format='xml')
    """
    <?xml version="1.0"?>
    <response>
        <long-url><![CDATA[http://www.google.com/]]></long-url>
    </response>
    """
    doc = xml.dom.minidom.parseString(longUrl)
    nodes = doc.getElementsByTagName('long-url')
    for node in nodes:
        for dataNode in node.childNodes:
            print(dataNode.data)
            
    print(expander.ExpandURL('http://bit.ly/w'))
            
if __name__ == "__main__":
    Test()
    
        