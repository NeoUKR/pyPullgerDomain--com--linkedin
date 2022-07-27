from squirrel import SquairrelCore
from pyPullgerFootPrint.com.linkedin import authorization as linkedinAuthorizationFootPrint
from pyPullgerFootPrint.com.linkedin.search import people as linkedinSearchPeopleFootPrint
from pyPullgerFootPrint.com.linkedin.people import card as linkedinPeopleCardFootPrint
from pyPullgerFootPrint.com.linkedin import general as linkedinGeneral
import time
import logging

class Domain:
    authorizated = None
    connected = None
    squirrel = None
    squirrel_initialized = None
    RootLoaded = None
    
    def __init__(self, initializationNeed = True):
        if initializationNeed == True:
            self.squirrel = SquairrelCore.Squirrel('selenium')
            self.squirrel_initialized = self.squirrel.initialize()

    def createPeopleSubject(self, **kwargs):
        newSubject = PeopleSubject(self)

        if 'id' in kwargs: newSubject.id = kwargs['id']
        if 'nick' in kwargs: newSubject.nick = kwargs['nick']

        return newSubject

    def connect(self):
        result = None

        if self.squirrel_initialized != None:
            result = self.squirrel.get('https://www.linkedin.com/')

        self.RootLoaded = result
        self.connected = True

        return result

    def authorization(self, inUserName, inPassword):
        if self.RootLoaded != True:
            self.connect()

        if self.RootLoaded == True:
            time.sleep(2)
            AuthorizationResult = linkedinAuthorizationFootPrint.setUserName(self.squirrel, inUserName);

            if AuthorizationResult == True:
                time.sleep(1)
                AuthorizationResult = linkedinAuthorizationFootPrint.setPassword(self.squirrel, inPassword);

                if AuthorizationResult == True:
                    time.sleep(1)
                    AuthorizationResult = linkedinAuthorizationFootPrint.singIn(self.squirrel);
                    #Check result of authorization
                    time.sleep(5)
                    restest = self.squirrel.find_XPATH('//div[@id="app__container"]')
                    if restest != None:
                        mainSection = restest.find_XPATH('.//main')
                        raise Exception(f'Authentification error: {mainSection.text}')


            # def check_authorizationResult(self)

            self.authorizated = AuthorizationResult

        return self.authorizated;

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

        self.squirrel.get(url)

        return True;

    def getCountOfResults(self):
        return linkedinSearchPeopleFootPrint.getCountOfResults(self.squirrel);

    def getListOfPeoples(self):
        return linkedinSearchPeopleFootPrint.getListOfPeoples(self.squirrel);

    def listOfPeopleNext(self):
        result = None;

        self.squirrel.send_PAGE_DOWN()
        time.sleep(1)
        self.squirrel.send_PAGE_DOWN()
        time.sleep(1)

        CurPagination = linkedinSearchPeopleFootPrint.getNumberCurentPaginationPage(self.squirrel)
        LastPagination = linkedinSearchPeopleFootPrint.getNumberLastPaginationPage(self.squirrel)
        if CurPagination != None and LastPagination != None:
            if CurPagination < LastPagination:
                result = linkedinSearchPeopleFootPrint.pushNextPaginationButton(self.squirrel)
            else:
                result = False;
        return result

    #     pass
        #linkedinSearchPeopleFootPrint
        #return linkedinSearchPeopleFootPrint.pushNextPaginationButton(self.squirrel);

    def getPerson(self, **kwargs):

        if 'in' in kwargs or 'nick' in kwargs:
            objPeople = self.createPeopleSubject(**kwargs)
            objPeople.getPage()

            return objPeople

    def close(self):
        self.squirrel.close();

class PeopleSubject(Domain):

    id = None
    nick = None

    def __init__(self, childrenClassObject):
        self.authorizated = childrenClassObject.authorizated
        self.connected = childrenClassObject.connected
        self.squirrel = childrenClassObject.squirrel
        self.squirrel_initialized = childrenClassObject.squirrel_initialized
        self.RootLoaded = childrenClassObject.RootLoaded

    def getPage(self):
        if self.authorizated == True:
            prefix = 'www'
            if self.nick != None:
                identificator = self.nick;
            else:
                identificator = self.id;
        else:
            prefix = 'be'
            identificator = self.nick;
        time.sleep(1)
        self.squirrel.get(f'https://{prefix}.linkedin.com/in/{identificator}')
        # ?trk=public_profile_experience-group-header
        checkCorrection = self.isPageCorrect()
        if checkCorrection != True:
            raise Exception(checkCorrection)
        time.sleep(1)

    def isPageCorrect(self):
        isNoError = True

        if self.authorizated == False:
            errorSection = self.squirrel.find_XPATH('//section[@class="profile"]')
        else:
            errorSection = self.squirrel.find_XPATH('//section[@class="artdeco-card ember-view pv-top-card"]')

        if errorSection == None:
            markerCkeckpoint = self.squirrel.current_url.find('checkpoint')
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

        # time.sleep(1)
        # self.squirrel.send_PAGE_DOWN()

        # lang = self.squirrel.find_XPATH('//html').get_attribute("lang")
        # if lang == 'ru':
        #     keyWord = 'Опыт работы'
        # elif lang == 'en':
        #     keyWord = 'Experience'
        # else:
        #     keyWord = None
        #     logging.error(f'function: getListOfExperience Module: linkedIN Incorrect language: [{lang}] in url: [{self.squirrel.current_url}]')
        #
        # if keyWord != None:
        #     CompareSections = self.squirrel.finds_XPATH('//section[@class="artdeco-card ember-view relative break-words pb3 mt2 "]')
        #     for testSection in CompareSections:
        #         testElement = testSection.find_XPATH(f'.//span[text()="{keyWord}"]')
        #         if testElement != None:
        #             moreButton = testSection.find_XPATH('.//div[@class="pvs-list__footer-wrapper"]')
        #             if moreButton != None:
        #                 time.sleep(1)
        #                 moreButton.click()
        #                 time.sleep(3)
        #                 break

        self.squirrel.get(f'{self.squirrel.current_url}details/experience/')

        time.sleep(2)
        self.squirrel.send_PAGE_DOWN()
        time.sleep(1)
        self.squirrel.send_PAGE_DOWN()
        time.sleep(1)
        self.squirrel.send_END()
        time.sleep(1)
        return linkedinPeopleCardFootPrint.getListOfExperience(self.squirrel);