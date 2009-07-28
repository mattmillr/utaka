'''
Created on Jul 21, 2009
UtakaRequest
wraps an apache request
adds:
	user
	key
	bucket
	subresources - dict of query string keys and vals
	customHeaderPrefix -
	customHeaderTable - dict of headers that began with the customHeaderPrefix, prefix has been stripped
@author: Andrew
'''

from mod_python import apache
from mod_python import util
from utaka.src.rest.HMAC_SHA1_Authentication import getUser
import utaka.src.config as config

class UtakaRequest:

	def __init__(self, req, virtualBucket=False):

		self.req = req
		self.bucket = self.key = None
		self.subresources = {}
		self.__writeBuffer = ''

		#Query string digest
		if self.req.args:
			self.subresources = util.parse_qs(self.req.args, True)
			if 'logging' in self.subresources:
				if 'acl' in self.subresources or 'torrent' in self.subresources or 'location' in self.subresources:
					'''raise error'''
			elif 'acl' in self.subresources:
				if 'torrent' in self.subresources or 'location' in self.subresources:
					'''raise error'''
			elif 'torrent' in self.subresources:
				if 'location' in self.subresources:
					'''raise error'''

		#URI digest
		uriDigestResults = self.uriDigest(req.uri)
		self.bucket = uriDigestResults.get('bucket')
		self.key = uriDigestResults.get('key')

		#custom header table
		try:
			self.customHeaderPrefix = config.get('common', 'customHeaderPrefix').lower()
		except Exception:
			raise apache.SERVER_RETURN, apache.HTTP_INTERNAL_SERVER_ERROR
		else:
			self.customHeaderTable = {}
			for val in self.req.headers_in.keys():
				if val.lower().startswith(self.customHeaderPrefix):
					self.customHeaderTable[val.lower()[len(self.customHeaderPrefix):]] = self.req.headers_in[val]
				
		#authenticate -- must happen after custom header table is created
		self.accesskey, self.signature = self.__getAccessKeyAndSignature()
		self.stringToSign = self.__buildStringToSign()
		self.user, self.computedSig = getUser(self.signature, self.accesskey, self.stringToSign)

		#Check date
		#check customDateHeader then date header
		
		if 'signature' in self.subresources:
			self.write(self.computedSig + "\r\n")
			self.write(self.stringToSign + "\r\n")
			self.write(str(self.subresources) + "\r\n")
			self.send()
		
	def write(self, msg):
		self.__writeBuffer += msg

	def send(self):
		self.req.content_type = 'application/xml'
		self.req.set_content_length(len(self.__writeBuffer))
		self.req.write(self.__writeBuffer)
		
	def uriDigest(self, uri):
		results = {}
		splitURI = uri.split('/', 2)
		for segment in splitURI[:]:
			if len(segment) == 0:
				splitURI.remove(segment)
		if len(splitURI) == 2:
			results['bucket'], results['key'] = splitURI[0], splitURI[1]
		elif len(splitURI) == 1:
			results['bucket'] = splitURI[0]
		return results
		
	def __buildStringToSign(self):
		nl = '\n'

		#http headers
		methodString = self.req.method
		contentMd5String = self.req.headers_in.get('content-md5', '')
		contentTypeString = self.req.headers_in.get('content-type', '')
		dateString = self.req.headers_in.get('date', '')

		#Canonicalize Custom Headers
		__customHeaderPrefix = config.get('common', 'customHeaderPrefix').lower()
		__customDateHeader = __customHeaderPrefix + "-date"

		canCustomHeaders = ''
		customHeaderList = []

		for val in self.req.headers_in.keys():
			if val.lower().startswith(__customHeaderPrefix):
				customHeaderList.insert(val.lower() + ':' + self.req.headers_in[val].lstrip() + nl)
				if val.lower() == __customDateHeader:
					dateString = ''
		customHeaderList.sort()
		for val in customHeaderList:
			canCustomHeaders += val

		#Canoicalize URI
		uriString = self.req.uri
		for val in ('acl',):
			self.write("CHECKING FOR ACL\r\n")
			if val in self.subresources:
				self.write("FOUND ACL\r\n")
				uriString += '?' + val
		return (methodString + nl + contentMd5String + nl +
			contentTypeString + nl + dateString + nl + canCustomHeaders + uriString)
		
		
	def __getAccessKeyAndSignature(self):
		try:
			header = config.get('authentication', 'header')
			prefix = config.get('authentication', 'prefix') + ' '
		except ServerException, e:
			'''raise error'''
		else:
			try:
				authString = self.req.headers_in[header]
			except KeyError:
				return None, None
			else:
				splitAuth = authString.split(prefix)
				if len(splitAuth) == 2 and len(splitAuth[0]) == 0:
					try:
						accesskey, signature = splitAuth[1].split(':')
					except ValueError, e:
						'''raise error'''
					else:
						return accesskey, signature