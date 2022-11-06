import time
import importlib

from pullgerInternalControl import pIC_pD
from pullgerFootPrint.com.linkedin import authorization as fp_authorization


def authorization(self, user_name: str, password: str):
    squirrel = self._squirrel

    if self._initialized is True:
        # if self._connected is not True:
        self.connect()

        if self._connected is True:
            time.sleep(2)

            importlib.reload(fp_authorization)

            fp_authorization.acceptance_of_questions(squirrel=squirrel)

            fp_authorization.goto_login_page(squirrel=squirrel)

            fp_authorization.set_user_name(squirrel=squirrel, user_name=user_name)
            time.sleep(1)

            fp_authorization.set_password(squirrel=squirrel, password=password)
            time.sleep(1)

            fp_authorization.sing_in(squirrel=squirrel)
            time.sleep(5)

            if self.squirrel.find_xpath(xpath="//div[@id='app__container']") is not None:
                mainSection = self.squirrel.find_xpath('.//main')
                raise pIC_pD.connect.System(
                    f'Authentication error: {mainSection.text}',
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
