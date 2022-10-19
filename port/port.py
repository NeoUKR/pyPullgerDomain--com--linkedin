import time
import pullgerSquirrel

from pullgerFootPrint.com.linkedin.search import people as linkedinSearchPeopleFootPrint
from pullgerFootPrint.com.linkedin.people import card as linkedinPeopleCardFootPrint
from pullgerFootPrint.com.linkedin import general as linkedinGeneral, authorization as linkedinAuthorizationFootPrint
from pullgerInternalControl import pIC_pD


class Domain:
    __slots__ = (
        '_authorized',
        '_connected',
        '_squirrel',
        '_initialized',
        '_squirrel_initialized',
        '_RootLoaded',
    )

    @property
    def authorized(self):
        return self._authorized

    @property
    def connected(self):
        return self._connected

    @property
    def squirrel(self):
        return self._squirrel

    @property
    def initialized(self):
        return self._initialized

    @property
    def squirrel_initialized(self):
        return self._squirrel_initialized

    @property
    def RootLoaded(self):
        return self._RootLoaded

    def __init__(self, squirrel: pullgerSquirrel = None):
        self._authorized = False
        self._connected = False
        self._squirrel = None
        self._initialized = False
        self._squirrel_initialized = False
        self._RootLoaded = None

        if squirrel is None:
            self._squirrel = pullgerSquirrel.Squirrel(pullgerSquirrel.Connectors.selenium)
        else:
            self._squirrel = squirrel

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
        if self._initialized is True:
            url = 'https://www.linkedin.com/'
            try:
                if self._squirrel_initialized is not None:
                    if self._squirrel.get_page(url=url) is False:
                        raise pIC_pD.connect.System(
                            f'Undefined error on create connection to URL:{url}',
                            level=50
                        )
                else:
                    raise pIC_pD.connect.General(
                        f'Squirrel not initialized!!',
                        level=50
                    )
            except BaseException as e:
                raise pIC_pD.connect.System(
                    f'Cant create connection to URL:{url}.',
                    level=50,
                    exception=e
                )

            self._connected = True
        else:
            raise pIC_pD.connect.System(
                f'Domain not initialized!!',
                level=50
            )

    def disconect(self):
        self.close()

    def close(self):
        self._squirrel.close();

    def authorization(self, user_name: str, password: str):
        squirrel = self._squirrel

        if self._initialized is True:
            if self._connected is not True:
                self.connect()

            if self._connected is True:
                time.sleep(2)

                if linkedinAuthorizationFootPrint.set_user_name(squirrel=squirrel, user_name=user_name) is True:
                    time.sleep(1)

                    if linkedinAuthorizationFootPrint.set_password(squirrel=squirrel, password=password) is True:
                        time.sleep(1)

                        if linkedinAuthorizationFootPrint.sing_in(squirrel=squirrel) is True:
                            time.sleep(5)

                            if self.squirrel.find_xpath(xpath="//div[@id='app__container']") is not None:
                                mainSection = self.squirrel.find_xpath('.//main')
                                raise pIC_pD.connect.System(
                                    f'Authentication error: {mainSection.text}',
                                    level=40
                                )
                        else:
                            raise pIC_pD.authorization.InputProcess(
                                f'Incorrect sing in operation.',
                                level=40
                            )
                    else:
                        raise pIC_pD.authorization.InputProcess(
                            f'Incorrect password set on authorization',
                            level=40
                        )
                else:
                    raise pIC_pD.authorization.InputProcess(
                        f'Incorrect user set on authorization',
                        level=40
                    )
            else:
                raise pIC_pD.authorization.General(
                    f"No connection to domain",
                    level=50
                )
        else:
            raise pIC_pD.authorization.General(
                f"Can't do authorization - domain not initialized",
                level=50
            )

        self._authorized = True

    def is_page_correct(self):
        isError = False

        errorSection = self.squirrel.find_xpath('//section[@class="global-error artdeco-empty-state ember-view"]')
        if errorSection is not None: isError = True

        if isError is False:
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

        self._squirrel.send_page_down()
        time.sleep(1)
        self._squirrel.send_page_down()
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
        self._authorized = childrenClassObject._authorized
        self._connected = childrenClassObject._connected
        self._squirrel = childrenClassObject._squirrel
        self._squirrel_initialized = childrenClassObject._squirrel_initialized
        self._RootLoaded = childrenClassObject._RootLoaded

    def getPage(self):
        if self._authorized is True:
            prefix = 'www'
            if self.nick is not None:
                identificator = self.nick;
            else:
                identificator = self.id;
        else:
            prefix = 'be'
            identificator = self.nick;
        time.sleep(1)
        self._squirrel.get(f'https://{prefix}.linkedin.com/in/{identificator}')
        # ?trk=public_profile_experience-group-header
        checkCorrection = self.is_page_correct()
        if checkCorrection is not True:
            raise pIC_pD.pages.Incorrect(
                msg=checkCorrection,
                level=30
            )
        time.sleep(1)

    def is_page_correct(self):
        isNoError = True

        if self._authorized is False:
            errorSection = self._squirrel.find_xpath('//section[@class="profile"]')
        else:
            errorSection = self._squirrel.find_xpath('//section[@class="artdeco-card ember-view pv-top-card"]')

        if errorSection == None:
            markerCkeckpoint = self._squirrel.current_url.find('checkpoint')
            if markerCkeckpoint != -1:
                isNoError = True

            else:
                isNoError = 'incorrect page';

        return isNoError

    @staticmethod
    def getCleanedURL(url):
        return linkedinGeneral.get_cleaned_url(url)

    @staticmethod
    def checkNick(nick):
        return linkedinGeneral.checkNick(nick)

    @staticmethod
    def getNickFromURL(url):
        return linkedinGeneral.getNickFromURL(url)

    def get_list_of_experience(self):
        self._squirrel.get(f'{self._squirrel.current_url}details/experience/')

        time.sleep(2)
        self._squirrel.send_page_down()
        time.sleep(1)
        self._squirrel.send_page_down()
        time.sleep(1)
        self._squirrel.send_end()
        time.sleep(1)
        return linkedinPeopleCardFootPrint.get_list_of_experience(self._squirrel);
