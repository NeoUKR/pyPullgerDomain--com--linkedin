import time
import pullgerSquirrel as squirrel

from pullgerFootPrint.com.linkedin.search import people as linkedinSearchPeopleFootPrint
from pullgerFootPrint.com.linkedin.people import card as linkedinPeopleCardFootPrint
from pullgerFootPrint.com.linkedin import general as linkedinGeneral, authorization as linkedinAuthorizationFootPrint
from pullgerExceptions import *

LOGGER_NAME = "pullgerDomain.com.linkedin.port"

class Domain:
    __slots__ = (
        '_authorizated',
        '_connected',
        '_squirrel',
        '_initialized',
        '_squirrel_initialized',
        '_RootLoaded',
    )

    @property
    def authorizated(self):
        return self._authorizated
    @property
    def connected(self):
        return self._connected
    @property
    def initialized(self):
        return self._initialized
    @property
    def squirrel_initialized(self):
        return self._squirrel_initialized
    @property
    def RootLoaded(self):
        return self._RootLoaded

    def __init__(self, sqirrel = None):
        self._authorizated = False
        self._connected = False
        self._squirrel = None
        self._initialized = False
        self._squirrel_initialized = False
        self._RootLoaded = None

        if sqirrel == None:
            self._squirrel = squirrel.Squirrel(squirrel.Connectors.selenium)
        else:
            self._squirrel = sqirrel

        if self._squirrel.initialized != True:
            self._squirrel.initialize()

        self._squirrel_initialized = self._squirrel.initialized
        self._initialized = self._squirrel.initialized

    def createPeopleSubject(self, **kwargs):
        newSubject = PeopleSubject(self)

        if 'id' in kwargs: newSubject.id = kwargs['id']
        if 'nick' in kwargs: newSubject.nick = kwargs['nick']

        return newSubject

    def connect(self):
        if self._initialized == True:
            url = 'https://www.linkedin.com/'
            try:
                if self._squirrel_initialized != None:
                    if self._squirrel.get(url) == False:
                        raise excDomain_Connect_System(f'Unefine error on create connection to URL:{url}', loggerName=LOGGER_NAME, level=50)
                else:
                    raise excDomain_Connect(f'Squirell not initialized!!', loggerName=LOGGER_NAME, level=50)
            except BaseException as e:
                raise excDomain_Connect_System(f'Cant create connection to URL:{url}.', loggerName=LOGGER_NAME, level=50, exception=e)

            self._connected = True
        else:
            raise excDomain_Connect_System(f'Domain not initialized!!', loggerName=LOGGER_NAME, level=50)

    def disconect(self):
        self.close()

    def close(self):
        self._squirrel.close();

    def authorization(self, inUserName, inPassword):
        if self._initialized == True:
            if self._connected != True:
                self.connect()

            if self._connected == True:
                time.sleep(2)

                if linkedinAuthorizationFootPrint.setUserName(self._squirrel, inUserName) == True:
                    time.sleep(1)

                    if linkedinAuthorizationFootPrint.setPassword(self._squirrel, inPassword) == True:
                        time.sleep(1)

                        if linkedinAuthorizationFootPrint.singIn(self._squirrel) == True:
                            time.sleep(5)

                            if self._squirrel.find_XPATH('//div[@id="app__container"]', True) != None:
                                mainSection = self._squirrel.find_XPATH('.//main')
                                raise excDomain_Authorization_ResultCheck(f'Authentification error: {mainSection.text}', loggerName=LOGGER_NAME, level=40)
                        else:
                            raise excDomain_Authorization_InputProcess(f'Incorrect sing in operation.', loggerName=LOGGER_NAME, level=40)
                    else:
                        raise excDomain_Authorization_InputProcess(f'Incorrect password set on authorization', loggerName=LOGGER_NAME, level=40)
                else:
                    raise excDomain_Authorization_InputProcess(f'Incorrect user set on authorization', loggerName=LOGGER_NAME, level=40)
            else:
                raise excDomain_Authorization(f"No connection to domain", loggerName=LOGGER_NAME, level=50)
        else:
            raise excDomain_Authorization(f"Can't do authorization - domain not initialazed", loggerName=LOGGER_NAME, level=50)

        self._authorizated = True;

    def isPageCorrect(self):
        isError = False

        errorSection = self.squirrel.find_XPATH('//section[@class="global-error artdeco-empty-state ember-view"]')
        if errorSection != None: isError = True;

        if isError == False:
            splitedURL = list(filter(None, self.squirrel.current_url.split('/')))
            if not (splitedURL[2] == 'company' or splitedURL[2] == 'school'): isError = True

            if isError == False:
                if splitedURL[-1] == 'unavailable': isError = True

        return not isError

    def search(self, searchScope, locationsArray, keywords):
        geoUrn = '';
        prefixRequest = '&'

        if len(locationsArray) != 0:
            geoUrn = 'geoUrn=%5B'

        prefix = '';
        for curLocation in locationsArray:
            geoUrn = geoUrn + prefix + '"' + str(curLocation) + '"'
            prefix = '%2C'

        if geoUrn != "":
            geoUrn = geoUrn + '%5D'

        url = "https://www.linkedin.com/search/results/" + searchScope + "/?origin=FACETED_SEARCH"
        if geoUrn != '':
            url = url + prefixRequest + geoUrn

        url = url + prefixRequest + 'keywords=' + keywords

        self._squirrel.get(url)

    def getCountOfResults(self):
        return linkedinSearchPeopleFootPrint.getCountOfResults(self._squirrel)

    def getListOfPeoples(self):
        return linkedinSearchPeopleFootPrint.getListOfPeoples(self._squirrel)

    def listOfPeopleNext(self):
        result = None;

        self._squirrel.send_PAGE_DOWN()
        time.sleep(1)
        self._squirrel.send_PAGE_DOWN()
        time.sleep(1)

        CurPagination = linkedinSearchPeopleFootPrint.getNumberCurentPaginationPage(self._squirrel)
        LastPagination = linkedinSearchPeopleFootPrint.getNumberLastPaginationPage(self._squirrel)
        if CurPagination != None and LastPagination != None:
            if CurPagination < LastPagination:
                result = linkedinSearchPeopleFootPrint.pushNextPaginationButton(self._squirrel)
            else:
                result = False;
        return result

    def getPerson(self, **kwargs):

        if 'in' in kwargs or 'nick' in kwargs:
            objPeople = self.createPeopleSubject(**kwargs)
            objPeople.getPage()

            return objPeople

class PeopleSubject(Domain):
    id = None
    nick = None

    def __init__(self, childrenClassObject):
        self._authorizated = childrenClassObject._authorizated
        self._connected = childrenClassObject._connected
        self._squirrel = childrenClassObject._squirrel
        self._squirrel_initialized = childrenClassObject._squirrel_initialized
        self._RootLoaded = childrenClassObject._RootLoaded

    def getPage(self):
        if self._authorizated == True:
            prefix = 'www'
            if self.nick != None:
                identificator = self.nick;
            else:
                identificator = self.id;
        else:
            prefix = 'be'
            identificator = self.nick;
        time.sleep(1)
        self._squirrel.get(f'https://{prefix}.linkedin.com/in/{identificator}')
        # ?trk=public_profile_experience-group-header
        checkCorrection = self.isPageCorrect()
        if checkCorrection != True:
            raise Exception(checkCorrection)
        time.sleep(1)

    def isPageCorrect(self):
        isNoError = True

        if self._authorizated == False:
            errorSection = self._squirrel.find_XPATH('//section[@class="profile"]')
        else:
            errorSection = self._squirrel.find_XPATH('//section[@class="artdeco-card ember-view pv-top-card"]')

        if errorSection == None:
            markerCkeckpoint = self._squirrel.current_url.find('checkpoint')
            if markerCkeckpoint != -1:
                isNoError = True;

            else:
                isNoError = 'incorrect page';

        return isNoError

    @staticmethod
    def getCleanedURL(url):
        return linkedinGeneral.getCleanedURL(url)

    @staticmethod
    def checkNick(nick):
        return linkedinGeneral.checkNick(nick)

    @staticmethod
    def getNickFromURL(url):
        return linkedinGeneral.getNickFromURL(url)

    def getListOfExperience(self):
        self._squirrel.get(f'{self._squirrel.current_url}details/experience/')

        time.sleep(2)
        self._squirrel.send_PAGE_DOWN()
        time.sleep(1)
        self._squirrel.send_PAGE_DOWN()
        time.sleep(1)
        self._squirrel.send_END()
        time.sleep(1)
        return linkedinPeopleCardFootPrint.getListOfExperience(self._squirrel);