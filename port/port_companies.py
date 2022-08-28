from .port import Domain as Root
import time

class CompanyDomain(Root):
    CompanyLoaded = None
    CompanyDATALoaded = None
    id = None
    nick = None
    routeID = None
    DATA = {
        'ID': None,
        'NAME': None,
        'DISCRIPTION': None,
        'CARD_TYPE': None,
        'LOCATION_NAME': None,
        'FOLLOWERS': None,
        'OVERVIEW': None,
        'WEBSITE': None,
        'INDUSTRY': None,
        'COMPANY_SIZE': None,
        'EMPLOYEE_LINKEDIN': None,
        'HEADQUARTERS': None,
        'FOUNDED': None,
        'SPECIALITIES': None,
        'LOCATIONS': None
    }

    def __init__(self, **kParams):
        if 'root' in kParams:
            self.squirrel = kParams['root'].squirrel
            self.authorizated = kParams['root'].authorizated
            self.RootLoaded = kParams['root'].RootLoaded
        else:
            super().__init__()

    def __dict__(self):
        res = {
            "test": self.test
        }
        return res

    def isPageCompanyOpen(self):
        isCorrect = True
        current_url = self.squirrel.current_url
        if type(current_url) == str:
            listUrl = list(filter(None, current_url.split('/')))
            if len(listUrl) > 3:
                if listUrl[2] != 'company':
                    isCorrect = False;
            else:
                isCorrect = False;

        return isCorrect

    def calculateCompanyRootURL(self, **kParams):
        resultURL = None
        routeID = None

        if 'id' in kParams:
            routeID = kParams['id']
        elif 'nick' in kParams:
            routeID = kParams['nick']
        elif 'url' in kParams:
            splitedURL = list(filter(None, kParams['url'].split('/')))
            if len(splitedURL) >= 4:
                routeID = splitedURL[3]
        else:
            if self.nick != None:
                routeID = self.nick
            elif self.id != None:
                routeID = self.id

        if routeID != None:
            resultURL = 'https://www.linkedin.com/company/' + str(routeID) + '/'

        return resultURL

    def _calculateRouteIDfromURL(self, inURL):
        result = {
            'id':None,
            'nick':None
        }

        urlSplited = list(filter(None, inURL.split('/')))
        if urlSplited[2] == 'company':
            try:
                result['id'] = int(urlSplited[3])
            except:
                result['nick'] = urlSplited[3]

        return result

    def _clearData(self):
        self.id = None
        self.nick = None
        self.CompanyLoaded = None

    def _pullBaseData(self):
        result = None
        pullDATA = {
            'id' : None,
            'nick' : None
        }

        current_url = self.squirrel.current_url
        if current_url != None:
            if self.isPageCompanyOpen():
                from pullgerFootPrint.com.linkedin.company import card
                pullDATA['nick'] = card.getNick(squirrel = self.squirrel)
                pullDATA['id'] = card.getID(squirrel = self.squirrel)

        if pullDATA['id'] != None:
            try:
                self.id = int(pullDATA['id'])
                result = True
            except:
                pass

        if pullDATA['nick'] != None:
            self.nick = pullDATA['nick']
            result = True

        return result

    #Acepted parameters:
    # 'id' or 'nick' or 'url'
    def setCompany(self, **kParams):
        result = None

        url = self.calculateCompanyRootURL(**kParams)

        if url != None:
            self._clearData();
            #++++ Reserv identification
            calculatedRouters = self._calculateRouteIDfromURL(url)
            if calculatedRouters['id'] != None:
                self.id = calculatedRouters['id']
            elif calculatedRouters['nick'] != None:
                self.nick = calculatedRouters['nick']
            #----
            if self.squirrel.get(url = url, timeout = 30, readyState = 'complete') == True:
            # if self.squirrel.get(url = url, timeout = 30, xpath = '//*[@data-entity-hovercard-id]') == True:
                if self.isPageCorrect():
                    self._pullBaseData()
                    result = True

        self.CompanyLoaded = result
        return result

    # def goToRoot(self):
    #
    #     url = self.getCompanyLinkedinURL(**kParams)
    #
    #     #self.squirrel.get(url)
    #
    #     if self.isPageCorrect() and self.isPageCompanyOpen():
    #         self.CompanyLoaded = True;
    #
    #     #id
    #
    #     return self.CompanyLoaded

    def goToAbout(self):
        result = None

        urlSplited = list(filter(None, self.squirrel.current_url.split('/')))

        if len(urlSplited) == 0 or urlSplited[-1] != 'about':
            if self.squirrel.current_url.find('linkedin.com') != -1 \
                and ('school' in urlSplited or 'company' in urlSplited):
                    # lang = self.squirrel.find_XPATH('//html').get_attribute("lang")
                    # if lang == 'ru':
                    #     keyWord = 'Общие сведения'
                    # elif lang == 'en':
                    #     keyWord = 'About'
                    # else:
                    #     keyWord = None
                    #     logging.error(
                    #         f'function: getListOfExperience Module: linkedIN Incorrect language: [{lang}] in url: [{self.squirrel.current_url}]')
                    #
                    # if keyWord != None:
                    #     AboutButton = self.squirrel.find_XPATH(f'//*[text()="{keyWord}"]')
                    #
                    # if AboutButton != None:
                    #     AboutButton.click()
                    #
                    #
                    self.squirrel.get(self.squirrel.current_url + 'about')
                    time.sleep(2)
                    self.squirrel.updateURL()
                    if self.squirrel.current_url.find('/about') != -1 :
                        result = True;

            if result == False:
                url = self.calculateCompanyRootURL()
                if url != None:
                    url += 'about/'
                    if self.squirrel.get(url = url, timeout = 30, xpath = '//*[@class="org-top-card-summary-info-list__info-item"]') == True:
                        if self.isPageCorrect():
                            result = True
        else:
            result = True

        return result

    def pullDATA(self):
        self.CompanyDATALoaded = None

        if self.CompanyLoaded != None:
            if self.goToAbout() == True:
                from pullgerFootPrint.com.linkedin.company import card
                aboutDATA = card.getAboutData(squirrel=self.squirrel)
                if aboutDATA != None:
                    for keyOfDATA in self.DATA.keys():
                        if keyOfDATA in aboutDATA:
                            self.DATA[keyOfDATA] = aboutDATA[keyOfDATA]
                    self.CompanyDATALoaded = True

        return self.CompanyDATALoaded