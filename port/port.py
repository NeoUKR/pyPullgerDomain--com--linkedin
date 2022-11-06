import time
import importlib

import pullgerSquirrel

from pullgerFootPrint.com.linkedin.search import people as linkedinSearchPeopleFootPrint
from pullgerFootPrint.com.linkedin.people import card as linkedinPeopleCardFootPrint
from pullgerFootPrint.com.linkedin import general as linkedinGeneral
# from pullgerFootPrint.com.linkedin import authorization
# from pullgerFootPrint.com.linkedin import authorization as linkedinAuthorizationFootPrint
from pullgerAccountManager import authorizationsServers
from pullgerSquirrel import connectors

from . import port_functions

from pullgerInternalControl import pIC_pD


class Domain:
    __slots__ = (
        '_authorized',
        '_connected',
        '_squirrel',
        '_initialized',
        '_squirrel_initialized',
        '_RootLoaded'
    )

    @staticmethod
    def required_authorization_servers_options():
        authorization_list = [
            authorizationsServers.linkedin.instances.general,
        ]

        response = {}
        for cur_auth in authorization_list:
            response[str(cur_auth)] = cur_auth

        return response

    @staticmethod
    def required_connector_options():
        connectors_list = [
            connectors.connector.selenium.chrome.standard,
        ]

        response = {}
        for cur_connector in connectors_list:
            response[str(cur_connector)] = cur_connector

        return response

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
            self._squirrel = pullgerSquirrel.Squirrel(connectors.connector.selenium.chrome)
        else:
            self._squirrel = squirrel

        if self._squirrel.initialized is not True:
            self._squirrel.initialize()

        self._squirrel_initialized = self._squirrel.initialized
        self._initialized = self._squirrel.initialized

    def createPeopleSubject(self, id_person: int = None, nick: str = None, **kwargs):
        newSubject = PeopleSubject(self)
        newSubject.id = id
        newSubject.nick = nick
        return newSubject

    def create_company_subject(self, id_company: int):
        from .port_companies import CompanyDomain
        new_subject = CompanyDomain(self)
        new_subject.id_company = id_company
        return new_subject


        return new_subject

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
        importlib.reload(port_functions)
        port_functions.authorization(self, user_name, password)

    def is_page_correct(self):
        is_error = False

        errorSection = self.squirrel.find_xpath('//section[@class="global-error artdeco-empty-state ember-view"]')
        if errorSection is not None:
            is_error = True

        if is_error is False:
            split_url = list(filter(None, self.squirrel.current_url.split('/')))
            if not (is_error[2] == 'company' or is_error[2] == 'school'):
                isError = True

            if is_error is False:
                if isError[-1] == 'unavailable':
                    isError = True

        return not isError

    def search(self, search_scope: str, locations_list: list, keywords: str):
        geoUrn = ''
        prefixRequest = '&'

        if len(locations_list) != 0:
            geoUrn = 'geoUrn=%5B'

        prefix = ''
        for curLocation in locations_list:
            geoUrn = geoUrn + prefix + '"' + str(curLocation) + '"'
            prefix = '%2C'

        if geoUrn != "":
            geoUrn = geoUrn + '%5D'

        url = "https://www.linkedin.com/search/results/" + search_scope + "/?origin=FACETED_SEARCH"
        if geoUrn != '':
            url = url + prefixRequest + geoUrn

        url = url + prefixRequest + 'keywords=' + keywords

        self._squirrel.get(url)

    def get_count_of_results(self):
        return linkedinSearchPeopleFootPrint.getCountOfResults(self._squirrel)

    def get_list_of_peoples(self):
        return linkedinSearchPeopleFootPrint.get_list_of_peoples(self._squirrel)

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

    def get_person(self, id_person: int = None, nick: str = None, **kwargs):

        if nick is not None:
            objPeople = self.createPeopleSubject(id_person=id_person, nick=nick, **kwargs)
            objPeople.getPage()
            return objPeople

    def get_company(self, id_element: int):
        obj_company = self.create_company_subject(id_element=id_element)
        obj_company.get_page()

        return obj_company


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


class CompanySubject(Domain):
    id = None
    data = None

    def __init__(self, session):
        self.session = session

    def set_domain(self):
        pass



